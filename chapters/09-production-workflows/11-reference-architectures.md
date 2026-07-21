# Reference Architectures

Reference architectures turn principles into a starting point that a team can review, adapt and operate. They are not vendor prescriptions: the right design depends on traffic, data sensitivity, editor workflow, budget and the cost of downtime.

## 1. Small Editorial Site

```text
Visitor → CDN → managed WordPress host → PHP + MySQL
                    └→ object cache (optional)
```

Use this for a mostly public website with a small editorial team. Priorities are reliable backups, staging, image optimization, page caching and a minimal plugin set. A managed host can be the correct choice when the team does not need custom server control.

| Component | Minimum responsibility |
|-----------|------------------------|
| CDN | Static assets, DDoS protection and public-page caching |
| WordPress host | PHP, database, TLS, backups and monitoring |
| Repository | Theme/plugin code, configuration examples and release history |
| Staging | Plugin/theme and content-change validation |

Avoid adding Redis, multiple servers or a headless frontend until measurement shows a real constraint. Operational simplicity is a performance feature for a small site.

## 2. Growing WooCommerce Store

```text
Visitor → CDN/WAF → Nginx page cache → PHP-FPM → MySQL
                                  └→ Redis object cache
WooCommerce → Action Scheduler worker → payment / ERP / email services
```

This design separates public cacheable browsing from dynamic cart, checkout and account requests. The database, PHP worker pool and background queue need independent monitoring because a queue backlog can affect stock, emails and external synchronization long after the visitor's request ends.

Key decisions:

- cart, checkout and account pages bypass every shared page cache;
- payment and ERP webhooks are verified, idempotent and queued;
- HPOS compatibility and order-data migration are tested before activation;
- backups include a tested plan for orders created during recovery;
- cache rules are tested with anonymous, cart and logged-in sessions.

## 3. High-Traffic or Business-Critical Site

```text
                ┌→ application node A ─┐
Visitor → CDN → load balancer           ├→ managed/replicated database
                └→ application node B ─┘
                         └→ shared object cache and queue workers
```

Scale only after the single-server design has been measured and optimized. Multiple nodes require shared uploads or object storage, shared cache/queue infrastructure, central logs, consistent secrets and deployment coordination. WordPress code must not rely on local disk state or per-server cron behavior.

## Architecture Review Questions

- What happens if the database, cache, queue or one application node fails?
- Which components contain customer or payment-related data?
- What is the expected recovery time and who performs the recovery?
- Which components must scale for a campaign or sale?
- Can a new engineer understand the request path and deploy safely?

Choose the simplest architecture that meets these answers, then document its boundaries and failure modes.
