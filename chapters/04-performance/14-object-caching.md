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

Both work. Redis is the modern standard.

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

WordPress needs a drop-in file at `wp-content/object-cache.php` to use external caching. Don't write this yourself—use a maintained solution:

| Plugin | Notes |
|--------|-------|
| **Redis Object Cache** | Most popular, good admin UI |
| **Object Cache Pro** | Commercial, best performance, supports Relay |
| **WP Redis** | Pantheon's plugin, solid alternative |

Install the plugin, then enable the drop-in through its settings.

### 3. Verify It's Working

Check that cache hits are happening:

**With Query Monitor:**
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

Key settings in `/etc/redis/redis.conf`:

```ini
# Memory limit
maxmemory 256mb

# Eviction policy when memory is full
# allkeys-lru: Remove least recently used keys (recommended)
maxmemory-policy allkeys-lru

# Persistence (optional - disable for pure cache)
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

- [Transients Deep Dive](./11-transients-strategies.md) - Application-level caching patterns
- [Database Optimization](./07-database-optimizations.md) - Reducing what needs caching
- [Scaling WordPress](./09-scaling-wordpress.md) - Object cache in multi-server setups
