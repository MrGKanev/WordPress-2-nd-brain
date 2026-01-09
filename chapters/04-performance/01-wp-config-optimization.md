# WP-Config.php Optimization

## Overview

The `wp-config.php` file controls critical WordPress settings that can significantly impact performance environments. Proper configuration can dramatically reduce resource usage, especially on limited hardware like 2-core VPS setups.

## Essential Optimizations

### Memory Management

```php
// Increase PHP memory limit for WordPress
// For a 2GB RAM VPS, 256M is typically safe
// For a 4GB RAM VPS, 384M-512M may be appropriate
define('WP_MEMORY_LIMIT', '256M');

// Increase memory for admin operations, which are more resource-intensive
define('WP_MAX_MEMORY_LIMIT', '384M');
```

### Post Revision Control

```php
// Limit post revisions to reduce database bloat
// 5 is a good balance between usability and performance
define('WP_POST_REVISIONS', 5);

// Or disable revisions entirely (not recommended for content-heavy sites)
// define('WP_POST_REVISIONS', false);
```

### Disable Automatic Updates

For VPS environments where you manage updates manually:

```php
// Disable core auto-updates
define('AUTOMATIC_UPDATER_DISABLED', true);

// Disable theme/plugin auto-updates
define('WP_AUTO_UPDATE_CORE', false);
```

### Cron Optimization

```php
// Disable WordPress cron and use system cron instead
// This prevents random visitor-triggered cron processes
define('DISABLE_WP_CRON', true);
```

### Debug Settings for Production

```php
// Disable debug for production
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);

// Disable concatenation of admin scripts
define('CONCATENATE_SCRIPTS', false);
```

### Security Enhancements

```php
// Disable file editing in admin
define('DISALLOW_FILE_EDIT', true);

// Disable plugin and theme installation/updates
define('DISALLOW_FILE_MODS', true);

// Set custom auth keys and salts (generate at WordPress.org)
define('AUTH_KEY',         'unique-value-here');
define('SECURE_AUTH_KEY',  'unique-value-here');
define('LOGGED_IN_KEY',    'unique-value-here');
define('NONCE_KEY',        'unique-value-here');
define('AUTH_SALT',        'unique-value-here');
define('SECURE_AUTH_SALT', 'unique-value-here');
define('LOGGED_IN_SALT',   'unique-value-here');
define('NONCE_SALT',       'unique-value-here');
```

## Common Pitfalls

### Leftover Configurations

When migrating from managed hosting like SiteGround, GoDaddy, or Bluehost, make sure to:

1. Remove any host-specific include statements
2. Check for and remove cached paths pointing to old host
3. Update any hardcoded URLs or paths

### Memory Overallocation

Setting memory limits too high on a VPS can lead to:

- Server-wide memory exhaustion
- PHP-FPM process termination
- Unexpected 503 errors

For a 2-core/4GB VPS, keep WP_MEMORY_LIMIT under 384M to leave resources for the OS and other services.

## Implementation Steps

1. Always back up your original wp-config.php file
2. Make one change at a time, testing between changes
3. Monitor server load after modifications
4. If using Redis object cache, add the appropriate Redis configuration
