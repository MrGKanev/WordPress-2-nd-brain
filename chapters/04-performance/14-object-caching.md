# Object Caching

## Overview

WordPress's built-in object cache only survives a single page request. Every new request rebuilds the cache from scratch—querying the database for options, user data, and transients all over again. Persistent object caching stores this data in memory (Redis or Memcached) so subsequent requests skip the database entirely.

For high-traffic sites, this is often the single biggest performance improvement after page caching.

## Why Object Caching Matters

Without persistent object cache, every request repeats expensive work:

```
Request 1: Load options from database → use → discard
Request 2: Load options from database → use → discard
Request 3: Load options from database → use → discard
```

With persistent object cache:

```
Request 1: Load options from database → store in Redis
Request 2: Get options from Redis (instant)
Request 3: Get options from Redis (instant)
```

The database is slow. Memory is fast. Object caching keeps frequently-accessed data in memory.

### What Gets Cached

WordPress automatically caches these through the object cache API:

| Data Type | Cache Group | Typical Size |
|-----------|-------------|--------------|
| Options (`get_option()`) | `options` | Hundreds of rows |
| Post data | `posts` | Per-post metadata |
| User data | `users`, `user_meta` | Session-critical |
| Transients | `transient` | API responses, computed data |
| Terms and taxonomies | `terms`, `term_meta` | Category/tag lookups |

Plugins that use `wp_cache_get()` and `wp_cache_set()` also benefit automatically.

## Redis vs Memcached

[Redis](https://redis.io/) and [Memcached](https://memcached.org/) are both in-memory data stores, but they evolved with different philosophies. Memcached was designed purely as a cache—simple, fast, and ephemeral. Redis started as a cache but grew into a data structure server with persistence, replication, and rich data types.

For WordPress object caching, both work. Redis has become the modern standard because its features align better with how WordPress uses caching, and its ecosystem (tooling, documentation, hosting support) is more mature.

| Factor | Redis | Memcached |
|--------|-------|-----------|
| **Data structures** | Strings, lists, sets, hashes | Strings only |
| **Persistence** | Optional disk persistence | Memory only |
| **Replication** | Built-in primary/replica | Requires external tools |
| **Memory efficiency** | Slightly higher overhead | More memory-efficient |
| **Ecosystem** | Better tooling, more active development | Stable but slower evolution |

**Recommendation:** Use Redis unless you have a specific reason not to. Its data structures match WordPress's caching patterns better, and persistence prevents cold cache after restarts.

## Implementation

### 1. Install Redis

Most managed WordPress hosts include Redis. For self-managed servers:

```bash
# Ubuntu/Debian
sudo apt install redis-server

# Verify it's running
redis-cli ping
# Should return: PONG
```

### 2. Install a Drop-in

WordPress's object cache is pluggable through a special mechanism called "drop-ins." Unlike regular plugins that live in the plugins directory, drop-ins are specific files that WordPress looks for in `wp-content/`. When WordPress finds `object-cache.php` there, it uses that file's implementation instead of the default non-persistent cache.

This drop-in file contains the code that actually talks to Redis or Memcached. It implements the same interface (`wp_cache_get()`, `wp_cache_set()`, etc.) but stores data in external memory instead of PHP's request-local memory.

Don't write this yourself—the implementation needs to handle edge cases, connection failures, and serialization correctly. Use a maintained solution:

| Plugin | Notes |
|--------|-------|
| [Redis Object Cache](https://wordpress.org/plugins/redis-cache/) | Most popular, good admin UI |
| [Object Cache Pro](https://objectcache.pro/) | Commercial, best performance, supports [Relay](https://relay.so/) |
| [WP Redis](https://wordpress.org/plugins/wp-redis/) | Pantheon's plugin, solid alternative |

Install the plugin, then enable the drop-in through its settings.

### 3. Verify It's Working

Check that cache hits are happening:

**With [Query Monitor](https://wordpress.org/plugins/query-monitor/):**
Look for the "Object Cache" panel. You should see cache hits increasing and a connected status.

**With Redis CLI:**
```bash
redis-cli monitor
# Make a request to your site
# You should see GET/SET commands flowing
```

**With wp-cli:**
```bash
wp cache get alloptions options
# Should return cached options data
```

## Measuring Cache Effectiveness

### Cache Hit Ratio

The percentage of requests served from cache vs. database:

```
Hit Ratio = Cache Hits / (Cache Hits + Cache Misses) × 100
```

| Hit Ratio | Assessment |
|-----------|------------|
| 90%+ | Excellent |
| 70-90% | Good |
| 50-70% | Review what's missing cache |
| <50% | Something's wrong |

Query Monitor shows this in the Object Cache panel. Low hit ratios often indicate:
- Cache being flushed too frequently
- Short TTLs on transients
- Plugins bypassing the cache

### Memory Usage

Monitor Redis memory to ensure you're not hitting limits:

```bash
redis-cli info memory
# Look for used_memory_human
```

If Redis runs out of memory, it evicts keys (usually oldest first). This causes cache misses and database load spikes.

**Sizing guidance:**
- Small sites: 64-128 MB
- Medium sites: 256-512 MB
- Large sites: 1 GB+
- WooCommerce: Add 50-100% more

## Configuration

### Redis Configuration

Redis runs as a separate service with its own configuration. The settings that matter most for WordPress caching are memory limits and eviction policies.

**Memory limit** caps how much RAM Redis can use. Without a limit, Redis grows until system memory is exhausted, potentially crashing your server. Set a reasonable limit based on your site's needs and available RAM.

**Eviction policy** determines what happens when Redis reaches its memory limit. The `allkeys-lru` policy removes the least recently used keys to make room for new ones—ideal for caching where old, unused data is expendable. Other policies exist for specialized use cases, but LRU (Least Recently Used) works well for WordPress.

**Persistence** controls whether Redis saves data to disk. For pure caching, persistence is unnecessary—if Redis restarts, WordPress simply regenerates cached data from the database. Disabling persistence (`save ""` and `appendonly no`) improves performance slightly and avoids disk I/O.

Key settings in `/etc/redis/redis.conf`:

```ini
# Memory limit - adjust based on available RAM
maxmemory 256mb

# Eviction policy when memory is full
# allkeys-lru removes least recently used keys (recommended for caching)
maxmemory-policy allkeys-lru

# Persistence - disable for pure cache use
save ""
appendonly no
```

### WordPress Configuration

In `wp-config.php`:

```php
// Redis connection (if not using defaults)
define('WP_REDIS_HOST', '127.0.0.1');
define('WP_REDIS_PORT', 6379);
define('WP_REDIS_DATABASE', 0);

// Optional: prefix for multisite or multiple WP installs sharing Redis
define('WP_REDIS_PREFIX', 'mysite:');

// Optional: disable object cache for debugging
// define('WP_REDIS_DISABLED', true);
```

## Multi-Server Environments

When running multiple application servers, all must connect to the same Redis instance:

```
WRONG: Each server has local Redis
┌─────────┐     ┌─────────┐
│ App 1   │     │ App 2   │
│ Redis 1 │     │ Redis 2 │
└─────────┘     └─────────┘
(Cache inconsistency)

RIGHT: Shared Redis
┌─────────┐     ┌─────────┐
│ App 1   │     │ App 2   │
└────┬────┘     └────┬────┘
     └───────┬───────┘
             │
      ┌──────┴──────┐
      │   Redis     │
      └─────────────┘
```

For high availability, use Redis Sentinel or Redis Cluster for automatic failover.

## Common Issues

### Cache Stampede

When cache expires, multiple requests simultaneously try to rebuild it, all hitting the database at once.

**Solutions:**
- Stagger expiration times with jitter
- Use cache locking (Object Cache Pro handles this)
- Pre-warm cache before expiration

### Stale Data

Data changes but cache serves old values.

**Causes:**
- Plugin not calling `wp_cache_delete()` on updates
- Long TTLs without invalidation hooks
- Multiple WordPress installs sharing cache without prefixes

**Debug:** Clear cache and verify fresh data appears. If it does, the issue is invalidation logic.

### Connection Failures

Redis connection drops cause site errors or slowdowns.

**Prevent with:**
```php
// Graceful fallback if Redis is down
define('WP_REDIS_GRACEFUL', true);
```

This falls back to WordPress's built-in non-persistent cache instead of throwing errors.

## Object Cache vs Page Cache

These serve different purposes and should be used together:

| Aspect | Object Cache | Page Cache |
|--------|--------------|------------|
| **What it caches** | Database query results, computed values | Entire rendered HTML pages |
| **When it helps** | Every request (even cache misses) | Only cache hits |
| **Logged-in users** | Works normally | Usually bypassed |
| **Dynamic pages** | Works normally | May need exclusions |

Page cache is faster (serves static HTML). Object cache helps when page cache can't be used—logged-in users, dynamic content, admin pages, AJAX requests.

## Further Reading

**Internal:**
- [Transients Deep Dive](./11-transients-strategies.md) - Application-level caching patterns
- [Database Optimization](./07-database-optimizations.md) - Reducing what needs caching
- [Scaling WordPress](./09-scaling-wordpress.md) - Object cache in multi-server setups

**External:**
- [Redis documentation](https://redis.io/docs/) - Official Redis documentation
- [WordPress Object Cache documentation](https://developer.wordpress.org/reference/classes/wp_object_cache/) - Official WordPress docs
- [DigitalOcean Redis tutorials](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-22-04) - Practical Redis setup guides
