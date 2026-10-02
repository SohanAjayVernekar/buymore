from datetime import timedelta
from app.schemas import SearchQuery

TEXT = {"type": "text", "fields": {"raw": {"type": "keyword"}}, "analyzer": "standard"}
MAPPING = {"properties": {
    "order_id": {"type": "integer"}, "version": {"type": "integer"},
    "order_date": {"type": "date"}, "updated_at": {"type": "date"},
    "status": {"type": "keyword"}, "total_amount": {"type": "scaled_float", "scaling_factor": 100},
    "customer": {"properties": {"id": {"type": "integer"}, "name": TEXT, "email": TEXT}},
    "items": {"properties": {"product_id": {"type": "keyword"}, "title": TEXT,
                               "quantity": {"type": "integer"}, "unit_price": {"type": "scaled_float", "scaling_factor": 100}}},
}}


def build_search(q: SearchQuery):
    filters = []
    if q.statuses:
        filters.append({"terms": {"status": q.statuses}})
    dates = {}
    if q.date_from:
        dates["gte"] = q.date_from.isoformat()
    if q.date_to:
        dates["lt"] = (q.date_to + timedelta(days=1)).isoformat()
    if dates:
        filters.append({"range": {"order_date": dates}})
    prices = {}
    if q.min_price is not None:
        prices["gte"] = q.min_price
    if q.max_price is not None:
        prices["lte"] = q.max_price
    if prices:
        filters.append({"range": {"total_amount": prices}})
    must = [{"multi_match": {"query": q.query.strip(), "fields": ["customer.name^2", "customer.email", "items.title"], "type": "bool_prefix"}}] if q.query.strip() else [{"match_all": {}}]
    return {"query": {"bool": {"must": must, "filter": filters}}, "track_total_hits": True,
            "from": (q.page - 1) * q.page_size, "size": q.page_size,
            "sort": [{"order_date": "desc"}, {"order_id": "desc"}],
            "aggs": {"revenue": {"sum": {"field": "total_amount"}}, "by_status": {"terms": {"field": "status", "size": 3}}}}
