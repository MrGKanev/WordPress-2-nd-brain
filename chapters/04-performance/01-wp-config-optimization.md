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

### Autosave and Trash Settings

```php
// Increase autosave interval (default: 60 seconds)
// Reduces AJAX calls and database writes during editing
define('AUTOSAVE_INTERVAL', 120);

// Days before trashed items are permanently deleted (default: 30)
// Lower values reduce database bloat from deleted content
define('EMPTY_TRASH_DAYS', 14);

// Disable trash entirely (items deleted immediately)
// define('EMPTY_TRASH_DAYS', 0);
```

### Database Connection Optimization

```php
// Use IP address instead of 'localhost' for faster connection
// Why? When you use 'localhost', PHP tries to connect via Unix socket first,
// then falls back to TCP if that fails. This detection takes time.
// Using '127.0.0.1' tells PHP to use TCP directly, avoiding the overhead.
// On some servers this saves 10-50ms per database connection.
define('DB_HOST', '127.0.0.1');

// Database charset and collation (usually set correctly by installer)
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');

// Custom database table prefix for security
$table_prefix = 'wp_xyz_';

// Enable database repair mode (only when needed, then disable)
// define('WP_ALLOW_REPAIR', true);
```

### Environment Type (WordPress 5.5+)

```php
// Set environment type for environment-aware behavior
// Values: 'local', 'development', 'staging', 'production'
define('WP_ENVIRONMENT_TYPE', 'production');
```

Plugins and themes can use `wp_get_environment_type()` to adjust behavior per environment.

### URL and Path Configuration

```php
// Override site URLs (useful for migrations)
// Remove these after migration is complete
define('WP_HOME', 'https://example.com');
define('WP_SITEURL', 'https://example.com');

// Custom content directory (if restructuring WordPress)
define('WP_CONTENT_DIR', dirname(__FILE__) . '/content');
define('WP_CONTENT_URL', 'https://example.com/content');

// Custom plugin directory
define('WP_PLUGIN_DIR', dirname(__FILE__) . '/content/plugins');
define('WP_PLUGIN_URL', 'https://example.com/content/plugins');

// Custom uploads directory (relative to ABSPATH)
define('UPLOADS', 'wp-content/uploads');
```

### SSL and HTTPS

```php
// Force SSL for admin area
define('FORCE_SSL_ADMIN', true);

// Fix SSL detection behind load balancer or reverse proxy
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) &&
    $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}

// Alternative: Trust X-Forwarded headers
if (isset($_SERVER['HTTP_X_FORWARDED_HOST'])) {
    $_SERVER['HTTP_HOST'] = $_SERVER['HTTP_X_FORWARDED_HOST'];
}
```

### Cache Configuration

```php
// Enable WordPress object cache
define('WP_CACHE', true);

// Cache key salt (prevents collisions when sharing Redis/Memcached)
define('WP_CACHE_KEY_SALT', 'mysite_prod_');

// Redis-specific configuration
define('WP_REDIS_HOST', '127.0.0.1');
define('WP_REDIS_PORT', 6379);
define('WP_REDIS_DATABASE', 0);  // 0-15, use different numbers per site

// Graceful fallback if Redis is unavailable
define('WP_REDIS_GRACEFUL', true);
```

### Cookie Settings

```php
// Custom cookie domain (useful for subdomains)
define('COOKIE_DOMAIN', '.example.com');

// Custom cookie path
define('COOKIEPATH', '/');
define('SITECOOKIEPATH', '/');

// Cookie names customization
define('USER_COOKIE', 'wp_user_' . COOKIEHASH);
define('PASS_COOKIE', 'wp_pass_' . COOKIEHASH);
define('AUTH_COOKIE', 'wp_auth_' . COOKIEHASH);
define('SECURE_AUTH_COOKIE', 'wp_sec_' . COOKIEHASH);
define('LOGGED_IN_COOKIE', 'wp_logged_in_' . COOKIEHASH);
```

### Filesystem Method

```php
// Force direct filesystem access (faster than FTP)
// Use when WordPress can write to the filesystem directly
define('FS_METHOD', 'direct');

// Alternative: SSH2 (requires SSH extension)
// define('FS_METHOD', 'ssh2');

// FTP credentials (for restricted hosting)
// define('FTP_USER', 'username');
// define('FTP_PASS', 'password');
// define('FTP_HOST', 'ftp.example.com');
```

### Multisite Constants

For WordPress Multisite installations:

```php
// Enable Multisite
define('WP_ALLOW_MULTISITE', true);

// After network setup, these are required
define('MULTISITE', true);
define('SUBDOMAIN_INSTALL', false);  // true for subdomain, false for subdirectory
define('DOMAIN_CURRENT_SITE', 'example.com');
define('PATH_CURRENT_SITE', '/');
define('SITE_ID_CURRENT_SITE', 1);
define('BLOG_ID_CURRENT_SITE', 1);
```

## Complete Production Configuration Example

```php
<?php
// Database
define('DB_NAME', 'wordpress');
define('DB_USER', 'wp_user');
define('DB_PASSWORD', 'secure_password_here');
define('DB_HOST', '127.0.0.1');
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');
$table_prefix = 'wp_';

// Security Keys (generate at api.wordpress.org/secret-key/1.1/salt/)
define('AUTH_KEY',         'your-unique-phrase');
define('SECURE_AUTH_KEY',  'your-unique-phrase');
define('LOGGED_IN_KEY',    'your-unique-phrase');
define('NONCE_KEY',        'your-unique-phrase');
define('AUTH_SALT',        'your-unique-phrase');
define('SECURE_AUTH_SALT', 'your-unique-phrase');
define('LOGGED_IN_SALT',   'your-unique-phrase');
define('NONCE_SALT',       'your-unique-phrase');

// Performance
define('WP_MEMORY_LIMIT', '256M');
define('WP_MAX_MEMORY_LIMIT', '384M');
define('WP_POST_REVISIONS', 5);
define('AUTOSAVE_INTERVAL', 120);
define('EMPTY_TRASH_DAYS', 14);
define('DISABLE_WP_CRON', true);

// Caching
define('WP_CACHE', true);
define('WP_CACHE_KEY_SALT', 'mysite_');

// Security
define('DISALLOW_FILE_EDIT', true);
define('FORCE_SSL_ADMIN', true);
define('FS_METHOD', 'direct');

// Environment
define('WP_ENVIRONMENT_TYPE', 'production');
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);

// SSL behind load balancer
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) &&
    $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}

// WordPress paths
if (!defined('ABSPATH')) {
    define('ABSPATH', dirname(__FILE__) . '/');
}

require_once ABSPATH . 'wp-settings.php';
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
