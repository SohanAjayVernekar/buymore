import re
from decimal import Decimal
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import DuplicateKeyError
from sqlalchemy import select
from app.config import settings
from app.db import Session, products, es
from app.models import Order, OrderItem, User, utcnow
from app.schemas import OrderCreate, ProductWrite, SearchQuery, StatusUpdate
from app.search import build_search
from app.sync import dispatch, order_document, sync_state

app = FastAPI(title="BuyMore · Order Management & Search")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","),
                   allow_methods=["GET", "POST", "PUT", "PATCH"], allow_headers=["Content-Type"])


def product_out(doc):
    return {**doc, "_id": str(doc["_id"])}


def oid(value):
    if not ObjectId.is_valid(value):
        raise HTTPException(422, "Invalid product ID")
    return ObjectId(value)


@app.get("/api/users")
def users():
    with Session() as db:
        return [{"id": u.id, "name": u.name, "email": u.email} for u in db.scalars(select(User).order_by(User.id))]


@app.get("/api/products")
def list_products(category: str = "", query: str = "", include_inactive: bool = False, page: int = Query(1, ge=1), page_size: int = Query(6, ge=1, le=100), max_price: float | None = Query(None, ge=0)):
    criteria = {} if include_inactive else {"active": True}
    if category:
        criteria["category"] = category
    if query.strip():
        expr = {"$regex": re.escape(query.strip()), "$options": "i"}
        criteria["$or"] = [{"title": expr}, {"tags": expr}, {"sku": expr}]
    if max_price is not None:
        criteria["price"] = {"$lte": max_price}
    total = products.count_documents(criteria)
    items = [product_out(p) for p in products.find(criteria).sort("sku", 1).skip((page - 1) * page_size).limit(page_size)]
    return {"items": items, "total": total, "page": page, "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "catalog_counts": {"active": products.count_documents({"active": True}),
                               "inactive": products.count_documents({"active": False})}}


@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    doc = products.find_one({"_id": oid(product_id)})
    if not doc:
        raise HTTPException(404, "Product not found")
    return product_out(doc)


def product_data(payload):
    data = payload.model_dump()
    data["price"] = float(payload.price)
    data["updated_at"] = utcnow()
    return data


@app.post("/api/products", status_code=201)
def create_product(payload: ProductWrite):
    data = product_data(payload)
    try:
        products.insert_one(data)
    except DuplicateKeyError:
        raise HTTPException(409, "SKU already exists")
    return product_out(data)


@app.put("/api/products/{product_id}")
def update_product(product_id: str, payload: ProductWrite):
    data = product_data(payload)
    try:
        result = products.replace_one({"_id": oid(product_id)}, data)
    except DuplicateKeyError:
        raise HTTPException(409, "SKU already exists")
    if not result.matched_count:
        raise HTTPException(404, "Product not found")
    return {**data, "_id": product_id}


@app.post("/api/orders", status_code=201)
def place_order(payload: OrderCreate):
    quantities = {}
    for item in payload.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity
    if any(q > 100 for q in quantities.values()):
        raise HTTPException(422, "Maximum quantity is 100 per product")
    catalog = {str(p["_id"]): p for p in products.find({"_id": {"$in": [oid(i) for i in quantities]}, "active": True})}
    if len(catalog) != len(quantities):
        raise HTTPException(409, "A cart product is no longer available. Please update your cart.")
    with Session() as db:
        with db.begin():
            if not db.get(User, payload.user_id):
                raise HTTPException(422, "Choose a valid shopper")
            lines = [OrderItem(product_id=pid, title=catalog[pid]["title"], quantity=qty,
                               unit_price=Decimal(str(catalog[pid]["price"])).quantize(Decimal("0.01"))) for pid, qty in quantities.items()]
            order = Order(user_id=payload.user_id, status="PENDING", items=lines,
                          total_amount=sum((i.unit_price * i.quantity for i in lines), Decimal("0.00")))
            db.add(order)
            db.flush()
            document = order_document(order)
        # Dispatch is deliberately outside the committed PostgreSQL transaction.
        document["sync_status"] = dispatch(order.id)
        return document


@app.get("/api/orders/{order_id}")
def get_order(order_id: int):
    with Session() as db:
        order = db.get(Order, order_id)
        if not order:
            raise HTTPException(404, "Order not found")
        return {**order_document(order), "sync_status": sync_state(order)}


@app.patch("/api/orders/{order_id}/status")
def update_status(order_id: int, payload: StatusUpdate):
    with Session() as db:
        with db.begin():
            order = db.scalar(select(Order).where(Order.id == order_id).with_for_update(of=Order))
            if not order:
                raise HTTPException(404, "Order not found")
            order.status = payload.status
            order.updated_at = utcnow()
            order.version += 1
            document = order_document(order)
        return {**document, "sync_status": dispatch(order_id)}


@app.post("/api/search/orders")
def search_orders(payload: SearchQuery):
    try:
        result = es.search(index=settings.elasticsearch_index, body=build_search(payload))
    except Exception:
        raise HTTPException(503, "Order search is temporarily unavailable. Please try again shortly.")
    return {"orders": [h["_source"] for h in result["hits"]["hits"]],
            "total": result["hits"]["total"]["value"],
            "revenue": result["aggregations"]["revenue"]["value"],
            "by_status": {b["key"]: b["doc_count"] for b in result["aggregations"]["by_status"]["buckets"]}}
