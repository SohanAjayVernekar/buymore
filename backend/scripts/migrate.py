from app.db import engine, products
from app.models import Base
from app.sync import ensure_index

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    products.create_index("sku", unique=True)
    ensure_index()
    print("PostgreSQL schema, MongoDB SKU index, and Elasticsearch mapping ready.")
