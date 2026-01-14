# Multisite Performance

## Overview

WordPress Multisite introduces performance challenges that don't exist in single-site installations. Network-wide queries, cross-site lookups, and shared tables create overhead that scales with network size. This chapter covers identifying and addressing Multisite-specific bottlenecks.

## Multisite Architecture

WordPress Multisite runs multiple sites from a single WordPress installation. Instead of installing WordPress five times for five sites, you install it once and create five sites within it. This provides centralized management (one codebase, one plugin set, one update process) but introduces shared resources that can become bottlenecks.

Understanding the database structure helps diagnose performance issues:

```
Global Tables (shared):
├── wp_users           - All users across network
├── wp_usermeta        - User metadata
├── wp_blogs           - Site registry
├── wp_site            - Network registry
├── wp_sitemeta        - Network options
└── wp_blogmeta        - Per-site metadata

Per-Site Tables (multiplied):
├── wp_2_posts         - Site 2 posts
├── wp_2_postmeta      - Site 2 post metadata
├── wp_3_posts         - Site 3 posts
├── wp_3_postmeta      - Site 3 post metadata
└── ... (grows with each site)
```

The main site (site ID 1) uses the base prefix (`wp_posts`). Additional sites get numbered prefixes (`wp_2_posts`, `wp_3_posts`). This means a network with 100 sites has 100+ copies of each core table—and the global tables (users, usermeta) contain data for all sites combined.

This architecture creates two distinct scaling concerns: global tables that grow with total users across all sites, and the sheer number of tables that database operations (backups, maintenance) must handle.

## Common Performance Issues

### 1. switch_to_blog() Overhead

The `switch_to_blog()` function is multisite's way of working with data from different sites. It changes WordPress's internal context—the database table prefix, the site URL, options, and cache—so that functions like `get_posts()` or `get_option()` work against a different site's data.

```php
// Common pattern that causes problems
$sites = get_sites(['number' => 100]);
foreach ($sites as $site) {
    switch_to_blog($site->blog_id);
    // Do something on this site
    $count = wp_count_posts();
    restore_current_blog();
}
```

This looks simple but hides significant overhead. Each `switch_to_blog()` call:

**Problems:**
- Clears and rebuilds object cache on each switch—cached data from the previous site is irrelevant, so WordPress resets cache state
- Reloads site options—queries the database for the new site's options
- Creates memory overhead from stack of switched sites—WordPress tracks the "stack" of switches so `restore_current_blog()` can return to the right place
- Doesn't scale—100 sites = 100 context switches, each with its own overhead

In a loop processing 500 sites, you're paying this cost 500 times. What looks like a simple foreach becomes the performance bottleneck of your entire operation.

**Solutions:**

Direct database queries when possible:

```php
global $wpdb;

// Instead of switching to count posts
$counts = $wpdb->get_results("
    SELECT blog_id,
           (SELECT COUNT(*) FROM {$wpdb->base_prefix}{blog_id}_posts
            WHERE post_status = 'publish' AND post_type = 'post') as count
    FROM {$wpdb->blogs}
    WHERE deleted = 0 AND archived = 0
");
```

Batch operations with single switch:

```php
// Group operations by site
$sites = get_sites(['number' => 100]);
$results = [];

foreach ($sites as $site) {
    switch_to_blog($site->blog_id);

    // Do ALL work for this site at once
    $results[$site->blog_id] = [
        'posts' => wp_count_posts(),
        'users' => count_users(),
        'options' => get_option('blogname'),
    ];

    restore_current_blog();
}
```

Cache results aggressively:

```php
function get_network_post_counts() {
    $cache_key = 'network_post_counts';
    $counts = get_site_transient($cache_key);

    if (false === $counts) {
        $counts = [];
        foreach (get_sites(['number' => 0]) as $site) {
            switch_to_blog($site->blog_id);
            $counts[$site->blog_id] = wp_count_posts()->publish;
            restore_current_blog();
        }
        set_site_transient($cache_key, $counts, HOUR_IN_SECONDS);
    }

    return $counts;
}
```

### 2. Global Table Bloat

Unlike per-site tables that are isolated to one site, global tables accumulate data from the entire network. Every user who registers on any site ends up in `wp_users`. Every plugin that stores user preferences adds rows to `wp_usermeta` for every user on every site.

**wp_users / wp_usermeta:**

```sql
-- Check user table size
SELECT COUNT(*) as users FROM wp_users;
SELECT COUNT(*) as meta_rows FROM wp_usermeta;
```

The math is concerning: if you have 10,000 users and each user has 25 meta rows (WordPress defaults plus a few plugins), that's 250,000 rows in `wp_usermeta`. Add a plugin that stores per-site preferences for users, and each user gets additional meta for each site they're on. The table can grow explosively.

Large networks can have millions of usermeta rows. Each user adds 20+ meta entries by default, and many plugins add their own.

**Solutions:**
- Clean orphaned usermeta: `DELETE FROM wp_usermeta WHERE user_id NOT IN (SELECT ID FROM wp_users)`
- Audit plugins adding excessive user meta
- Consider custom tables for high-volume user data

**wp_blogs / wp_sitemeta:**

```sql
-- Check for site bloat
SELECT COUNT(*) FROM wp_blogs WHERE deleted = 1;  -- Soft-deleted sites
SELECT COUNT(*) FROM wp_sitemeta;
```

**Solutions:**
- Permanently delete soft-deleted sites
- Audit network options stored in sitemeta
- Clean up after removed plugins

### 3. Object Cache Key Collisions

Object caching (see [Object Caching](./14-object-caching.md)) stores data by key. In single-site WordPress, the key `my_data` is unambiguous. In multisite, `my_data` could mean data from any site—leading to one site receiving another site's cached data.

WordPress core handles this by automatically prefixing keys with the blog ID for most cache groups. But plugins writing custom caching code might not be aware:

```php
// Dangerous in multisite - same key on all sites
$data = wp_cache_get('my_data');

// Correct - WordPress adds blog_id automatically for most functions
// But custom caching code needs awareness
$data = wp_cache_get('my_data', 'my_plugin_' . get_current_blog_id());
```

The danger isn't just getting stale data—it's getting another site's private data. A poorly-written plugin could cache user-specific information without site prefixing, leading to Site B's users seeing Site A's private content.

Redis/Memcached configuration must account for multisite, especially if you're running multiple WordPress installations on the same cache server:

```php
// wp-config.php
define('WP_CACHE_KEY_SALT', 'mynetwork_');
```

This salt ensures your network's cache keys don't collide with another WordPress installation sharing the same Redis server.

### 4. Cross-Site Queries

A common multisite feature request is "show recent posts from all sites" or "display network-wide search results." This requires querying across site boundaries—something WordPress's standard functions don't support directly. Each site's posts live in separate tables (`wp_2_posts`, `wp_3_posts`, etc.), so there's no single query that covers them all.

Developers often resort to the switch-and-loop pattern, creating the N+1 query problem:

```php
// BAD: N+1 query pattern
$all_recent_posts = [];
foreach (get_sites() as $site) {
    switch_to_blog($site->blog_id);
    $posts = get_posts(['numberposts' => 5]);
    $all_recent_posts = array_merge($all_recent_posts, $posts);
    restore_current_blog();
}

For 100 sites, this executes 100+ queries plus all the `switch_to_blog()` overhead. Even with caching, the first uncached run can take several seconds. The solution is a SQL UNION query that hits all tables in a single database round-trip:

// BETTER: Union query (requires custom SQL)
global $wpdb;
$sites = get_sites(['number' => 0]);
$unions = [];

foreach ($sites as $site) {
    $table = $wpdb->base_prefix . $site->blog_id . '_posts';
    $unions[] = "(SELECT *, {$site->blog_id} as blog_id FROM {$table}
                  WHERE post_status = 'publish'
                  ORDER BY post_date DESC LIMIT 5)";
}

$sql = implode(' UNION ALL ', $unions) . ' ORDER BY post_date DESC LIMIT 50';
$posts = $wpdb->get_results($sql);
```

### 5. Network Admin Slowness

The network admin dashboard (at `/wp-admin/network/`) presents a unique challenge: its interface is designed to provide an overview of the entire network, which means querying all sites on many pages.

**Sites list:**
- Each page load queries `wp_blogs` to build the site list
- Statistics (post counts, user counts) require querying each site's tables
- Large networks (1000+ sites) slow significantly—the admin wasn't designed for this scale

The core issue is architectural: WordPress's network admin assumes you have tens or maybe hundreds of sites. University networks or hosting platforms with thousands of sites push beyond its design limits.

**Solutions:**
- Increase PHP memory limit for network admin (the admin user needs more than frontend visitors)
- Use pagination strictly—never try to load "all" sites on one page
- Disable admin features that scan all sites (some plugins add network-wide statistics)
- Consider custom admin solutions for very large networks—build a separate management interface that queries efficiently

## Caching Strategies for Multisite

### Object Cache Requirements

Multisite object caching needs:

1. **Proper key prefixing** - Each site's cache is isolated
2. **Network-wide cache** - For cross-site operations
3. **Sufficient memory** - Multiply single-site needs by active sites

```php
// Site-specific cache (automatic)
wp_cache_get('posts', 'default');  // Automatically prefixed with blog_id

// Network-wide cache
wp_cache_get('network_data', 'site-transient');
```

### Page Cache Considerations

| Approach | Multisite Compatibility |
|----------|------------------------|
| [WP Super Cache](https://wordpress.org/plugins/wp-super-cache/) | Good - handles multisite natively |
| [W3 Total Cache](https://wordpress.org/plugins/w3-total-cache/) | Good - multisite aware |
| [WP Rocket](https://wp-rocket.me/) | Good - per-site configuration |
| [Varnish](https://varnish-cache.org/)/Nginx | Requires proper VCL/config for subdirectory installs |

**Subdomain vs Subdirectory:**

Subdomain installs (`site1.example.com`) cache more cleanly—each site has distinct URLs.

Subdirectory installs (`example.com/site1/`) require cache rules that respect path prefixes.

### Redis for Multisite

Configuration with proper isolation:

```php
// wp-config.php
define('WP_REDIS_DATABASE', 0);  // All sites in one database is fine

// Automatic prefixing handles isolation
// But set a salt to avoid conflicts with other WP installs
define('WP_CACHE_KEY_SALT', 'my_network_');
```

## Database Optimization

### Index Optimization

Global tables benefit from additional indexes:

```sql
-- Speed up user queries by email domain (for large networks)
CREATE INDEX idx_user_email_domain ON wp_users ((SUBSTRING_INDEX(user_email, '@', -1)));

-- Speed up blog lookups
CREATE INDEX idx_blogs_domain ON wp_blogs (domain);
```

### Table Maintenance

With many tables, maintenance becomes critical:

```bash
# Optimize all tables in the network
wp db optimize --network

# Or target specific table patterns
mysqlcheck -o wordpress "wp_%_posts"
```

### Query Monitoring

Enable slow query log and watch for:

```sql
-- Queries without blog_id filter
SELECT * FROM wp_usermeta WHERE meta_key = '...'
-- Should usually include user_id constraint

-- Full table scans on wp_blogs
SELECT * FROM wp_blogs WHERE ... -- Ensure indexed columns used
```

## Scaling Large Networks

### When to Worry

| Network Size | Typical Issues |
|--------------|----------------|
| 1-50 sites | Usually fine with standard optimization |
| 50-500 sites | switch_to_blog overhead noticeable |
| 500-5000 sites | Database size, admin slowness |
| 5000+ sites | Architecture review needed |

### Horizontal Scaling Considerations

Multisite complicates horizontal scaling:

**Database:**
- Read replicas work but all sites share the primary
- Sharding by site group possible but complex

**File Storage:**
- Each site has uploads directory
- Shared storage (S3, EFS) handles this well

**Object Cache:**
- Single Redis instance can serve all sites
- Memory requirements scale with active sites, not total sites

### Alternative Architectures

For very large networks, consider:

**Satellite installations:**
- Separate WordPress installs per major site
- Share users via external authentication
- Lose multisite benefits but gain independence

**Headless / API approach:**
- Central content API
- Separate frontend instances
- Better performance isolation

## Performance Checklist

For existing multisite networks:

- [ ] Object cache (Redis) configured with proper prefixing
- [ ] Page caching enabled and tested per-site
- [ ] `switch_to_blog()` usage audited and optimized
- [ ] Slow query log enabled, patterns identified
- [ ] Global table sizes monitored
- [ ] Orphaned data cleaned (deleted sites, users)
- [ ] Network admin pagination configured
- [ ] Memory limits appropriate for network size

## Further Reading

**Internal:**
- [Object Caching](./14-object-caching.md) - Deep dive into Redis/Memcached
- [Database Optimization](./07-database-optimizations.md) - Query and table optimization
- [Scaling WordPress](./09-scaling-wordpress.md) - Horizontal scaling patterns

**External:**
- [WordPress Multisite Developer Resources](https://developer.wordpress.org/advanced-administration/multisite/) - Official documentation
- [WP-CLI Multisite commands](https://developer.wordpress.org/cli/commands/) - Command-line management
- [Developer Blog - Multisite](https://developer.wordpress.org/news/tag/multisite/) - Latest multisite updates and guidance
