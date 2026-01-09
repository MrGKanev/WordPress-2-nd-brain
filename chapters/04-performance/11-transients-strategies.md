# Transients Deep Dive

## Overview

Transients are WordPress's built-in caching mechanism for storing temporary data with expiration times. Used correctly, they dramatically reduce database queries and API calls. Used incorrectly, they bloat your database and cause performance issues.

## How Transients Work

Transients store data in one of two places:

| Storage Backend | When Used | Characteristics |
|-----------------|-----------|-----------------|
| **Database** (`wp_options`) | No object cache | Persistent, slower, can bloat |
| **Object Cache** (Redis/Memcached) | Object cache configured | Fast, memory-based, auto-evicting |

```php
// Set a transient (expires in 1 hour)
set_transient( 'my_data', $data, HOUR_IN_SECONDS );

// Get a transient
$data = get_transient( 'my_data' );

// Delete a transient
delete_transient( 'my_data' );
```

**Critical behavior:** When object cache is available, transients bypass the database entirely. This is why they're the preferred caching method for plugins - they automatically use the best available storage.

## Transient vs. Option vs. Object Cache

| Storage | Expires | Persists | Best For |
|---------|---------|----------|----------|
| **Transient** | Yes | Yes (DB) or No (object cache) | Cached external data, expensive computations |
| **Option** | No | Yes | Settings, permanent data |
| **Object Cache** | Request only (non-persistent) or TTL (persistent) | Depends on backend | Frequent reads within request |

```php
// Use transient: data that can be regenerated, has TTL
set_transient( 'weather_data', $api_response, HOUR_IN_SECONDS );

// Use option: permanent settings
update_option( 'my_plugin_settings', $settings );

// Use object cache directly: per-request caching (no TTL)
wp_cache_set( 'computed_value', $value, 'my_group' );
```

## Basic Patterns

### Fetch with Cache

The standard pattern for expensive operations:

```php
function get_expensive_data() {
    // Try cache first
    $data = get_transient( 'expensive_data' );

    if ( false === $data ) {
        // Cache miss - generate data
        $data = compute_expensive_data();

        // Store in cache
        set_transient( 'expensive_data', $data, 12 * HOUR_IN_SECONDS );
    }

    return $data;
}
```

### API Response Caching

```php
function get_github_stars( $repo ) {
    $cache_key = 'github_stars_' . sanitize_key( $repo );
    $stars     = get_transient( $cache_key );

    if ( false === $stars ) {
        $response = wp_remote_get( "https://api.github.com/repos/{$repo}" );

        if ( is_wp_error( $response ) ) {
            // API failed - return cached value if any, or default
            return get_option( $cache_key . '_fallback', 0 );
        }

        $body  = json_decode( wp_remote_retrieve_body( $response ), true );
        $stars = isset( $body['stargazers_count'] ) ? absint( $body['stargazers_count'] ) : 0;

        // Cache for 1 hour
        set_transient( $cache_key, $stars, HOUR_IN_SECONDS );

        // Store fallback for API failures
        update_option( $cache_key . '_fallback', $stars );
    }

    return $stars;
}
```

### Query Result Caching

```php
function get_popular_posts( $count = 10 ) {
    $cache_key = 'popular_posts_' . $count;
    $posts     = get_transient( $cache_key );

    if ( false === $posts ) {
        $posts = get_posts( array(
            'post_type'      => 'post',
            'posts_per_page' => $count,
            'meta_key'       => 'views',
            'orderby'        => 'meta_value_num',
            'order'          => 'DESC',
        ) );

        // Cache for 6 hours
        set_transient( $cache_key, $posts, 6 * HOUR_IN_SECONDS );
    }

    return $posts;
}
```

## Expiration Strategies

### Time Constants

WordPress provides constants for common intervals:

```php
MINUTE_IN_SECONDS  // 60
HOUR_IN_SECONDS    // 3600
DAY_IN_SECONDS     // 86400
WEEK_IN_SECONDS    // 604800
MONTH_IN_SECONDS   // 2592000 (30 days)
YEAR_IN_SECONDS    // 31536000
```

### Choosing Expiration Times

| Data Type | Suggested TTL | Reasoning |
|-----------|---------------|-----------|
| API rate-limited data | Match API cache headers | Respect source |
| Social counts | 1-4 hours | Balances freshness and API limits |
| Menu/navigation | 12-24 hours | Rarely changes |
| Exchange rates | 1 hour | Changes frequently |
| Remote RSS feeds | 2-4 hours | Standard RSS practice |
| Computed aggregates | 6-24 hours | Expensive to regenerate |

### No Expiration (Use Carefully)

Setting expiration to `0` means "no expiration" but this behaves differently:
- **With object cache:** Evicted when memory is needed (LRU)
- **Without object cache:** Stored permanently in database (dangerous)

```php
// Dangerous without object cache - never expires in database
set_transient( 'my_data', $data, 0 );

// Safer: use a very long expiration instead
set_transient( 'my_data', $data, YEAR_IN_SECONDS );
```

## Cache Invalidation

The hardest problem in caching: knowing when data is stale.

### Event-Based Invalidation

Delete transients when underlying data changes:

```php
// When a post is updated, clear related caches
add_action( 'save_post', 'invalidate_post_caches' );

function invalidate_post_caches( $post_id ) {
    // Don't run on autosaves
    if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
        return;
    }

    // Clear specific post cache
    delete_transient( 'post_data_' . $post_id );

    // Clear aggregate caches
    delete_transient( 'popular_posts_10' );
    delete_transient( 'recent_posts' );

    // Clear category-specific caches
    $categories = get_the_category( $post_id );
    foreach ( $categories as $cat ) {
        delete_transient( 'posts_in_cat_' . $cat->term_id );
    }
}
```

### Pattern-Based Deletion

For related transients, use a naming convention:

```php
// Store with prefix
set_transient( 'myprefix_user_123_profile', $data, HOUR_IN_SECONDS );
set_transient( 'myprefix_user_123_posts', $posts, HOUR_IN_SECONDS );

// Delete all user caches (requires database query without object cache)
function delete_user_transients( $user_id ) {
    global $wpdb;

    // Delete from database
    $wpdb->query( $wpdb->prepare(
        "DELETE FROM {$wpdb->options}
         WHERE option_name LIKE %s
         OR option_name LIKE %s",
        $wpdb->esc_like( '_transient_myprefix_user_' . $user_id ) . '%',
        $wpdb->esc_like( '_transient_timeout_myprefix_user_' . $user_id ) . '%'
    ) );

    // With object cache, you'd need to track keys separately
}
```

### Version-Based Invalidation

For broad cache invalidation without deleting individual keys:

```php
function get_cache_version() {
    $version = get_option( 'my_cache_version', 1 );
    return $version;
}

function bump_cache_version() {
    $version = get_option( 'my_cache_version', 1 );
    update_option( 'my_cache_version', $version + 1 );
}

// Include version in cache key
function get_cached_data() {
    $version   = get_cache_version();
    $cache_key = 'my_data_v' . $version;

    $data = get_transient( $cache_key );

    if ( false === $data ) {
        $data = generate_data();
        set_transient( $cache_key, $data, DAY_IN_SECONDS );
    }

    return $data;
}

// Invalidate all caches by bumping version
// Old versioned keys will expire naturally
bump_cache_version();
```

## Site Transients (Multisite)

For multisite installations, site transients are shared across all sites:

```php
// Network-wide transient
set_site_transient( 'network_stats', $stats, HOUR_IN_SECONDS );
$stats = get_site_transient( 'network_stats' );
delete_site_transient( 'network_stats' );

// Regular transient (per-site)
set_transient( 'site_stats', $stats, HOUR_IN_SECONDS );
```

Use site transients for:
- Network-wide settings
- Shared API responses
- Cross-site aggregations

## Database Bloat Problem

Without object cache, transients are stored in `wp_options`:

```sql
-- Each transient creates TWO rows
_transient_my_cache           -- The data
_transient_timeout_my_cache   -- The expiration timestamp
```

### Causes of Bloat

1. **Too many unique keys:** Dynamic keys like `cache_user_{id}_page_{num}` create thousands of entries
2. **No expiration:** Setting expiration to `0` without object cache
3. **Expired transients not cleaned:** WordPress only cleans on access, not proactively

### Checking for Bloat

```sql
-- Count transients
SELECT COUNT(*) FROM wp_options
WHERE option_name LIKE '%_transient_%';

-- Size of transients
SELECT SUM(LENGTH(option_value)) / 1024 / 1024 as MB
FROM wp_options
WHERE option_name LIKE '%_transient_%';

-- Largest transients
SELECT option_name, LENGTH(option_value) / 1024 as KB
FROM wp_options
WHERE option_name LIKE '%_transient_%'
ORDER BY LENGTH(option_value) DESC
LIMIT 20;
```

### Cleaning Expired Transients

```php
// WP-CLI
// wp transient delete --expired

// Programmatically
function clean_expired_transients() {
    global $wpdb;

    $time = time();

    // Find expired transients
    $expired = $wpdb->get_col( $wpdb->prepare(
        "SELECT option_name FROM {$wpdb->options}
         WHERE option_name LIKE %s
         AND option_value < %d",
        $wpdb->esc_like( '_transient_timeout_' ) . '%',
        $time
    ) );

    foreach ( $expired as $timeout_key ) {
        $transient_key = str_replace( '_transient_timeout_', '_transient_', $timeout_key );
        delete_option( $transient_key );
        delete_option( $timeout_key );
    }

    return count( $expired );
}

// Schedule cleanup
add_action( 'wp_scheduled_delete', 'clean_expired_transients' );
```

## Cache Warming

Pre-populate caches before they're needed:

```php
// Warm cache after post is published
add_action( 'publish_post', 'warm_post_cache' );

function warm_post_cache( $post_id ) {
    // Pre-generate expensive data
    $post = get_post( $post_id );

    // Cache reading time calculation
    $content     = strip_tags( $post->post_content );
    $word_count  = str_word_count( $content );
    $reading_time = ceil( $word_count / 200 );

    set_transient(
        'reading_time_' . $post_id,
        $reading_time,
        WEEK_IN_SECONDS
    );

    // Pre-fetch related posts
    get_related_posts( $post_id ); // This function caches internally
}
```

### Scheduled Warming

```php
// Register cron event
add_action( 'wp', 'schedule_cache_warming' );

function schedule_cache_warming() {
    if ( ! wp_next_scheduled( 'warm_popular_content_cache' ) ) {
        wp_schedule_event( time(), 'hourly', 'warm_popular_content_cache' );
    }
}

add_action( 'warm_popular_content_cache', 'warm_popular_content' );

function warm_popular_content() {
    // Regenerate popular posts cache before it expires
    delete_transient( 'popular_posts' );
    get_popular_posts(); // Regenerates and caches
}
```

## Debugging Transients

### Check if Transient Exists

```php
// Check existence and value
$value = get_transient( 'my_key' );
if ( false === $value ) {
    echo 'Transient does not exist or expired';
}

// Check in database directly
global $wpdb;
$exists = $wpdb->get_var( $wpdb->prepare(
    "SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name = %s",
    '_transient_my_key'
) );
```

### Query Monitor

Query Monitor shows:
- All transients get/set operations
- Which transients came from database vs. object cache
- Transient sizes

### Logging Transient Operations

```php
// Debug wrapper
function debug_get_transient( $key ) {
    $start = microtime( true );
    $value = get_transient( $key );
    $time  = microtime( true ) - $start;

    $status = ( false === $value ) ? 'MISS' : 'HIT';
    error_log( sprintf(
        '[Transient] %s: %s (%.4fs)',
        $key,
        $status,
        $time
    ) );

    return $value;
}
```

## Best Practices

### Do

- **Use meaningful expiration times** - Match data volatility
- **Invalidate on data change** - Hook into save/update actions
- **Include version in keys** - Makes bulk invalidation easy
- **Use object cache in production** - Avoids database bloat
- **Test cache misses** - Ensure regeneration works correctly

### Don't

- **Don't cache user-specific data in transients** - Use user meta or sessions
- **Don't use dynamic keys without limits** - Can create thousands of entries
- **Don't set 0 expiration without object cache** - Creates permanent database rows
- **Don't store serialized objects with closures** - Will fail to unserialize
- **Don't assume cache exists** - Always handle the miss case

### Key Naming Convention

```php
// Good: descriptive, scoped, versioned
'myplugin_github_stars_repo_v1'
'myplugin_user_stats_123'
'myplugin_posts_category_5_page_1'

// Bad: generic, no scope
'data'
'cache'
'temp'
```

## Complete Example

```php
class My_Cached_Service {

    private $cache_group = 'my_service';
    private $default_ttl = HOUR_IN_SECONDS;

    /**
     * Get data with caching
     */
    public function get_data( $id ) {
        $cache_key = $this->get_cache_key( 'data', $id );

        $data = get_transient( $cache_key );

        if ( false === $data ) {
            $data = $this->fetch_data( $id );

            if ( ! is_wp_error( $data ) ) {
                set_transient( $cache_key, $data, $this->default_ttl );
            }
        }

        return $data;
    }

    /**
     * Invalidate cache for an item
     */
    public function invalidate( $id ) {
        delete_transient( $this->get_cache_key( 'data', $id ) );
    }

    /**
     * Invalidate all caches (version bump)
     */
    public function invalidate_all() {
        $version = get_option( $this->cache_group . '_version', 1 );
        update_option( $this->cache_group . '_version', $version + 1 );
    }

    /**
     * Generate cache key with version
     */
    private function get_cache_key( $type, $id ) {
        $version = get_option( $this->cache_group . '_version', 1 );
        return sprintf(
            '%s_%s_%s_v%d',
            $this->cache_group,
            $type,
            $id,
            $version
        );
    }

    /**
     * Fetch fresh data (expensive operation)
     */
    private function fetch_data( $id ) {
        // API call, complex query, etc.
        return wp_remote_get( 'https://api.example.com/data/' . $id );
    }
}

// Usage
$service = new My_Cached_Service();
$data = $service->get_data( 123 );  // Cached
$service->invalidate( 123 );         // Clear one
$service->invalidate_all();          // Clear all
```

## Further Reading

- [Database Operations](../08-plugin-development/03-database-operations.md) - Options API and storage
- [Database Optimization](./07-database-optimizations.md) - Cleaning up bloat
- [Scaling WordPress](./09-scaling-wordpress.md) - Object caching at scale
- [WordPress Transients API](https://developer.wordpress.org/apis/transients/) - Official documentation
