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

### Migration Performance Gains

PHP version upgrades provide substantial performance improvements without code changes:

| Migration Path | Performance Gain | Notes |
|----------------|------------------|-------|
| PHP 5.6 → 7.0 | 2x faster | Major engine rewrite |
| PHP 7.0 → 7.4 | 30-50% faster | Continuous optimization |
| PHP 7.4 → 8.0 | 10-20% faster | JIT compiler (limited WordPress benefit) |
| PHP 8.0 → 8.2 | 5-10% faster | Memory optimizations |

**Key insight:** Migrating from PHP 5.6 to 7.4+ allows serving **3x more concurrent requests** with the same hardware.

### JIT Compiler (PHP 8.0+)

PHP 8.0 introduced Just-In-Time compilation. For WordPress specifically:

- **Typical WordPress benefit:** ~5% improvement
- **Computation-heavy plugins:** More significant gains
- **Why limited:** WordPress is I/O-bound (database, file operations), not CPU-bound

**Enable JIT (optional):**

```ini
; php.ini - JIT configuration
opcache.jit_buffer_size=100M
opcache.jit=1255
```

For most WordPress sites, the complexity isn't worth the marginal gain. Focus on OPcache and PHP-FPM tuning instead.

### Checking PHP Compatibility Before Upgrade

Before upgrading production:

```bash
# Using PHP Compatibility Checker plugin
wp plugin install php-compatibility-checker --activate
# Run scan from admin panel

# Or via command line with PHPCS
phpcs -p --standard=PHPCompatibilityWP --runtime-set testVersion 8.2 wp-content/themes/yourtheme/
```

**Resources:**
- [php.watch](https://php.watch/) - Version-specific migration guides
- [PHPCompatibilityWP](https://github.com/PHPCompatibility/PHPCompatibilityWP) - WordPress-specific ruleset

### Enabling OPCache

Check if OPCache is available:

```bash
php -v
# Look for: with Zend OPcache v8.2.8, Copyright (c), by Zend Technologies
```

Check if enabled:

```bash
php -i | grep opcache
# Look for: opcache.enable => On => On
```

Enable OPCache in php.ini:

```ini
[opcache]
opcache.enable=1
opcache.memory_consumption=256
opcache.interned_strings_buffer=16
opcache.max_accelerated_files=20000
opcache.revalidate_freq=0
opcache.validate_timestamps=0
opcache.save_comments=1
opcache.enable_file_override=1
```

### WordPress-Specific OPCache Settings

For WordPress installations, these settings provide optimal performance:

```ini
; Increase max_accelerated_files to handle WordPress + plugins + themes
opcache.max_accelerated_files=20000

; For production, disable timestamp validation for maximum performance
opcache.validate_timestamps=0
opcache.revalidate_freq=0

; For development, enable validation to see changes immediately
; opcache.validate_timestamps=1
; opcache.revalidate_freq=2
```

**Important:** Always reload PHP-FPM after changes:

```bash
sudo systemctl reload php8.2-fpm
```

### Persistent OPcache (File Cache)

By default, OPcache stores compiled opcodes in shared memory. When PHP restarts (server reboot, PHP-FPM reload), the cache is lost and must be rebuilt—causing slow responses during warm-up.

**Solution:** Enable file-based cache for persistence:

```ini
; Store opcodes on disk for survival across restarts
opcache.file_cache=/var/cache/php/opcache
opcache.file_cache_only=0
opcache.file_cache_consistency_checks=1
```

**Setup:**

```bash
# Create cache directory with proper permissions
sudo mkdir -p /var/cache/php/opcache
sudo chown www-data:www-data /var/cache/php/opcache
sudo chmod 755 /var/cache/php/opcache
```

**How it works:**
- `file_cache_only=0` - Use shared memory as primary, file as backup
- `file_cache_only=1` - Use file cache only (useful for shared hosting)
- On restart, opcodes load from disk instantly instead of recompiling

**Production recommendation:**

```ini
; Production OPcache with file persistence
opcache.enable=1
opcache.memory_consumption=256
opcache.interned_strings_buffer=16
opcache.max_accelerated_files=20000
opcache.validate_timestamps=0
opcache.revalidate_freq=0
opcache.file_cache=/var/cache/php/opcache
opcache.file_cache_only=0
opcache.save_comments=1
opcache.enable_file_override=1
```

### OPcache Preloading (PHP 7.4+)

Preloading compiles specified files at server startup, keeping them permanently in memory:

```php
// preload.php
<?php
// Preload WordPress core files
$files = [
    ABSPATH . 'wp-includes/class-wp.php',
    ABSPATH . 'wp-includes/class-wp-query.php',
    ABSPATH . 'wp-includes/formatting.php',
    ABSPATH . 'wp-includes/plugin.php',
];

foreach ($files as $file) {
    if (file_exists($file)) {
        opcache_compile_file($file);
    }
}
```

```ini
; php.ini
opcache.preload=/var/www/html/preload.php
opcache.preload_user=www-data
```

**Caution:** Preloading is complex with WordPress due to dynamic plugin loading. Test thoroughly before production use. For most sites, standard OPcache with file persistence is sufficient.

### Invalidating OPcache After Deployments

When `validate_timestamps=0`, PHP won't detect file changes. Clear cache after deployments:

```bash
# Via PHP-FPM reload (clears shared memory cache)
sudo systemctl reload php8.2-fpm

# Via WP-CLI (if using a cache plugin with OPcache support)
wp cache flush

# Via PHP script
php -r "opcache_reset();"

# Via curl to a cache-clear endpoint
curl -X POST https://yoursite.com/clear-opcache.php
```

**Deployment script example:**

```bash
#!/bin/bash
# deploy.sh
git pull origin main
composer install --no-dev
sudo systemctl reload php8.2-fpm  # Clear OPcache
```

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
