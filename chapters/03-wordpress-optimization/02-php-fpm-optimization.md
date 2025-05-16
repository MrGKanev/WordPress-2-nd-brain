# PHP-FPM Optimization for Low-Resource VPS

## Overview

PHP-FPM (FastCGI Process Manager) is critical for WordPress performance on VPS environments. Proper tuning of PHP-FPM can dramatically reduce resource usage and improve response times, especially on limited hardware like 2-core VPS setups.

## Process Manager Selection

PHP-FPM offers three process management methods:

| Mode | Description | Best For |
|------|-------------|----------|
| `static` | Fixed number of child processes | High-traffic, consistent load sites |
| `dynamic` | Processes vary between min/max settings | Medium traffic, variable load |
| `ondemand` | Processes start only when needed | Low-traffic sites, conserving resources |

### ondemand Configuration

For a 2-core VPS with 4GB RAM (like in the case study), the `ondemand` process manager is ideal:

```ini
; Set in /etc/php/8.x/fpm/pool.d/www.conf
pm = ondemand
pm.max_children = 12
pm.process_idle_timeout = 30s
pm.max_requests = 500
```

## Calculating Optimal pm.max_children

The most critical setting is `pm.max_children`. Calculate this based on:

```
pm.max_children = Total RAM / Maximum PHP process size
```

For WordPress sites:

- Average PHP process: ~50-100MB
- With object caching: ~30-50MB
- High complexity sites: ~100-150MB

### Example Calculation

For a 4GB VPS running WordPress with database and web server:

1. Reserve ~1.5GB for OS, MySQL, Nginx: 4GB - 1.5GB = 2.5GB for PHP
2. Estimate ~100MB per PHP process: 2.5GB ÷ 100MB = 25 processes
3. Add safety margin: 25 × 0.8 = 20 processes max

For a 2-core VPS, you may want to further limit this number based on CPU constraints.

## Timeout Settings

Adjust these timeout settings for better performance:

```ini
; Process idle timeout (how long a process sits idle before terminating)
pm.process_idle_timeout = 30s

; Max execution time for PHP scripts
max_execution_time = 60

; Max time to receive input from client
max_input_time = 60

; Request termination timeout
request_terminate_timeout = 300
```

## Max Requests Setting

The `pm.max_requests` setting controls how many requests a child process handles before recycling:

```ini
; Recycle processes after 500 requests to prevent memory leaks
pm.max_requests = 500
```

Lower values (e.g., 200-500) help prevent memory leaks but cause more frequent process recycling. Higher values (1000+) reduce process recycling overhead but may allow memory leaks to grow.

## PHP Version Considerations

Always use the latest stable PHP version:

- PHP 8.1+ provides significant performance improvements over PHP 7.x
- PHP 8.2+ offers further optimizations for WordPress

The case study used PHP 8.2 with FPM for optimal performance.

## PHP OPCache Configuration

Enable and optimize OPCache for significant performance gains:

```ini
[opcache]
opcache.enable=1
opcache.memory_consumption=128
opcache.interned_strings_buffer=8
opcache.max_accelerated_files=10000
opcache.revalidate_freq=60
opcache.save_comments=1
opcache.enable_file_override=1
opcache.validate_timestamps=1
```

## Implementation Steps

1. Edit your PHP-FPM pool configuration:
   - Ubuntu/Debian: `/etc/php/8.x/fpm/pool.d/www.conf`
   - CentOS/RHEL: `/etc/php-fpm.d/www.conf`

2. After making changes, restart PHP-FPM:

   ```bash
   sudo systemctl restart php8.x-fpm
   ```

3. Monitor resource usage to validate changes.

## Monitoring PHP-FPM

Monitor PHP-FPM performance with:

```bash
# Check current PHP-FPM processes
ps aux | grep php-fpm

# Monitor PHP-FPM pool status (if status page enabled)
curl -s 127.0.0.1/status?full

# Check PHP-FPM error log
tail -f /var/log/php8.x-fpm.log
```

## Common Pitfalls

- Setting `pm.max_children` too high, causing memory exhaustion
- Using `static` mode on low-resource VPS, wasting resources
- Setting timeouts too high, allowing runaway processes
- Not monitoring PHP-FPM metrics after changes

## Resources

- [PHP-FPM Best Practices and Calculator](https://php-fpm.gkanev.com/) (useful for tuning settings, and I'm the author)
- [PHP-FPM Configuration Documentation](https://www.php.net/manual/en/install.fpm.configuration.php)
- [Calculating PHP-FPM Processes](https://myshell.co.uk/blog/2012/07/adjusting-child-processes-for-php-fpm-nginx/)