from elasticsearch import Elasticsearch
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.postgres_url, pool_pre_ping=True)
Session = sessionmaker(engine, expire_on_commit=False)
mongo = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=4000)
products = mongo[settings.mongodb_database].products
es = Elasticsearch(settings.elasticsearch_url, request_timeout=5)
