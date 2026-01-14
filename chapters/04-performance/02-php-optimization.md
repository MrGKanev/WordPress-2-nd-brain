# Advanced PHP Performance Optimization

## Overview

Beyond basic PHP-FPM configuration, advanced PHP performance optimization involves comprehensive OPCache implementation, systematic performance testing, and data-driven tuning approaches. This section covers enterprise-level optimization techniques that can dramatically reduce server requirements.

## OPCache Implementation

### Understanding OPCache

OPCache is an opcode cache that eliminates expensive PHP parsing operations on every request:

**Without OPCache:**

1. Interpreter loads script
2. Script parsed into syntax tree
3. Tree converted to opcodes
4. Zend Engine executes opcodes
5. Output

**With OPCache:**

1. Interpreter loads script
2. Zend Engine executes cached opcodes
3. Output

This optimization can provide 3-10x performance improvements for WordPress sites.

## PHP Version Impact

### Why PHP Version Matters

Upgrading PHP is often the easiest performance win available. Each major PHP version includes engine optimizations that make your existing code run faster without any changes on your part. The PHP development team focuses heavily on performance, and WordPress benefits directly from these improvements.

The difference is dramatic. A WordPress site running on PHP 5.6 requires roughly three times the server resources to handle the same traffic as the identical site on PHP 8.x. This translates directly to hosting costs—you can either serve three times more visitors or reduce your server budget by two-thirds.

### Performance Gains by Version

| Migration Path | Performance Gain | What Changed |
|----------------|------------------|--------------|
| PHP 5.6 → 7.0 | 2x faster | Complete engine rewrite (phpng project) |
| PHP 7.0 → 7.4 | 30-50% faster | Preloading, typed properties, FFI |
| PHP 7.4 → 8.0 | 10-20% faster | JIT compiler, union types, named arguments |
| PHP 8.0 → 8.1 | 5-10% faster | Fibers, enums, readonly properties |
| PHP 8.1 → 8.2 | 3-8% faster | Readonly classes, memory optimizations |
| PHP 8.2 → 8.3 | 2-5% faster | Typed class constants, json_validate() |
| PHP 8.3 → 8.4 | 2-5% faster | Property hooks, asymmetric visibility |
| PHP 8.4 → 8.5 | 2-3% faster | Continued incremental improvements |

The biggest gains came with PHP 7.0, which was essentially a complete rewrite of the PHP engine. Since then, each version delivers incremental but meaningful improvements. Even small percentages add up—going from PHP 7.4 to 8.5 represents roughly 25-30% better performance.

### Understanding JIT Compilation

PHP 8.0 introduced Just-In-Time (JIT) compilation, which compiles PHP code to machine code at runtime rather than interpreting it. This sounds revolutionary, but for WordPress the benefits are modest—typically around 5% improvement.

The reason is that WordPress spends most of its time waiting: waiting for database queries, waiting for file operations, waiting for external API calls. JIT helps CPU-bound tasks (mathematical calculations, image processing, complex algorithms), but WordPress is fundamentally I/O-bound. The bottleneck isn't how fast PHP executes code; it's how fast the database responds.

JIT becomes more valuable for computation-heavy plugins—image manipulation, PDF generation, or complex data processing. For typical content-focused WordPress sites, the configuration complexity outweighs the marginal gains. Focus on OPcache and PHP-FPM tuning first; consider JIT only if profiling shows CPU as your bottleneck.

### PHP 8.x Features Relevant to WordPress

**PHP 8.0** brought named arguments, which make function calls more readable, and union types for better code documentation. The nullsafe operator (`?->`) simplifies code that checks for null values throughout a chain.

**PHP 8.1** introduced enums (finally!) and readonly properties, reducing boilerplate in plugin development. Fibers enable async-like programming patterns, though WordPress core doesn't yet leverage them.

**PHP 8.2** focused on readonly classes and deprecated dynamic properties—the latter being significant for WordPress plugins that relied on this pattern. Some older plugins needed updates.

**PHP 8.3** added typed class constants and the `json_validate()` function, useful for validating JSON without parsing it. The `#[\Override]` attribute helps catch method naming mistakes in class hierarchies.

**PHP 8.4** introduced property hooks, allowing getter/setter logic without explicit methods, and asymmetric visibility (public read, private write). These features modernize PHP's object model significantly.

**PHP 8.5** continues incremental improvements to the engine and standard library, focusing on performance and developer experience.

### Checking Compatibility Before Upgrading

Before upgrading PHP in production, verify that your themes, plugins, and custom code work with the new version. Incompatibilities typically manifest as deprecation warnings, fatal errors, or subtle behavioral changes.

The PHP Compatibility Checker plugin scans your site and reports potential issues. For more thorough analysis, PHPCompatibilityWP (a PHP_CodeSniffer standard) checks code against specific PHP version requirements. Running these tools on staging before upgrading production prevents unpleasant surprises.

Most actively maintained plugins work on PHP 8.x. Problems usually appear with abandoned plugins, custom code written years ago, or plugins that rely on deprecated PHP features. The WordPress core team maintains compatibility across PHP versions, so WordPress itself rarely causes upgrade issues.

**Resources:**
- [php.watch](https://php.watch/) - Detailed version-specific migration guides
- [PHPCompatibilityWP](https://github.com/PHPCompatibility/PHPCompatibilityWP) - WordPress-specific compatibility checking

### Enabling and Verifying OPCache

Most modern PHP installations include OPcache, but it may not be enabled by default. You can verify its status by checking PHP's version output (which mentions OPcache if loaded) or by examining the PHP configuration through `php -i` or a `phpinfo()` page.

Once enabled, OPcache needs memory allocation. The memory consumption setting determines how much RAM OPcache can use to store compiled scripts. For WordPress sites with many plugins, 256MB is a reasonable starting point. Smaller sites might work with 128MB, while large multisite installations might need 512MB or more.

The max_accelerated_files setting limits how many PHP files OPcache will cache. WordPress core, a theme, and several plugins easily exceed the default limit, so increase this to 20,000 or higher. Running out of file slots forces OPcache to evict cached scripts, defeating its purpose.

### Development vs Production Settings

OPcache behaves differently depending on whether timestamp validation is enabled. With validation on, OPcache checks if source files have changed and recompiles them automatically—essential for development where you're constantly editing code. With validation off, OPcache ignores file modifications and serves cached opcodes indefinitely—optimal for production where code doesn't change between deployments.

The trade-off is clear: validation adds overhead (checking file timestamps on every request) but ensures code changes take effect immediately. In production, disable validation and manually clear the cache after deployments. In development, enable validation so your changes appear instantly.

### Understanding File-Based Persistence

By default, OPcache stores everything in shared memory, which is fast but volatile. When PHP restarts—due to configuration changes, server reboots, or deployment procedures—the cache empties and must be rebuilt from scratch. During this warm-up period, every PHP file must be parsed and compiled again, causing temporarily slower responses.

File-based persistence solves this by writing compiled opcodes to disk alongside the memory cache. When PHP restarts, it reads pre-compiled opcodes from disk rather than parsing source files. This eliminates the warm-up penalty almost entirely. The first request after restart loads opcodes from disk into memory; subsequent requests use the fast memory cache.

This persistence is particularly valuable for sites with frequent PHP-FPM reloads or for shared hosting environments where you have limited control over the PHP lifecycle. The disk cache acts as a safety net, ensuring performance remains consistent even when the memory cache gets cleared.

### Cache Invalidation After Deployments

When timestamp validation is disabled (as it should be in production), OPcache won't notice when you deploy new code. You must explicitly clear the cache after deployments. The simplest approach is reloading PHP-FPM, which clears the memory cache entirely. With file persistence enabled, you may also need to clear the file cache directory, or configure PHP to regenerate it automatically.

Many deployment tools and hosting platforms handle this automatically. If you're building custom deployment scripts, include a cache clear step after uploading new files. Forgetting this step is a common source of "I deployed but nothing changed" confusion.

The most reliable way to clear OPcache is reloading PHP-FPM. This forces all worker processes to restart, clearing the memory cache completely:

```bash
sudo systemctl reload php8.3-fpm
```

### Production Configuration Example

This configuration combines everything discussed above. The `memory_consumption` of 256MB handles most WordPress sites with multiple plugins. The `max_accelerated_files` at 20000 ensures WordPress core, themes, and plugins all fit. Timestamp validation is disabled for maximum performance, and file cache provides persistence across restarts.

```ini
[opcache]
; Enable OPcache
opcache.enable=1

; Memory allocation - 256MB handles most WordPress sites
opcache.memory_consumption=256

; String interning saves memory when the same strings appear in multiple files
opcache.interned_strings_buffer=16

; WordPress + plugins easily exceed defaults - set high
opcache.max_accelerated_files=20000

; Production: disable timestamp checking for speed
opcache.validate_timestamps=0
opcache.revalidate_freq=0

; File cache for persistence across PHP restarts
opcache.file_cache=/var/cache/php/opcache
opcache.file_cache_only=0

; Keep comments - needed for some plugins that use annotations
opcache.save_comments=1

; Allow file_exists() to use cache
opcache.enable_file_override=1
```

For development environments, change `validate_timestamps` to 1 and `revalidate_freq` to 2 so code changes appear without manual cache clearing.

### OPcache Preloading

PHP 7.4 introduced preloading, which goes further than standard OPcache by loading specified files once at server startup and keeping them in memory permanently. Unlike regular OPcache entries that might be evicted under memory pressure, preloaded files stay resident.

The theory is appealing: identify your most-used files, preload them, and eliminate even the small overhead of checking the cache. In practice, preloading is complex with WordPress because of how plugins work. WordPress dynamically loads plugins based on database configuration, and preloading files that reference not-yet-loaded dependencies causes problems. The plugin ecosystem's diversity makes it difficult to predict which files will actually be used.

If you want to experiment with preloading, you need a preload script that specifies which files to load. This script runs once when PHP starts, not on every request:

```php
<?php
// preload.php - runs once at PHP startup
$files = [
    '/var/www/html/wp-includes/class-wp.php',
    '/var/www/html/wp-includes/formatting.php',
    '/var/www/html/wp-includes/plugin.php',
];

foreach ($files as $file) {
    if (file_exists($file)) {
        opcache_compile_file($file);
    }
}
```

Then configure PHP to use it. The `preload_user` setting specifies which system user runs the preload script—typically the same user that runs PHP-FPM:

```ini
opcache.preload=/var/www/html/preload.php
opcache.preload_user=www-data
```

For most WordPress sites, standard OPcache with file persistence provides 95% of the benefit with none of the complexity. Consider preloading only if you've profiled your specific site, identified frequently-loaded core files, and have the expertise to troubleshoot issues that arise. Frameworks like Laravel, with their predictable structure, benefit more from preloading than WordPress does.

## Advanced PHP-FPM Tuning

### Memory Usage Calculation

Calculate precise PHP process memory usage:

```bash
# Get average memory per PHP process
ps --no-headers -eo rss,comm | grep php | awk '{sum+=$1; count++} END {if (count > 0) print "Average Memory Usage (KB):", sum/count; else print "No PHP processes found."}'
```

### Process Count Optimization

The traditional calculation is:

```
pm.max_children = Available RAM / Average Process Size
```

However, optimal performance often requires fewer processes than maximum memory allows due to:

- CPU limitations
- Database connection limits  
- I/O bottlenecks
- Context switching overhead

### Real-World Example Configuration

Based on testing with a 4-core, 8GB server running WordPress:

```ini
; /etc/php/8.2/fpm/pool.d/www.conf
pm = dynamic
pm.max_children = 100
pm.start_servers = 70
pm.min_spare_servers = 60
pm.max_spare_servers = 80
pm.max_requests = 1000
```

This configuration:

- Starts with adequate process pool
- Allows scaling under load
- Prevents memory exhaustion
- Handles typical WordPress traffic patterns

## Performance Testing Methodology

### Load Testing Setup

Use Apache Bench for basic performance testing:

```bash
# Test with 10 concurrent connections, 1000 total requests
ab -n 1000 -c 10 https://yoursite.com/

# Test specific WordPress pages
ab -n 500 -c 5 https://yoursite.com/sample-post/
ab -n 500 -c 5 https://yoursite.com/wp-admin/
```

### Monitoring During Tests

Monitor these metrics during load testing:

```bash
# CPU usage
top -p $(pgrep php-fpm | tr '\n' ',' | sed 's/,$//')

# Memory usage  
free -m

# Active PHP processes
ps aux | grep php-fpm | wc -l

# PHP-FPM status (if enabled)
curl -s localhost/status?full
```

### Performance Benchmarking Process

1. **Establish baseline** - Test with default settings
2. **Enable OPCache** - Measure improvement
3. **Tune PHP-FPM** - Iteratively optimize process settings
4. **Test different workloads** - Admin pages, frontend, API endpoints
5. **Monitor resource utilization** - Ensure optimal CPU/memory usage

## WordPress-Specific Optimizations

### Complementary WordPress Settings

```php
// wp-config.php optimizations for performance testing
define('WP_MEMORY_LIMIT', '256M');
define('WP_MAX_MEMORY_LIMIT', '512M');
define('DISABLE_WP_CRON', true);
define('WP_POST_REVISIONS', 3);

// Disable debugging in production
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);
```

### Cache WordPress Configuration

For Laravel Artisan equivalent in WordPress:

```bash
# Use WP-CLI to clear/regenerate caches
wp cache flush
wp rewrite flush
wp plugin list --status=active
```

## Case Study Results

Real-world optimization results from a high-traffic WordPress site:

**Before Optimization:**

- 5x t2.xlarge servers (40 vCPUs, 160GB RAM)
- CPU usage: 15-30%
- Memory usage: ~2GB total
- Average response time: 150ms
- OPCache: Disabled

**After Optimization:**

- 2x t2.xlarge servers (16 vCPUs, 64GB RAM)  
- CPU usage: ~2%
- Memory usage: ~7GB total
- Average response time: 23ms
- OPCache: Enabled with optimized settings

**Performance Improvement:**

- 6.5x faster response times
- 60% reduction in server costs
- 87% reduction in CPU usage
- Better resource utilization

## Implementation Steps

1. **Baseline measurement** - Document current performance metrics
2. **Enable OPCache** - Implement with production-optimized settings
3. **PHP-FPM tuning** - Start conservative, increase based on monitoring
4. **Load testing** - Use systematic testing across different page types
5. **Monitor and adjust** - Use real traffic data to fine-tune settings
6. **Document changes** - Keep configuration changes tracked

## Monitoring Tools

Set up comprehensive monitoring:

- **Server metrics** - CPU, memory, disk I/O
- **PHP-FPM metrics** - Process utilization, queue lengths
- **Application metrics** - Response times, error rates
- **Database metrics** - Query performance, connection counts

## Common Pitfalls

1. **Over-provisioning processes** - More isn't always better
2. **Ignoring OPCache** - Missing the biggest performance win
3. **Testing only homepage** - Different pages have different resource needs
4. **Production changes without testing** - Always test configuration changes
5. **Not monitoring after changes** - Performance can degrade over time

## Resources

- [Symfony OPCache Recommendations](https://symfony.com/doc/current/performance.html#performance-configure-opcache)
- [PHP-FPM Process Manager Documentation](https://www.php.net/manual/en/install.fpm.configuration.php)
- [PHP Performance Benchmarking Tools](https://github.com/kosinix/php-benchmark-script)
