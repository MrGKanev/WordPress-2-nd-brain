# Debugging & Profiling Tools

## Overview

"Measure first" is the first principle of optimization. This guide covers the tools and techniques for finding what's actually slow before attempting to fix it.

Guessing at performance problems wastes time. A site slow due to a bad database query won't be fixed by image optimization. Profiling tells you exactly where time is spent.

## WordPress Debug Mode

### Enabling Debug Mode

WordPress has built-in debugging that's disabled by default. In `wp-config.php`:

```php
// Enable debugging
define( 'WP_DEBUG', true );

// Log errors to wp-content/debug.log instead of displaying
define( 'WP_DEBUG_LOG', true );

// Don't display errors on screen (for production debugging)
define( 'WP_DEBUG_DISPLAY', false );

// Log database queries (memory intensive)
define( 'SAVEQUERIES', true );

// Show script and style versions
define( 'SCRIPT_DEBUG', true );
```

### Debug Configuration Patterns

**Development environment:**
```php
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', true );  // Show errors on screen
define( 'SAVEQUERIES', true );
define( 'SCRIPT_DEBUG', true );
```

**Production debugging (temporary):**
```php
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', false );  // Never show to visitors
// Don't enable SAVEQUERIES in production - too slow
```

**Production (normal):**
```php
define( 'WP_DEBUG', false );
```

### Reading debug.log

The log file is at `wp-content/debug.log`:

```bash
# View last 50 lines
tail -50 wp-content/debug.log

# Follow log in real-time
tail -f wp-content/debug.log

# Search for specific errors
grep "Fatal error" wp-content/debug.log

# Count error types
grep -c "Warning" wp-content/debug.log
```

### Custom Debug Logging

```php
// Simple logging
error_log( 'Something happened' );

// Log variables
error_log( print_r( $data, true ) );

// Log with context
error_log( sprintf(
    '[%s] User %d accessed function %s',
    current_time( 'mysql' ),
    get_current_user_id(),
    __FUNCTION__
) );

// Conditional logging
if ( defined( 'WP_DEBUG' ) && WP_DEBUG ) {
    error_log( 'Debug info: ' . $variable );
}
```

## Query Monitor

Query Monitor is the essential WordPress debugging plugin. Install it on any development site.

### What Query Monitor Shows

| Panel | Information |
|-------|-------------|
| **Queries** | All database queries, time, caller, duplicates |
| **Request** | Query vars, rewrite rules, matched rule |
| **Template** | Template hierarchy, loaded template, parts |
| **Hooks** | All actions/filters, components using them |
| **HTTP API** | External requests, response times |
| **PHP Errors** | Notices, warnings, errors with file/line |
| **Environment** | PHP version, MySQL version, memory |

### Reading Query Monitor Data

**Database Queries Panel:**
- Sort by time to find slow queries
- Look for duplicate queries (same query run multiple times)
- Check "Queries by Component" to identify problematic plugins
- Red queries are slow (>0.05s)

**Slow query example analysis:**
```
Query: SELECT * FROM wp_postmeta WHERE meta_key = 'price' ORDER BY meta_value
Time: 2.3 seconds
Caller: WC_Product_Query->get_products()
Rows: 50,000

Problem: Full table scan ordering by unindexed column
Solution: Add index on meta_key, or use custom table for products
```

**HTTP API Panel:**
- Shows external API calls
- Identifies slow third-party services
- Reveals unnecessary external requests

### Query Monitor for AJAX/REST

Query Monitor works with AJAX and REST API requests:
1. Make the request normally
2. Check the Admin Bar dropdown for "AJAX" or "REST API" entries
3. Click to see query data for that request

## Database Query Analysis

### Using SAVEQUERIES

When `SAVEQUERIES` is true, WordPress stores all queries:

```php
// Access stored queries
global $wpdb;
print_r( $wpdb->queries );

// Each query entry:
array(
    0 => 'SELECT * FROM wp_posts...',  // SQL
    1 => 0.0123,                        // Time in seconds
    2 => 'require, wp-blog-header.php...'  // Call stack
)

// Total queries count
echo 'Queries: ' . $wpdb->num_queries;
```

### MySQL EXPLAIN

Analyze query execution plans:

```sql
-- Prefix query with EXPLAIN
EXPLAIN SELECT * FROM wp_posts WHERE post_status = 'publish';

-- Key things to look for:
-- type: ALL (bad - full scan), ref/range (good - using index)
-- key: Which index is being used (NULL = no index)
-- rows: Estimated rows to examine
-- Extra: "Using filesort" or "Using temporary" = potential problem
```

### Slow Query Log

Enable in MySQL configuration (`my.cnf`):

```ini
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 1  # Queries taking >1 second
```

Analyze the log:

```bash
# View slow queries
tail -100 /var/log/mysql/slow.log

# Use mysqldumpslow to summarize
mysqldumpslow -s t /var/log/mysql/slow.log
```

## PHP Profiling

### Xdebug Profiling

Xdebug can generate profiling data showing exactly where PHP time is spent.

**Enable in php.ini:**
```ini
xdebug.mode = profile
xdebug.output_dir = /tmp/xdebug
xdebug.profiler_output_name = cachegrind.out.%p
```

**Trigger profiling for specific requests:**
```ini
xdebug.mode = profile
xdebug.start_with_request = trigger
```

Then add `?XDEBUG_PROFILE=1` to any URL to profile that request.

**Analyze with KCachegrind/QCachegrind:**
- Open the cachegrind file
- Sort by "Self Time" to find expensive functions
- Check call counts for functions called too often

### Simple Timing

For quick measurements without full profiling:

```php
// Time a block of code
$start = microtime( true );

// ... code to measure ...

$elapsed = microtime( true ) - $start;
error_log( sprintf( 'Operation took %.4f seconds', $elapsed ) );

// Reusable timer
class Simple_Timer {
    private static $timers = array();

    public static function start( $name ) {
        self::$timers[ $name ] = microtime( true );
    }

    public static function stop( $name ) {
        if ( isset( self::$timers[ $name ] ) ) {
            $elapsed = microtime( true ) - self::$timers[ $name ];
            error_log( sprintf( '[Timer] %s: %.4f seconds', $name, $elapsed ) );
            return $elapsed;
        }
    }
}

// Usage
Simple_Timer::start( 'api_call' );
$response = wp_remote_get( $url );
Simple_Timer::stop( 'api_call' );
```

### Memory Profiling

```php
// Current memory usage
$memory = memory_get_usage( true );
error_log( 'Memory: ' . round( $memory / 1024 / 1024, 2 ) . ' MB' );

// Peak memory usage
$peak = memory_get_peak_usage( true );
error_log( 'Peak memory: ' . round( $peak / 1024 / 1024, 2 ) . ' MB' );

// Check WordPress memory limit
echo 'WP Memory Limit: ' . WP_MEMORY_LIMIT;
echo 'WP Max Memory: ' . WP_MAX_MEMORY_LIMIT;
```

## Production Monitoring

### New Relic

New Relic provides application performance monitoring (APM) for production:

**What it tracks:**
- Transaction traces (slow page loads)
- Database query performance
- External service response times
- Error rates and types
- PHP runtime metrics

**Key features for WordPress:**
- Automatic WordPress-aware transaction naming
- Plugin performance breakdown
- Real user monitoring (RUM)

**Identifying issues:**
1. Go to Transactions → Sort by "Most Time Consuming"
2. Click transaction to see breakdown
3. Database segment shows slow queries
4. External segment shows slow API calls

### Blackfire

Blackfire is a profiler designed for production:

```bash
# Profile a URL
blackfire curl https://example.com/

# Profile CLI command
blackfire run wp plugin list
```

**Advantages over Xdebug:**
- Low overhead, safe for production
- Call graph visualization
- Comparison between profiles
- Recommendations for improvements

### Server Monitoring

Monitor server resources alongside application performance:

**Netdata** (real-time):
- CPU, memory, disk, network
- Per-process resource usage
- PHP-FPM metrics
- MySQL metrics

**Command-line tools:**
```bash
# System overview
htop

# Disk I/O
iotop

# Network connections
netstat -tuln

# PHP-FPM status
curl http://localhost/status?full

# MySQL process list
mysqladmin processlist
```

## Browser DevTools

### Performance Panel

Chrome's Performance panel records everything the browser does:

1. Open DevTools → Performance
2. Click Record
3. Load the page
4. Stop recording
5. Analyze the timeline

**What to look for:**
- Long tasks (>50ms) blocking main thread
- Layout thrashing (repeated forced reflows)
- Excessive JavaScript execution
- Slow network requests

### Network Panel

**Waterfall analysis:**
- Look for blocking resources (render-blocking JS/CSS)
- Check Time to First Byte (TTFB) - server response time
- Identify slow resources
- Look for unnecessary requests

**Key metrics:**
- TTFB: Time from request to first byte received (server speed)
- Content Download: Time to download the resource (size/bandwidth)
- Waterfall shape: Parallel downloads vs. sequential blocking

### Lighthouse

Built into Chrome DevTools:

1. Open DevTools → Lighthouse
2. Select categories (Performance, Accessibility, etc.)
3. Click "Analyze page load"
4. Review scores and recommendations

**Performance metrics explained:**

| Metric | What It Measures | Target |
|--------|------------------|--------|
| FCP (First Contentful Paint) | Time to first content visible | <1.8s |
| LCP (Largest Contentful Paint) | Time to main content visible | <2.5s |
| TBT (Total Blocking Time) | Time main thread was blocked | <200ms |
| CLS (Cumulative Layout Shift) | Visual stability | <0.1 |
| Speed Index | How quickly content is visually complete | <3.4s |

## Debugging Specific Issues

### White Screen of Death

```php
// 1. Enable debug mode
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', true );

// 2. Check debug.log for fatal errors

// 3. If still white, check PHP error log
// Location varies: /var/log/php/error.log or /var/log/apache2/error.log

// 4. Increase memory if memory exhausted
define( 'WP_MEMORY_LIMIT', '256M' );

// 5. Disable plugins via database if can't access admin
UPDATE wp_options SET option_value = '' WHERE option_name = 'active_plugins';
```

### Slow Admin

Common causes:
1. **Heartbeat API** - Check Network panel for admin-ajax.php calls
2. **Plugin update checks** - Disable with plugin or on slow hosting
3. **Dashboard widgets** - External API calls in widgets
4. **Autoloaded options** - Check with Query Monitor

```php
// Reduce heartbeat frequency
add_filter( 'heartbeat_settings', function( $settings ) {
    $settings['interval'] = 60; // Default is 15-60
    return $settings;
});

// Disable heartbeat completely on specific pages
add_action( 'init', function() {
    if ( is_admin() && ! wp_doing_ajax() ) {
        wp_deregister_script( 'heartbeat' );
    }
});
```

### Slow Frontend

Debugging checklist:
1. **Run Lighthouse** - Get baseline metrics
2. **Check TTFB** - If >600ms, server-side issue
3. **Query Monitor** - Look at database queries
4. **Network panel** - Identify blocking resources
5. **Coverage tool** - Find unused CSS/JS

```bash
# Quick TTFB test
curl -o /dev/null -s -w "TTFB: %{time_starttransfer}s\n" https://example.com/
```

## Debugging Checklist

When investigating performance:

1. **Define the problem**
   - [ ] What's actually slow? (specific page, action, feature)
   - [ ] How slow? (get baseline numbers)
   - [ ] When did it start? (recent change?)

2. **Server-side investigation**
   - [ ] Enable WP_DEBUG and check debug.log
   - [ ] Install Query Monitor and check database queries
   - [ ] Check slow query log
   - [ ] Monitor server resources (CPU, memory, disk)

3. **Frontend investigation**
   - [ ] Run Lighthouse for baseline
   - [ ] Check Network panel waterfall
   - [ ] Analyze Performance panel recording
   - [ ] Test on real mobile device

4. **Isolate the cause**
   - [ ] Disable plugins one by one
   - [ ] Switch to default theme temporarily
   - [ ] Test with caching disabled
   - [ ] Test with CDN bypassed

5. **Measure the fix**
   - [ ] Document before/after metrics
   - [ ] Test under load if relevant
   - [ ] Monitor after deployment

## Further Reading

- [Database Optimization](./07-database-optimizations.md) - Fixing slow queries
- [Core Web Vitals](./08-core-web-vitals-optimizations.md) - Frontend metrics
- [PHP Optimization](./02-php-optimization.md) - PHP configuration for performance
- [Query Monitor Plugin](https://querymonitor.com/) - Official documentation
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/) - Google's guide
