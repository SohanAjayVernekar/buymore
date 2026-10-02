# Learning milestones

## 1. Split-brain: Elasticsearch unavailable for five minutes

PostgreSQL continues accepting committed orders. Search is stale or unavailable, and the dashboard reports an explicit error rather than pretending there are zero orders. RabbitMQ holds tasks and Celery retries ES indexing. After ES recovers, pending/retried tasks read current SQL state and rebuild their documents. External versioning prevents a late older task from overwriting a newer result. If publication failed or retries expired, replay all SQL orders with `python -m scripts.reindex_orders`.

This remains a dual-write consistency gap: a successful SQL commit and successful message publish are separate actions. There is no exactly-once checkout guarantee. Queue persistence helps after publication; it cannot recover a message that never reached RabbitMQ.

| Approach | Latency | Failure recovery | Complexity |
| --- | --- | --- | --- |
| Queued dual-write (implemented) | Usually next worker execution plus ES refresh | Durable tasks + retries; manual reconciliation for commit/publish gap | Moderate: broker, worker, versioning |
| Periodic polling (comparison only) | At least the polling interval | A durable checkpoint with overlap and versioned writes can catch up; a fixed recent-time window alone can lose older changes | Moderate: scheduler and checkpoint management |
| Transactional outbox / CDC (comparison only) | Near-real-time | SQL order and event commit together; relay retries unacknowledged events | Higher: event table or change stream, relay, deduplication |

Only Option A is implemented by user choice, despite the PDF's two-strategy deliverable.

## 2. Why not a large SQL JOIN plus LIKE?

A B-tree excels at equality and ordered ranges, but a leading-wildcard `LIKE '%term%'` generally cannot use the ordinary B-tree to locate a substring efficiently. Joining users, orders, and line items also multiplies work and requires deduplication. Elasticsearch builds inverted indexes from analyzed terms, supports multi-field relevance/prefix queries, and computes facets and revenue using the same filtered document set. PostgreSQL can provide dedicated text/trigram indexes, but that is not the assigned architecture. Money and fulfillment still belong in PostgreSQL.

The search endpoint uses multi_match with bool_prefix across customer name/email and item titles, bool filters, date/amount range filters, a status terms aggregation and a revenue sum. A final partial word such as `Wirel` matches `Wireless`; arbitrary substrings in the middle of a word are not promised. Items are mapped as an object array because the assignment searches titles without requiring correlated filters on multiple fields of the same item. A nested mapping would be needed for those correlated predicates.

## 3. Why MongoDB for the catalog?

A mouse may have DPI and battery type; a hub has a ports array; a lamp has color variants. An embedded document can carry sparse attributes and variant arrays without adding SQL columns or maintaining several join tables for each product shape. Every seeded product demonstrates both a nested attributes object and a variants array. A unique SKU index catches duplicates. Product updates touch only MongoDB.

## 4. Why snapshot title and price?

An order is a historical agreement about what was purchased and its price. Joining the current catalog during receipt rendering would silently change past orders when a product is renamed or repriced. Checkout copies current Mongo titles/prices into PostgreSQL order_items, calculates the total using Decimal, and indexes those same snapshots into ES. The intentional Wireless Mouse / Wireless Mouse Pro mismatch demonstrates this directly.

## 5. Write-path discipline

- Storefront reads MongoDB products and PostgreSQL users; the cart stays in browser state.
- Checkout reads active Mongo products, then writes orders and items to PostgreSQL in one transaction.
- Order search reads only Elasticsearch; it never joins SQL or Mongo as a fallback.
- Order details read PostgreSQL. Status changes commit there and then dispatch a Celery task. The optional badge reads ES only to compare versions.
- Catalog admin creates/edits MongoDB products and never changes existing order snapshots.
- The worker reads PostgreSQL and writes ES. MongoDB is not on this synchronization path.

Writing duplicate order records into MongoDB would introduce another competing source of truth and failure boundary without the SQL transaction protecting fulfillment/money. It would also tempt later joins to mutable product records. Keep each store responsible for the job assigned to it.
