# Scaling WordPress

## Overview

Single-server optimization has limits. When traffic exceeds what one server can handle—or when uptime requirements demand redundancy—you need to scale horizontally. This guide covers architecture patterns for WordPress sites serving millions of pageviews.

## When to Scale

Single-server optimization should come first. Scale horizontally when:

- **Traffic exceeds server capacity** - Even optimized, one server can only handle so much
- **Uptime requirements exceed 99.9%** - Single points of failure prevent true high availability
- **Geographic distribution matters** - Users worldwide need consistent performance
- **Traffic is unpredictable** - Viral content or seasonal spikes need elastic capacity

Don't scale prematurely. A well-optimized single server with proper caching handles more traffic than most sites will ever see. Scale when you have data showing you need it.

## Elastic Architecture

The fundamental principle: **horizontal scalability beats vertical scalability**.

Vertical scaling (bigger server) has hard limits and single points of failure. Horizontal scaling (more servers) can expand indefinitely and provides redundancy.

```
Single Server (Vertical)          Multi-Server (Horizontal)
┌─────────────────────┐           ┌─────────────────────┐
│                     │           │   Load Balancer     │
│   Everything on     │           └──────────┬──────────┘
│   one machine       │                      │
│                     │           ┌──────────┼──────────┐
│   - Web Server      │           │          │          │
│   - PHP             │           ▼          ▼          ▼
│   - Database        │        ┌─────┐   ┌─────┐   ┌─────┐
│   - Cache           │        │ App │   │ App │   │ App │
│   - Files           │        │  1  │   │  2  │   │  3  │
│                     │        └──┬──┘   └──┬──┘   └──┬──┘
└─────────────────────┘           │         │         │
                                  └────┬────┴────┬────┘
                                       │         │
                                  ┌────┴───┐ ┌───┴────┐
                                  │ Shared │ │ Shared │
                                  │   DB   │ │ Files  │
                                  └────────┘ └────────┘
```

### Components of Elastic Architecture

| Component | Purpose | Options |
|-----------|---------|---------|
| **Load Balancer** | Distributes traffic across app servers | Nginx, HAProxy, AWS ALB, Cloudflare |
| **Application Servers** | Run PHP/WordPress | Identical, stateless instances |
| **Shared Database** | Central data storage | MySQL with replication |
| **Shared Filesystem** | Media uploads accessible to all nodes | NFS, GlusterFS, AWS EFS, S3 |
| **Shared Cache** | Object cache accessible to all nodes | Redis, Memcached |

### Key Principle: Stateless Application Servers

For horizontal scaling to work, any request must be handleable by any server. This means:

- **No local sessions** - Use database or Redis for sessions
- **No local file uploads** - Use shared storage or object storage (S3)
- **No local cache** - Use Redis/Memcached accessible to all nodes
- **Identical configuration** - All servers must have the same code, plugins, themes

## Page Caching at Scale

At scale, page caching moves from WordPress plugins to reverse proxies.

### Why Reverse Proxy Caching?

A reverse proxy like Varnish can serve cached pages **1000x faster** than PHP:

| Approach | How It Works | Performance |
|----------|--------------|-------------|
| **Plugin caching** (WP Super Cache, etc.) | PHP loads, checks cache, serves file | ~100-500 req/sec |
| **Reverse proxy** (Varnish, Nginx) | Request never reaches PHP | ~10,000+ req/sec |

The difference: plugin caching still loads PHP for every request. Reverse proxy caching intercepts the request before PHP ever starts.

### Reverse Proxy Options

**Varnish** - Purpose-built HTTP accelerator
- Extremely fast for cached content
- Powerful cache invalidation (VCL language)
- Requires separate service to manage

**Nginx as Reverse Proxy** - Web server with caching
- Already running as web server for most
- FastCGI cache is simple to configure
- Less flexible cache invalidation

**CDN Edge Caching** - Cloudflare, Fastly, AWS CloudFront
- Geographically distributed
- Handles DDoS protection too
- May add complexity for cache purging

### Cache Invalidation

The hard problem with caching: knowing when to clear it.

```
User publishes post → Cache must clear
                      ├── Homepage (has post list)
                      ├── Category pages (post appears)
                      ├── Tag pages (post appears)
                      ├── Author page (post appears)
                      ├── RSS feeds (post appears)
                      └── Related posts on other pages
```

Solutions:
- **TTL-based** - Cache expires after X minutes (simple but stale content possible)
- **Purge on publish** - WordPress hooks trigger cache clear (more complex)
- **Surrogate keys** - Tag cached items, purge by tag (most flexible, requires Varnish/Fastly)

## Object Caching at Scale

WordPress's built-in object cache only lasts for a single request. Persistent object caching with Redis or Memcached stores data across requests.

### Why Object Caching Matters at Scale

Without persistent object cache:
```
Request 1: Query database for options → Store in memory → Request ends → Memory cleared
Request 2: Query database for options → Store in memory → Request ends → Memory cleared
Request 3: Query database for options → Store in memory → Request ends → Memory cleared
```

With persistent object cache:
```
Request 1: Query database for options → Store in Redis
Request 2: Get options from Redis (no database)
Request 3: Get options from Redis (no database)
```

### Redis vs Memcached

| Factor | Redis | Memcached |
|--------|-------|-----------|
| **Data structures** | Strings, lists, sets, hashes | Strings only |
| **Persistence** | Can persist to disk | Memory only |
| **Replication** | Built-in | External tools |
| **Memory efficiency** | Less efficient | More efficient |
| **Recommendation** | Preferred for WordPress | Legacy choice |

**Redis is the modern standard.** Its data structures match WordPress's cache patterns better, and persistence prevents cache loss on restart.

### Multi-Server Object Cache

Critical: all application servers must share the same cache instance.

```
WRONG: Each server has local Redis
┌─────────┐     ┌─────────┐     ┌─────────┐
│ App 1   │     │ App 2   │     │ App 3   │
│ Redis 1 │     │ Redis 2 │     │ Redis 3 │
└─────────┘     └─────────┘     └─────────┘
(Cache incoherence - servers have different data)

RIGHT: Shared Redis instance
┌─────────┐     ┌─────────┐     ┌─────────┐
│ App 1   │     │ App 2   │     │ App 3   │
└────┬────┘     └────┬────┘     └────┬────┘
     │               │               │
     └───────────────┼───────────────┘
                     │
              ┌──────┴──────┐
              │   Redis     │
              │  (shared)   │
              └─────────────┘
```

## Database Scaling

The database is typically the final bottleneck. When caching isn't enough:

### Read Replicas

Most WordPress database load is reads (SELECT). Write operations (INSERT, UPDATE, DELETE) are relatively rare. Database replication sends writes to a primary server and distributes reads across replicas.

```
                    ┌─────────────────┐
                    │  WordPress      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
         ┌────────┐    ┌────────┐    ┌────────┐
         │ Primary│───▶│Replica │───▶│Replica │
         │ (write)│    │ (read) │    │ (read) │
         └────────┘    └────────┘    └────────┘
```

**HyperDB** - WordPress drop-in for database replication
- Routes read queries to replicas
- Routes write queries to primary
- Handles failover if replica is down
- Still maintained, works with modern WordPress

### Identifying Problem Queries

Before scaling the database, find and fix bad queries:

**Enable slow query log:**
```ini
# my.cnf
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 1
```

**Common culprits:**
- `meta_query` with multiple conditions
- `tax_query` across many terms
- Searches across post content
- Sorting by meta values
- Queries without proper indexes

**Tools:**
- Query Monitor plugin (development)
- New Relic APM (production monitoring)
- MySQL EXPLAIN for query analysis

### When to Add Read Replicas

Consider database replication when:
- Slow query log shows consistent load
- Object caching is already implemented
- Database CPU is consistently high
- You've optimized obvious bad queries

## Search at Scale

WordPress's default search is a `LIKE %term%` query—one of the slowest possible database operations.

### Why WordPress Search Doesn't Scale

```sql
-- What WordPress search does
SELECT * FROM wp_posts
WHERE post_content LIKE '%search term%'
   OR post_title LIKE '%search term%'
```

This query:
- Cannot use indexes (leading wildcard)
- Scans every row in the table
- Gets slower as content grows
- Provides poor relevance ranking

### Dedicated Search Index

A search index inverts the problem:

```
Database approach:          Search index approach:
"Find posts containing      "Which posts contain
 'wordpress'"               'wordpress'?"
      │                           │
      ▼                           ▼
Scan all posts              Lookup in index
(slow, O(n))               (fast, O(1))
```

### Search Solutions

| Solution | Type | Best For |
|----------|------|----------|
| **ElasticSearch** | Self-hosted | Full control, complex queries |
| **Algolia** | SaaS | Fast implementation, excellent UX |
| **AWS CloudSearch** | Managed | AWS infrastructure |
| **Meilisearch** | Self-hosted | Simpler alternative to Elastic |

**ElasticSearch** remains the standard for large WordPress sites. Plugins like ElasticPress or SearchWP integrate WordPress with ElasticSearch.

### Beyond Search

Once you have a search index, use it for more than search:

- **Faceted navigation** - Filter by category, tag, custom fields
- **Related posts** - Find similar content efficiently
- **Autocomplete** - Fast suggestions as users type
- **Complex queries** - Multi-field queries that would kill MySQL

## Development Workflow at Scale

Enterprise WordPress requires disciplined workflows.

### Version Control Requirements

At scale, version control is non-negotiable:

- **All custom code in Git** - Themes, plugins, mu-plugins
- **No production edits** - Code flows from Git, never from admin
- **Configuration as code** - Use WP-CFM or similar for wp_options

### Deployment Pipeline

```
Developer → Pull Request → Code Review → CI Tests → Staging → Production
                │              │            │           │
                │              │            │           └── Manual or automated
                │              │            └── Automated tests pass
                │              └── Peer approval required
                └── Branch-based development
```

**CI/CD Tools:**
- GitHub Actions (most common)
- GitLab CI
- CircleCI

### Environment Parity

Development, staging, and production should be as similar as possible:

| Aspect | Development | Staging | Production |
|--------|-------------|---------|------------|
| PHP version | Same | Same | Same |
| WordPress version | Same | Same | Same |
| Object cache | Redis | Redis | Redis |
| Database | MySQL | MySQL (copy) | MySQL |
| Plugins | Same | Same | Same |

**Local development tools:**
- DDEV (recommended - Docker-based, WordPress-aware)
- Local by Flywheel (GUI-based)
- Lando (flexible, Docker-based)

## Full Stack Architecture

A complete high-availability WordPress architecture:

```
                         Internet
                            │
                    ┌───────┴───────┐
                    │     CDN       │  ← Static assets, edge caching
                    │  (Cloudflare) │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │ Load Balancer │  ← SSL termination, routing
                    │  (Nginx/ALB)  │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐
        │  Varnish  │ │  Varnish  │ │  Varnish  │  ← Page cache
        └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
              │             │             │
        ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐
        │ PHP/Nginx │ │ PHP/Nginx │ │ PHP/Nginx │  ← Application
        └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
              │             │             │
              └─────────────┼─────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
  ┌─────┴─────┐      ┌──────┴──────┐     ┌──────┴──────┐
  │   Redis   │      │   MySQL     │     │    S3 /     │
  │  (cache)  │      │  Primary +  │     │    EFS      │
  │           │      │  Replicas   │     │   (files)   │
  └───────────┘      └─────────────┘     └─────────────┘

  Optional:
  ┌─────────────┐
  │ElasticSearch│  ← Search index
  └─────────────┘
```

## Managed Hosting vs. Self-Managed

At scale, you have two paths:

### Managed WordPress Hosting

Providers like WP Engine, Kinsta, or Pantheon handle:
- Server infrastructure
- Scaling and redundancy
- Security patches
- Backups
- CDN integration

**Pros:** Less operational overhead, proven architecture
**Cons:** Less flexibility, higher cost at very high scale

### Self-Managed Infrastructure

You build and maintain the stack using:
- Cloud providers (AWS, GCP, DigitalOcean)
- Configuration management (Ansible, Terraform)
- Container orchestration (Kubernetes, Docker Swarm)

**Pros:** Full control, potentially lower cost at scale
**Cons:** Requires DevOps expertise, operational burden

### Evaluation Questions

When choosing a provider or building infrastructure:

- How does it handle traffic spikes?
- What's the page caching strategy?
- Is object caching (Redis) included?
- How are media files stored and served?
- What's the database redundancy model?
- How do deployments work?
- What monitoring is included?

## Further Reading

- [Database Optimization](./07-database-optimizations.md) - Query-level optimizations
- [PHP-FPM Optimization](./03-php-fpm-optimization.md) - Process management tuning
- [Hosting Selection](../06-maintenance/02-hosting-selection.md) - Choosing the right host
- [Cloudflare Hardening](../05-security/01-cloudflare-hardening.md) - CDN and edge caching
