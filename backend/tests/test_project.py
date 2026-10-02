import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select, delete
from app import main
from app.config import settings
from app.db import Session, engine, es, products
from app.models import Order, OrderItem
from app.schemas import SearchQuery
from app.search import build_search
from app.sync import dispatch, index_order
from scripts.fixtures import USERS, catalog_documents, order_fixtures

client = TestClient(main.app)


def test_seed_distribution():
    now = datetime.now(timezone.utc)
    catalog = catalog_documents(now)
    active = [p for p in catalog if p['active']]
    assert len(USERS) == 8 and len(active) == 24 and len(catalog) == 25
    assert min(Counter(p['category'] for p in active).values()) >= 5
    assert sum('wireless' in p['tags'] for p in active) >= 6
    assert sum(p['price'] < 25 for p in active) >= 4
    assert sum(25 <= p['price'] < 100 for p in active) >= 4
    assert sum(p['price'] >= 100 for p in active) >= 4
    orders = list(order_fixtures(now))
    assert len(orders) == 40
    assert sum(len(o['items']) for o in orders) >= 80
    assert min(Counter(o['status'] for o in orders).values()) >= 10
    assert min(Counter(o['user_id'] for o in orders).values()) >= 2
    assert sum(o['order_date'] < now-timedelta(days=60) for o in orders) >= 5
    assert sum(o['user_id'] in (7,8) and o['order_date'] < now-timedelta(days=60) for o in orders) >= 5
    assert all(o['status'] == 'PENDING' for o in orders if o['user_id'] == 6)
    assert all(o['status'] == 'SHIPPED' for o in orders if o['user_id'] == 7)
    assert sum(o['order_date'] >= now-timedelta(days=7) for o in orders) >= 5
    assert sum(o['total_amount'] < 30 for o in orders) >= 5
    assert sum(30 <= o['total_amount'] <= 150 for o in orders) >= 5
    assert sum(o['total_amount'] > 200 for o in orders) >= 5
    assert sum(any(i['title'] == 'Wireless Mouse' for i in o['items']) for o in orders) >= 8
    assert sum(any(i['title'] == 'Mechanical Keyboard' for i in o['items']) for o in orders) >= 3
    assert sum({'Wireless Mouse','Mechanical Keyboard'} <= {i['title'] for i in o['items']} for o in orders) >= 2
    assert sum(o['user_id'] == 3 and any('Wireless' in i['title'] for i in o['items']) for o in orders) >= 3
    assert all(o['total_amount'] == sum(i['quantity'] * i['unit_price'] for i in o['items']) for o in orders)


def test_live_seed_and_snapshot():
    assert len(client.get('/api/users').json()) == 8
    result = client.get('/api/products?page_size=100').json()
    catalog = result['items']
    assert result['total'] >= 24 and all(p['active'] for p in catalog)
    assert any(p['title'] == 'Wireless Mouse Pro' and p['price'] == 59.9 for p in catalog)
    historical = client.get('/api/orders/9').json()
    assert any(i['title'] == 'Wireless Mouse' and i['unit_price'] == 50.16 for i in historical['items'])
    with Session() as db:
        count = db.scalar(select(func.count()).select_from(Order))
    result = client.post('/api/search/orders', json={}).json()
    assert result['total'] == count >= 40


def test_search_facets_are_filtered_and_es_only():
    with patch.object(main, 'Session', side_effect=AssertionError('Search must not read PostgreSQL')), patch.object(main, 'products') as mongo_mock:
        all_orders = client.post('/api/search/orders', json={}).json()
        wireless = client.post('/api/search/orders', json={'query':'Wirel', 'page_size':20}).json()
        assert wireless['total'] > 0
        assert any(o['customer']['name'] == 'Wendy Wireless' for o in wireless['orders'])
        assert any(o['customer']['name'] != 'Wendy Wireless' for o in wireless['orders'])
        narrow = client.post('/api/search/orders', json={'statuses':['PENDING'], 'max_price':30, 'page_size':20}).json()
        assert 0 < narrow['total'] < all_orders['total']
        assert set(narrow['by_status']) == {'PENDING'}
        assert narrow['by_status']['PENDING'] == narrow['total']
        assert abs(narrow['revenue'] - sum(o['total_amount'] for o in narrow['orders'])) < .001
        recent = client.post('/api/search/orders', json={'date_from':(datetime.now(timezone.utc)-timedelta(days=7)).date().isoformat()}).json()
        assert 0 < recent['total'] < all_orders['total']
        mongo_mock.find.assert_not_called()


def test_search_unavailable_is_not_empty_success():
    with patch.object(main.es, 'search', side_effect=RuntimeError('offline')):
        assert client.post('/api/search/orders', json={}).status_code == 503


def test_catalog_is_mongo_only_and_edit_preserves_history():
    original = products.find_one({'_id':ObjectId(f'{1:024x}')})
    old_order = client.get('/api/orders/9').json()
    payload = {k:v for k,v in original.items() if k not in ('_id','updated_at')}
    payload.update(title='Temporary edited product', price=77.77)
    try:
        with patch.object(main, 'Session', side_effect=AssertionError('Catalog must not read PostgreSQL')), patch.object(main.es, 'search', side_effect=AssertionError('Catalog must not read ES')):
            assert client.get('/api/products').status_code == 200
            assert client.put(f'/api/products/{original["_id"]}', json=payload).status_code == 200
        after = client.get('/api/orders/9').json()
        assert after['items'] == old_order['items']
        doc = es.get(index=settings.elasticsearch_index, id='9')['_source']
        assert doc['items'] == old_order['items']
    finally:
        products.replace_one({'_id':original['_id']}, original)


@pytest.mark.parametrize('body', [
    {'user_id':1,'items':[]},
    {'user_id':1,'items':[{'product_id':f'{1:024x}','quantity':0}]},
    {'user_id':1,'items':[{'product_id':'bad','quantity':1}]},
    {'user_id':99999,'items':[{'product_id':f'{1:024x}','quantity':1}]},
    {'user_id':1,'items':[{'product_id':f'{25:024x}','quantity':1}]},
])
def test_invalid_checkout_rejected(body):
    assert client.post('/api/orders', json=body).status_code in (409,422)


def test_transaction_rolls_back_all_order_rows():
    with Session() as db:
        before = db.scalar(select(func.count()).select_from(Order))
    def fail_items(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith('INSERT INTO order_items'):
            raise RuntimeError('Simulated item insert failure')
    event.listen(engine, 'before_cursor_execute', fail_items)
    try:
        with TestClient(main.app, raise_server_exceptions=False) as c:
            response = c.post('/api/orders', json={'user_id':1,'items':[{'product_id':f'{1:024x}','quantity':1}]})
        assert response.status_code == 500
    finally:
        event.remove(engine, 'before_cursor_execute', fail_items)
    with Session() as db:
        assert db.scalar(select(func.count()).select_from(Order)) == before


def wait_for_sync(order_id):
    for _ in range(40):
        data = client.get(f'/api/orders/{order_id}').json()
        if data['sync_status'] == 'in_sync':
            return data
        time.sleep(.25)
    raise AssertionError('RabbitMQ/Celery did not synchronize the order')


def test_real_checkout_worker_status_and_duplicate_delivery():
    response = client.post('/api/orders', json={'user_id':1,'items':[{'product_id':f'{1:024x}','quantity':2},{'product_id':f'{2:024x}','quantity':1}]})
    assert response.status_code == 201, response.text
    order = response.json()
    order_id = order['order_id']
    try:
        assert order['sync_status'] == 'queued'
        assert order['total_amount'] == 220.14
        assert order['items'][0]['title'] == 'Wireless Mouse Pro'
        wait_for_sync(order_id)
        updated = client.patch(f'/api/orders/{order_id}/status', json={'status':'SHIPPED'})
        assert updated.status_code == 200, updated.text
        assert updated.json()['version'] == 2
        wait_for_sync(order_id)
        index_order(order_id)
        doc = es.get(index=settings.elasticsearch_index, id=str(order_id))['_source']
        assert doc['status'] == 'SHIPPED' and doc['version'] == 2
        assert client.patch(f'/api/orders/{order_id}/status', json={'status':'INVALID'}).status_code == 422
    finally:
        with Session.begin() as db:
            db.execute(delete(Order).where(Order.id == order_id))
        es.options(ignore_status=404).delete(index=settings.elasticsearch_index, id=str(order_id), refresh=True)


def test_queue_failure_keeps_committed_order():
    with patch('app.sync.sync_order.delay', side_effect=RuntimeError('Broker unavailable')):
        response = client.post('/api/orders', json={'user_id':1,'items':[{'product_id':f'{1:024x}','quantity':1}]})
    assert response.status_code == 201
    order_id = response.json()['order_id']
    try:
        assert response.json()['sync_status'] == 'queue_unavailable'
        assert client.get(f'/api/orders/{order_id}').status_code == 200
        index_order(order_id)
        assert client.get(f'/api/orders/{order_id}').json()['sync_status'] == 'in_sync'
    finally:
        with Session.begin() as db:
            db.execute(delete(Order).where(Order.id == order_id))
        es.options(ignore_status=404).delete(index=settings.elasticsearch_index, id=str(order_id), refresh=True)


def test_invalid_search_range_and_inclusive_date():
    assert client.post('/api/search/orders', json={'min_price':100, 'max_price':1}).status_code == 422
    assert client.post('/api/search/orders', json={'date_from':'2026-10-02','date_to':'2026-10-01'}).status_code == 422
    query = build_search(SearchQuery(date_to='2026-10-02'))
    assert query['query']['bool']['filter'][0]['range']['order_date']['lt'] == '2026-10-03'


@pytest.mark.parametrize('params', ['page=0', 'page=-1', 'page_size=0', 'page_size=-1', 'page_size=101', 'max_price=-1'])
def test_product_pagination_validation(params):
    assert client.get('/api/products?' + params).status_code == 422


def test_product_search_pagination_and_catalog_counts():
    first = client.get('/api/products?include_inactive=true&page_size=6').json()
    second = client.get('/api/products?include_inactive=true&page_size=6&page=2').json()
    assert len(first['items']) == len(second['items']) == 6
    assert {p['_id'] for p in first['items']}.isdisjoint(p['_id'] for p in second['items'])
    expected = {'active': products.count_documents({'active': True}), 'inactive': products.count_documents({'active': False})}
    assert first['catalog_counts'] == second['catalog_counts'] == expected
    for term in ['Earbuds', 'BM-001']:
        result = client.get('/api/products', params={'query':term}).json()
        assert result['total'] > 0
        assert all(term.lower() in (p['title'] + ' ' + p['sku'] + ' ' + ' '.join(p['tags'])).lower() for p in result['items'])
        assert result['catalog_counts'] == expected
    empty = client.get('/api/products?query=NoSuchProduct987654').json()
    assert empty['items'] == [] and empty['total'] == 0 and empty['total_pages'] == 0
