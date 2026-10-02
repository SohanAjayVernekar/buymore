from sqlalchemy import select
from app.db import Session, es
from app.models import Order
from app.config import settings
from app.sync import ensure_index, index_order

def main():
    ensure_index()
    with Session() as db:
        ids = list(db.scalars(select(Order.id)))
    for order_id in ids:
        index_order(order_id)
    es.indices.refresh(index=settings.elasticsearch_index)
    print(f"Reconciled {len(ids)} orders from PostgreSQL into Elasticsearch.")

if __name__ == "__main__":
    main()
