# Database Operations

## Overview

WordPress provides multiple ways to store data, each suited for different purposes. Choosing the wrong storage method is a common mistake that leads to performance issues and maintenance headaches.

> **Key principle**: Use WordPress APIs whenever possible. They handle caching, multisite compatibility, and security automatically. Custom database queries should be a last resort, not a first choice.

## Storage Methods Comparison

| Method | Best For | Not For |
|--------|----------|---------|
| **Options API** | Plugin settings, configuration | Large datasets, per-post data |
| **Post Meta** | Data attached to specific posts | Settings, user preferences |
| **User Meta** | Data attached to specific users | Global settings, post data |
| **Transients** | Cached data with expiration | Permanent data storage |
| **Custom Tables** | Large datasets, complex queries | Simple key-value data |
| **Object Cache** | Temporary, frequently accessed data | Persistent storage |

## The Options API

The Options API stores key-value pairs in the `wp_options` table. It's the simplest storage method but often misused.

### When to Use Options

- Plugin settings and configuration
- Site-wide preferences
- Data that applies globally
- Small amounts of data (under 1MB recommended)

### When NOT to Use Options

- Data that grows over time (logs, history)
- Data tied to specific posts or users
- Large serialized arrays
- Frequently updated data (autoload issues)

### The Autoload Problem

Every option has an "autoload" flag. When set to "yes", WordPress loads that option on every page request. This is efficient for data you need everywhere, but devastating for large data you rarely use.

**The trap**: `add_option()` defaults autoload to "yes". If your plugin stores large arrays of data with autoload enabled, you'll slow down every page on the site.

**Solution**: Explicitly set autoload to "no" for large or rarely-used data:

```php
add_option('my_large_data', $data, '', 'no');
```

## Post Meta

Post meta attaches data to specific posts. WordPress stores this in the `wp_postmeta` table.

### Understanding the Structure

Each meta entry is a separate row:
- `post_id`: Which post this belongs to
- `meta_key`: The name of the data
- `meta_value`: The actual data (can be serialized)

This structure is flexible but has performance implications. Querying by meta values (like "find all posts where price > 100") is slow because meta values are stored as strings and not indexed by default.

### Single vs. Multiple Values

WordPress allows multiple meta entries with the same key. This is useful for things like multiple authors or tags, but confusing if you expect single values.

- `get_post_meta($id, 'key', true)` - Returns single value (or first if multiple exist)
- `get_post_meta($id, 'key', false)` - Returns array of all values

Always pass the third parameter explicitly to be clear about your intent.

### The $wpdb Performance Consideration

For meta queries, WordPress loads all meta for a post at once and caches it. This is efficient when you need multiple meta values, but wasteful if you only need one value from posts with hundreds of meta entries.

## User Meta

Identical to post meta, but for users. Same API, same performance characteristics, same gotchas.

Common uses:
- User preferences
- Extended profile data
- Plugin-specific user settings
- Last login dates, activity tracking

## Transients

Transients are cached data with an expiration time. They're stored in the database by default, but move to object cache (Redis, Memcached) if available.

### When to Use Transients

- API responses you don't want to fetch on every request
- Complex calculations that don't change often
- Aggregated data (counts, statistics)
- Anything expensive to generate

### Transient Gotchas

**They might not expire exactly on time.** WordPress only checks expiration when you request the transient. An expired transient sitting unused will stay in the database until something triggers cleanup.

**They're not guaranteed storage.** With object caching, transients can be evicted at any time when memory is needed. Never store data in transients that you can't regenerate.

**They can bloat the database.** Without object caching, expired transients accumulate. Plugins exist to clean them up, but it's better to avoid creating thousands of transients in the first place.

## Custom Database Tables

Sometimes WordPress's built-in tables aren't enough. Custom tables make sense when:

### Reasons to Create Custom Tables

1. **Volume** - Millions of records that would overwhelm post meta
2. **Query patterns** - Need to query by columns that don't map to WordPress structures
3. **Relationships** - Complex data relationships between entities
4. **Performance** - Need specific indexes for your query patterns
5. **Data integrity** - Need foreign keys or constraints

### Reasons NOT to Create Custom Tables

1. **Ecosystem compatibility** - Other plugins can't access your data easily
2. **Import/Export** - Standard tools won't include your tables
3. **Maintenance burden** - You handle schema updates, backups, optimization
4. **Multisite complexity** - Need to manage per-site tables yourself

### Schema Management

The biggest challenge with custom tables is managing schema changes across versions. WordPress provides `dbDelta()` for this - it compares your desired schema with the existing table and makes necessary changes.

**Caution**: `dbDelta()` is picky about SQL formatting. Spacing and keywords must be exact or it won't work correctly.

## The $wpdb Object

All database operations go through the global `$wpdb` object. It provides:

- Prepared statements for security
- Table name prefixes for multisite
- Debug logging
- Error handling

### Security: Always Use Prepared Statements

Never concatenate user input into SQL queries. This is the number one way plugins get hacked.

```php
// DANGEROUS - SQL Injection vulnerability
$wpdb->query("SELECT * FROM table WHERE id = " . $_GET['id']);

// SAFE - Prepared statement
$wpdb->prepare("SELECT * FROM table WHERE id = %d", $_GET['id']);
```

The placeholders:
- `%d` - Integer
- `%f` - Float
- `%s` - String (escaped)

### Table Prefixes

Never hardcode `wp_` as the table prefix. Many sites use custom prefixes for security.

```php
// Wrong
$wpdb->query("SELECT * FROM wp_posts");

// Right
$wpdb->query("SELECT * FROM {$wpdb->posts}");
$wpdb->query("SELECT * FROM {$wpdb->prefix}custom_table");
```

## Caching Strategies

WordPress has multiple caching layers. Understanding them prevents redundant database queries.

### Object Cache

WordPress caches database queries in memory during a request. If you call `get_post_meta($id, 'key')` twice, the database is only hit once.

With persistent object caching (Redis/Memcached), this cache survives across requests.

### Query Caching

When you use `WP_Query`, results are cached. Identical queries in the same request share results.

### When to Bypass Cache

Sometimes you need fresh data:

```php
// Force fresh data
wp_cache_delete($post_id, 'post_meta');
$fresh_meta = get_post_meta($post_id, 'key', true);
```

## Common Performance Mistakes

### Using Post Meta for Large Data

Storing thousands of entries in post meta then querying by meta value is slow. Consider:
- Custom tables with proper indexes
- Taxonomies for categorizable data
- Transients for computed aggregations

### Autoloading Large Options

As mentioned earlier, autoloaded options load on every request. Audit your options table for large autoloaded data.

### N+1 Query Problem

Looping through posts and fetching meta for each creates one query per post. WordPress primes the meta cache when using `WP_Query`, but direct `$wpdb` queries don't get this benefit.

### Not Using Indexes

Custom tables without indexes on frequently-queried columns perform poorly at scale. Always index columns used in WHERE, JOIN, and ORDER BY clauses.

## Database Best Practices

1. **Use WordPress APIs when possible** - They handle caching, multisite, and security
2. **Profile before optimizing** - Query Monitor plugin shows actual query performance
3. **Batch operations** - Insert/update many rows in single queries, not loops
4. **Clean up after yourself** - Delete data when your plugin is uninstalled
5. **Test with realistic data** - 10 rows works differently than 10,000

## Further Reading

- [Plugin Structure](./01-plugin-structure.md) - Where to put database code
- [Hooks System](./02-hooks-system.md) - When to run database operations
