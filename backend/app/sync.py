import logging
from celery import Celery
from elasticsearch import ConflictError, NotFoundError
from app.config import settings
from app.db import Session, es
from app.models import Order
from app.search import MAPPING

logger = logging.getLogger(__name__)
celery = Celery("buymore", broker=settings.rabbitmq_url)
celery.conf.update(task_default_queue="order_sync", task_serializer="json", accept_content=["json"],
                   task_default_delivery_mode="persistent", task_acks_late=True,
                   task_reject_on_worker_lost=True, worker_prefetch_multiplier=1,
                   broker_connection_retry_on_startup=True, broker_connection_timeout=3,
                   broker_transport_options={"confirm_publish": True},
                   task_publish_retry_policy={"max_retries": 2, "interval_start": 0, "interval_step": 1, "interval_max": 1})


def order_document(order):
    return {"order_id": order.id, "order_date": order.order_date.isoformat(),
            "updated_at": order.updated_at.isoformat(), "version": order.version,
            "status": order.status, "total_amount": float(order.total_amount),
            "customer": {"id": order.user.id, "name": order.user.name, "email": order.user.email},
            "items": [{"product_id": i.product_id, "title": i.title, "quantity": i.quantity,
                       "unit_price": float(i.unit_price)} for i in order.items]}


def ensure_index():
    if not es.indices.exists(index=settings.elasticsearch_index):
        es.indices.create(index=settings.elasticsearch_index, mappings=MAPPING)


def index_order(order_id):
    with Session() as db:
        order = db.get(Order, order_id)
        if not order:
            return
        document = order_document(order)
    try:
        es.index(index=settings.elasticsearch_index, id=str(order_id), document=document,
                 version=document["version"], version_type="external", refresh="wait_for")
    except ConflictError:
        # A duplicate task or a newer committed version already won the race.
        pass


@celery.task(autoretry_for=(Exception,), retry_backoff=2, retry_backoff_max=60,
             retry_jitter=False, max_retries=20)
def sync_order(order_id):
    index_order(order_id)


def dispatch(order_id):
    try:
        sync_order.delay(order_id)
        return "queued"
    except Exception:
        logger.exception("Order %s committed but could not be queued; run reindex_orders", order_id)
        return "queue_unavailable"


def sync_state(order):
    try:
        doc = es.get(index=settings.elasticsearch_index, id=str(order.id))["_source"]
        return "in_sync" if doc.get("version") == order.version else "pending"
    except NotFoundError:
        return "pending"
    except Exception:
        return "unavailable"
