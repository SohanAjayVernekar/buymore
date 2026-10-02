from sqlalchemy import select, text
from app.db import Session, engine, products
from app.models import Base, Order, OrderItem, User, utcnow
from scripts.fixtures import USERS, catalog_documents, order_fixtures
from scripts.reindex_orders import main as reindex


def main():
    Base.metadata.create_all(engine)
    products.create_index("sku", unique=True)
    now = utcnow()
    docs = catalog_documents(now)
    # Repeat runs preserve catalog edits and orders placed through the UI.
    for doc in docs:
        products.update_one({"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True)
    with Session.begin() as db:
        if db.scalar(select(Order.id).limit(1)) is None:
            for i, name in enumerate(USERS, 1):
                db.merge(User(id=i, name=name, email=name.lower().replace(" ", ".") + "@example.com"))
            db.flush()
            for fixture in order_fixtures(now):
                items = fixture.pop("items")
                db.add(Order(**fixture, items=[OrderItem(**item) for item in items]))
            db.flush()
            db.execute(text("SELECT setval(pg_get_serial_sequence('orders','id'), (SELECT max(id) FROM orders))"))
            db.execute(text("SELECT setval(pg_get_serial_sequence('users','id'), (SELECT max(id) FROM users))"))
    products.update_one({"_id": docs[0]["_id"], "title": "Wireless Mouse", "price": 50.16},
                        {"$set": {"title": "Wireless Mouse Pro", "price": 59.90, "updated_at": now}})
    reindex()
    print("Seed ready: 8 users, 24 active + 1 inactive products, 40 orders and historical snapshots.")


if __name__ == "__main__":
    main()
