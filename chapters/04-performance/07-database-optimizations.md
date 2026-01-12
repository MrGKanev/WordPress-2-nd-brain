# Database Optimization

## Overview

The database is often the hidden bottleneck in WordPress performance. Every page load triggers multiple database queries—fetching posts, loading options, checking user sessions. When these queries slow down, everything slows down.

Understanding database performance requires understanding how WordPress uses its database. This isn't about memorizing SQL commands; it's about recognizing patterns that cause problems and knowing which tools address them.

## Why WordPress Databases Slow Down

### The Meta Table Problem

WordPress's flexibility comes from its meta tables. Instead of creating a new database column for every piece of data, WordPress stores key-value pairs in `wp_postmeta`, `wp_usermeta`, and `wp_commentmeta`. This means you can add any data to any post without altering the database structure.

The cost: meta tables grow enormous. A WooCommerce product might have 50+ meta entries—price, SKU, stock, weight, dimensions, sale dates, and more. Multiply by thousands of products, and `wp_postmeta` contains millions of rows.

The problem compounds because WordPress often needs to query these tables inefficiently. Finding all products under $50 requires scanning meta values, which can't use indexes effectively. What would be a simple indexed column lookup in a purpose-built table becomes a slow table scan in meta tables.

This architectural decision made WordPress flexible enough to power 40% of the web. It also makes database optimization essential for serious sites.

### The Options Table Bottleneck

WordPress loads all "autoloaded" options into memory on every page load. This happens before your theme or plugins even start—it's part of WordPress's core initialization.

On a fresh WordPress install, autoloaded options might total 100KB. After years of plugins being installed, configured, and removed, this can balloon to several megabytes. Every page load pays this cost, regardless of whether the options are needed.

Common culprits include:
- **Expired transients**: WordPress stores temporary cached data as options. When cleanup doesn't run properly, expired data accumulates.
- **Plugin residue**: Many plugins don't clean up when deactivated or deleted. Their options persist forever.
- **Serialized blobs**: Some plugins store large serialized arrays—entire configuration sets, cached remote data, logging information.

The fix isn't just deleting unnecessary options—it's setting appropriate options to not autoload when they're not needed on every page.

### Query Volume

A simple blog post page might execute 20-30 database queries. A WooCommerce product page can execute 100-200. A complex admin screen might run 300+.

| Page Type | Typical Query Count |
|-----------|---------------------|
| Simple blog post | 20-40 |
| Archive/category page | 40-80 |
| WooCommerce product | 100-200 |
| WooCommerce cart | 150-250 |
| Admin dashboard | 100-200 |

Each query takes time, even fast ones. Network latency between PHP and MySQL matters. Query parsing overhead matters. Lock contention on busy tables matters.

The difference between a 100ms page and a 500ms page often isn't one slow query—it's 200 queries that each take 2ms instead of 1ms.

## The wp_options Table

### Why It's Critical

The `wp_options` table stores WordPress settings, plugin configurations, active plugins list, current theme, and much more. Its unique characteristic: WordPress loads all autoloaded options at the start of every request.

This design made sense when WordPress was simple and options were few. Modern WordPress sites, loaded with plugins, can have thousands of options totaling megabytes of data. Loading all of this, parsing serialized PHP arrays, and keeping it in memory consumes time and RAM.

### Diagnosing Options Problems

The health of your options table directly impacts baseline performance. Key metrics to watch:

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Autoloaded size | Under 500KB | 500KB - 1MB | Over 2MB |
| Option count | Under 500 | 500 - 2000 | Over 5000 |
| Largest single option | Under 50KB | 50 - 200KB | Over 500KB |

Query Monitor plugin displays autoloaded data size. WP-CLI's `wp option list --autoload=yes` shows individual autoloaded options. Manual database queries reveal the raw numbers.

### Common Options Cleanup

**Transients**: WordPress's transient API stores temporary data with expiration times. When cron jobs don't run reliably (common on low-traffic sites or poor hosting), expired transients accumulate. They should be deleted, and the underlying cron problem fixed.

**Widget data**: Each widget instance stores its configuration. Widgets you installed once and removed leave data behind. Old theme widgets from themes you no longer use persist indefinitely.

**Plugin settings**: Plugins you've deactivated or deleted may have left their options behind. Settings pages, license keys, and configuration blobs remain until manually removed.

The goal isn't minimizing option count—some options are essential. The goal is ensuring only necessary data autoloads and accumulated cruft gets cleaned up.

## The wp_postmeta Table

### The Scaling Challenge

Every post, page, product, and custom post type stores its custom data in `wp_postmeta`. The table has a simple structure: `meta_id`, `post_id`, `meta_key`, `meta_value`.

This simplicity enables WordPress's flexibility. It also creates performance challenges:
- **No typing**: Every value is stored as text, even numbers. Numeric comparisons require type conversion.
- **No structure**: Related data (like a product's multiple pricing fields) spreads across separate rows with no inherent connection.
- **Limited indexing**: Default indexes don't optimize for the queries plugins actually run.

A site with 10,000 posts and 50 meta entries each has 500,000 rows in `wp_postmeta`. Query performance depends heavily on what you're querying and how.

### Orphaned Data

When posts are deleted, their meta usually gets deleted too. But not always. Plugin bugs, direct database deletions, and interrupted operations can leave orphaned meta—data pointing to posts that no longer exist.

Orphaned data wastes space and can slow queries that scan the table. Periodic cleanup removes this dead weight. The cleanup process identifies meta entries where the referenced `post_id` doesn't exist in `wp_posts` and removes them.

### The Query Problem

Meta queries are inherently expensive. Finding all products with price under $50 requires:
1. Scanning `wp_postmeta` for rows where `meta_key = '_price'`
2. Comparing `meta_value` (stored as text) to '50' (requiring type conversion)
3. Joining back to `wp_posts` to get the actual posts

This operation can't use indexes efficiently because the query needs to filter by `meta_key`, compare `meta_value`, and join to another table.

WooCommerce's lookup tables partially solve this by copying critical product data (price, stock status, sale status) into dedicated, properly indexed tables. The meta tables still exist for flexibility, but common queries use the optimized lookup tables.

## Database Indexing

### What Indexes Do

An index is like a book's index—it tells the database where to find specific data without reading every row. Without an index, finding a row requires scanning the entire table (slow). With an index, the database jumps directly to matching rows (fast).

Think of searching for a word in a dictionary. With alphabetical ordering (the index), you flip to approximately the right page immediately. Without ordering, you'd read every page until you found it.

WordPress creates basic indexes: primary keys, foreign key relationships. But these defaults don't optimize for every query pattern. Complex queries, especially those involving meta tables, often can't use available indexes effectively.

### When Indexes Help

Indexes accelerate queries that filter or sort by indexed columns. Common WordPress scenarios:
- Looking up posts by specific meta key/value combinations
- Finding users by email address
- Sorting orders by date
- Filtering products by stock status

Adding an index to columns that queries filter on dramatically reduces query time—often from seconds to milliseconds.

### When Indexes Hurt

Indexes aren't free. Each index:
- Consumes disk space (can be significant for large tables)
- Slows down INSERT, UPDATE, and DELETE operations (the index must be updated)
- Requires memory for efficient operation

Adding indexes to columns that aren't queried wastes resources. Adding indexes to tables with heavy write activity creates overhead. The right indexes balance read performance against write overhead.

### WordPress-Specific Indexing

WordPress's default indexes cover basic operations well. Performance problems arise with:
- **Meta queries**: Complex `meta_query` arguments in `WP_Query` generate JOINs that default indexes don't optimize.
- **Text searches**: LIKE queries with leading wildcards (`LIKE '%term%'`) can't use indexes at all.
- **Sorting by meta**: ORDER BY on meta values requires scanning all matching meta entries.

Tools like Query Monitor reveal which queries are slow. MySQL's EXPLAIN command shows whether queries use indexes. This data guides index decisions.

## MySQL Configuration

### Why Configuration Matters

MySQL has dozens of configuration options that affect performance. Default configurations optimize for minimal resource usage, not maximum performance. Servers with available RAM and CPU can significantly improve by adjusting these settings.

### Key Settings

**InnoDB Buffer Pool**: MySQL's most important performance setting. This memory area caches table data and indexes. Larger buffer pools mean more data stays in memory rather than reading from disk.

For dedicated database servers, the buffer pool should use 60-80% of available RAM. For servers running both web and database, balance against other memory needs.

**Query Cache** (MySQL 5.7 and earlier): The query cache stored complete query results. This helped read-heavy workloads but caused problems with frequent writes (cache invalidation overhead). MySQL 8.0 removed the query cache entirely.

**Temporary Tables**: Complex queries create temporary tables for sorting and grouping. If these exceed configured limits, MySQL writes to disk, dramatically slowing queries.

### Configuration Approach

Don't blindly apply configuration recommendations. Instead:
1. Establish performance baselines with current configuration
2. Identify specific bottlenecks (slow queries, disk I/O, memory pressure)
3. Adjust settings that address identified problems
4. Measure improvement
5. Iterate

Most WordPress sites benefit from increased buffer pool size if RAM is available. Beyond that, specific problems require specific solutions.

## Object Caching

### The Repeated Query Problem

Without object caching, WordPress queries the database for the same data repeatedly. Load a page showing recent posts? Query the database. Load another page showing the same posts? Query again. The database does identical work for every visitor.

WordPress has built-in object caching, but by default it only lasts for a single request. When the request ends, the cache disappears. The next request starts fresh, querying everything again.

### Persistent Object Cache

Persistent object caching stores query results in Redis or Memcached—fast in-memory stores that survive between requests. The first visitor's request queries the database and stores results in cache. Subsequent visitors get cached results without database queries.

The impact varies by page type:

| Scenario | Without Object Cache | With Object Cache |
|----------|----------------------|-------------------|
| Homepage (cached) | 40 queries | ~5 queries |
| Admin dashboard | 150 queries | ~40 queries |
| Logged-in user pages | Full queries | Dramatically reduced |
| WooCommerce cart | 200+ queries | ~50 queries |

The impact is most dramatic for:
- **Logged-in users**: Page caching can't help them, but object caching reduces their database queries significantly.
- **Admin pages**: The dashboard, post lists, and settings pages make heavy database use. Object caching accelerates all of them.
- **Repeated queries**: Any data requested multiple times benefits—sidebar widgets, navigation menus, frequently accessed options.

### Redis vs Memcached

Both serve as persistent object caches. Redis has become the WordPress standard because it supports data structures that map well to WordPress's cache patterns, can persist data across restarts, and offers additional features plugins can leverage.

Memcached remains viable, especially in environments where it's already deployed. Both dramatically outperform no object cache.

## Query Optimization Patterns

### The N+1 Problem

A common performance antipattern: query a list, then query additional data for each item in a loop.

Example: Display 10 posts with their featured images. The naive approach:
1. Query 10 posts (1 query)
2. For each post, query its featured image (10 queries)

Total: 11 queries. If you also need author info, add 10 more. Category? Another 10. This "N+1" pattern (1 initial query plus N additional queries) scales terribly.

The solution: batch loading. WordPress provides `update_post_meta_cache()` and similar functions that load all meta for multiple posts in a single query. Call these before your loop, and subsequent meta access comes from cache, not database.

### Limiting Results

Queries without limits potentially return thousands of rows. Even if you only display 10, the database fetches all of them. Memory fills, processing time increases, and PHP may hit limits.

Always specify limits. Use `posts_per_page` in WP_Query. When you don't need all results, don't fetch all results.

### Field Selection

Default WordPress queries fetch all columns. If you only need IDs, you're transferring unnecessary data. The `fields` parameter in WP_Query can return only IDs, reducing data transfer and memory usage.

This matters most for large result sets. Fetching 1,000 complete posts differs significantly from fetching 1,000 IDs.

### Avoiding LIKE Wildcards

Text searches using `LIKE '%term%'` (with leading wildcard) can't use indexes. Every row must be examined. On large tables, this takes seconds or longer.

When search performance matters, dedicated search solutions (Elasticsearch, Algolia, Meilisearch) provide indexed full-text search. They're dramatically faster than database LIKE queries and offer better relevance ranking too.

## Maintenance Routines

### Regular Cleanup

Databases accumulate cruft over time. Regular maintenance keeps them healthy:

**Transient cleanup**: Delete expired transients. If using object cache, transients shouldn't be in the database at all—check if something's creating them incorrectly.

**Revision control**: Post revisions accumulate indefinitely by default. For most sites, 5-10 revisions per post suffices. Limit via `WP_POST_REVISIONS` constant in wp-config.php and clean up existing excess.

**Orphan removal**: Periodically check for orphaned postmeta, commentmeta, and term relationships. Remove them.

**Table optimization**: InnoDB tables fragment over time, especially with frequent updates and deletes. Periodic OPTIMIZE TABLE reclaims space and can improve performance. Monthly is typically sufficient.

### Maintenance Schedule

| Task | Frequency | Method |
|------|-----------|--------|
| Delete expired transients | Weekly | WP-CLI or plugin |
| Check autoload size | Monthly | Query Monitor or WP-CLI |
| Orphan cleanup | Monthly | WP-Sweep plugin or SQL |
| Table optimization | Monthly | WP-CLI `wp db optimize` |
| Full database backup | Before any maintenance | WP-CLI or hosting tools |

### Tools for Maintenance

**WP-CLI**: Command-line database operations, transient deletion, search-replace. Essential for serious WordPress management.

**Plugins for Database Health:**

| Plugin | Purpose | Notes |
|--------|---------|-------|
| [Index WP MySQL For Speed](https://wordpress.org/plugins/index-wp-mysql-for-speed/) | Add missing indexes | Analyzes queries and suggests indexes (50K+ installs) |
| [Advanced Database Cleaner](https://wordpress.org/plugins/advanced-database-cleaner/) | Deep cleanup | Finds orphaned data, plugin leftovers (100K+ installs) |
| [WP-Sweep](https://wordpress.org/plugins/wp-sweep/) | Safe cleanup | Uses WordPress functions, not raw SQL |
| [AAA Option Optimizer](https://wordpress.org/plugins/aaa-option-optimizer/) | Autoload analysis | Identifies bloated autoloaded options |
| [Optimize Database after Deleting Revisions](https://wordpress.org/plugins/optimize-database-after-delete-revisions/) | Revision cleanup | Focused on revision management |

**Query Monitor**: Not for cleanup, but essential for identifying what needs optimization. Shows all queries, their timing, and their callers.

## When to Consider Custom Tables

### The Meta Tables Limit

WordPress's meta tables work well for moderate data volumes and simple queries. They struggle with:
- **Millions of rows**: Query performance degrades significantly
- **Complex filtering**: Multiple meta conditions require multiple JOINs
- **Numeric sorting**: Text-stored numbers sort incorrectly without conversion
- **Specific schemas**: Predictable data structures don't benefit from key-value flexibility

### Custom Tables Trade-offs

Custom tables offer proper column types, efficient indexes on actual columns, simpler and faster queries, and direct SQL for complex operations.

Custom tables cost development complexity, no automatic integration with WordPress APIs, migration and upgrade challenges, and backup complications.

### When Custom Tables Make Sense

Consider custom tables when:
- Data volume is large (hundreds of thousands of rows)
- Query patterns are well-defined and won't change
- Performance requirements exceed what meta tables provide
- Data structure is consistent (not arbitrary key-value pairs)

WooCommerce's High-Performance Order Storage (HPOS) demonstrates this—moving orders from posts/postmeta to custom tables dramatically improved admin performance for high-volume stores.

## Monitoring and Measurement

### Baseline First

Before optimizing, establish baselines:
- Page load times under normal conditions
- Query counts and total query time
- Specific slow query identification
- Database size and growth rate

Without baselines, you can't measure improvement. You might spend hours on optimizations that change nothing meaningful.

### What to Measure

| Metric | What It Indicates |
|--------|-------------------|
| Total query count | Overall database load |
| Total query time | Database's contribution to page load |
| Slowest queries | Primary optimization targets |
| Most frequent queries | Small improvements multiply |

### Acting on Data

Optimization should target measured problems:
1. Identify the slowest or most frequent queries
2. Understand why they're slow (missing index? poor query design? too much data?)
3. Apply appropriate fix
4. Measure improvement
5. Repeat with next problem

Random optimization—adding indexes everywhere, enabling every cache—wastes effort and may introduce new problems. Targeted optimization, guided by measurement, produces results.

## Further Reading

- [PHP Optimization](./02-php-optimization.md) - Server-side performance complements database optimization
- [Transients Strategies](./11-transients-strategies.md) - Caching database queries in application code
- [WP-CLI Essentials](../02-maintenance/03-wp-cli-essentials.md) - Command-line database management
- [Scaling WordPress](./09-scaling-wordpress.md) - Database architecture for high-traffic sites
- [WooCommerce Performance](../06-e-commerce/03-woocommerce-performance.md) - Store-specific database challenges
