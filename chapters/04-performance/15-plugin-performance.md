# Plugin Performance Evaluation

## Overview

Every active plugin adds load time. Some add milliseconds, others add seconds. The difference between a fast WordPress site and a slow one is often just plugin selection. This chapter covers how to measure plugin impact, identify problem plugins, and decide when to replace or remove them.

## The True Cost of Plugins

Plugins affect performance in multiple ways:

| Impact Type | What Happens | When It Hurts |
|-------------|--------------|---------------|
| **PHP execution** | Code runs on every request | Always |
| **Database queries** | Additional SELECT/INSERT/UPDATE | Backend, dynamic pages |
| **HTTP requests** | External API calls | Page load, can block rendering |
| **Frontend assets** | CSS/JS files loaded | Every page (often unnecessarily) |
| **Cron jobs** | Background processing | Server load, affects other requests |
| **Autoloaded options** | Data loaded on every request | Memory usage, init time |

A plugin might be "lightweight" in one dimension but heavy in another. A simple plugin with a single slow database query can be worse than a complex plugin with optimized code.

## Measuring Plugin Impact

### Method 1: Query Monitor

[Query Monitor](https://wordpress.org/plugins/query-monitor/) is the most practical tool for plugin performance analysis.

**Setup:**
1. Install Query Monitor plugin
2. Access your site as an admin
3. Click the Query Monitor panel in the admin bar

**What to check:**

| Panel | What It Shows | Red Flags |
|-------|---------------|-----------|
| **Queries by Component** | Database queries per plugin | Single plugin >50 queries |
| **Queries** | Slow queries highlighted | Any query >0.05s |
| **HTTP API Calls** | External requests | Blocking calls on frontend |
| **Scripts/Styles** | Assets loaded | Unused assets on pages |
| **Hooks & Actions** | Execution time per hook | Single hook >100ms |

### Method 2: Plugin Profiling

Disable plugins systematically to measure their impact.

**Baseline test:**
1. Use a tool like [GTmetrix](https://gtmetrix.com/) or [WebPageTest](https://www.webpagetest.org/)
2. Record TTFB (Time to First Byte) and full load time
3. Document with all plugins active

**Isolation test:**
1. Deactivate one plugin
2. Clear all caches
3. Re-test
4. Compare to baseline
5. Reactivate and repeat for next plugin

This is tedious but reveals true impact. Some plugins only show their cost under specific conditions.

### Method 3: Code Profiling

For deeper analysis, use PHP profilers:

| Tool | Best For | Complexity |
|------|----------|------------|
| [Query Monitor](https://wordpress.org/plugins/query-monitor/) | Quick checks | Low |
| [Debug Bar](https://wordpress.org/plugins/debug-bar/) + extensions | Hook timing | Low |
| [Blackfire](https://www.blackfire.io/) | Production profiling | Medium |
| [New Relic](https://newrelic.com/) | Ongoing monitoring | Medium |
| [Xdebug](https://xdebug.org/) + Profiler | Deep code analysis | High |

### Method 4: WP-CLI Profile

The [WP-CLI profile command](https://developer.wordpress.org/cli/commands/profile/) is a powerful command-line profiling tool:

```bash
# Profile WordPress load time
wp profile stage --all

# Profile specific hook
wp profile hook init

# Profile with specific URL
wp profile stage --url=https://example.com/shop/
```

This shows where time is spent during WordPress initialization. Note: requires the [profile-command package](https://github.com/wp-cli/profile-command) to be installed.

## Common Performance Offenders

Understanding common patterns helps you identify problems faster. These categories cover most plugin performance issues you'll encounter.

### Plugins That Phone Home

"Phoning home" means making external HTTP requests—contacting remote servers for license checks, updates, analytics, or API data. Each request adds latency: DNS lookup, TCP connection, SSL handshake, waiting for response. On a slow external server or unreliable connection, this can add seconds to page load.

The worst offenders make these requests on every frontend page load, not just in the admin. A license check that runs once per admin page is annoying but manageable. The same check running on every visitor request is a performance disaster.

Common culprits:

- License verification checks (premium plugins validating your purchase)
- Update checks (beyond WordPress's built-in update system)
- Analytics/tracking (sending usage data to plugin developers)
- CDN/API connections (fetching remote content or configuration)

**Detection:** Query Monitor → HTTP API Calls panel. Look for requests on frontend page loads. Any external request during a normal visitor page view deserves scrutiny.

**Solutions:**
- Check plugin settings for "check for updates" options
- Use a caching plugin that caches external requests
- Replace with alternatives that don't phone home

### Plugins Loading Assets Everywhere

WordPress's enqueue system makes it easy to add CSS and JavaScript files—perhaps too easy. Many plugin developers take the simple approach: enqueue their assets on every page and let the browser figure it out. This works functionally but wastes bandwidth and slows rendering.

Every CSS file the browser encounters blocks rendering until it downloads and parses. Every JavaScript file (without async/defer) blocks HTML parsing. A plugin adding 50KB of CSS and 100KB of JavaScript to pages that don't use its features adds pure overhead.

The pattern is predictable:

```
Contact form plugin loads on every page
  → Even though form is only on /contact
Slider plugin loads on every page
  → Even though slider is only on homepage
Gallery lightbox loads on every page
  → Even though galleries only exist on portfolio pages
```

**Detection:** Query Monitor → Scripts/Styles panel shows which assets loaded on the current page. Compare what's loaded versus what's actually used. Chrome DevTools' Coverage tab reveals how much of loaded CSS/JS actually executes.

**Solutions:**
- Plugin settings (some offer conditional loading)
- Asset optimization plugins (Asset CleanUp, Perfmatters)
- Custom code to dequeue on specific pages:

```php
add_action('wp_enqueue_scripts', function() {
    if (!is_page('contact')) {
        wp_dequeue_style('contact-form-styles');
        wp_dequeue_script('contact-form-scripts');
    }
}, 100);
```

### WooCommerce Asset Bloat

WooCommerce is a major offender—loading cart fragments, styles, and scripts on every page:

**The cost:** ~15 HTTP requests and ~230KB on pages that have nothing to do with the store.

**Complete removal from non-shop pages:**

```php
add_action('template_redirect', function() {
    // Only run on frontend, non-WC pages
    if (is_admin()) return;
    if (is_woocommerce() || is_cart() || is_checkout() || is_account_page()) return;

    // Remove WooCommerce styles
    remove_action('wp_enqueue_scripts', [WC_Frontend_Scripts::class, 'load_scripts']);
    remove_action('wp_print_scripts', [WC_Frontend_Scripts::class, 'localize_printed_scripts'], 5);
    remove_action('wp_print_footer_scripts', [WC_Frontend_Scripts::class, 'localize_printed_scripts'], 5);

    // Remove cart fragments (AJAX cart updates)
    wp_dequeue_script('wc-cart-fragments');

    // Remove WooCommerce styles
    wp_dequeue_style('woocommerce-general');
    wp_dequeue_style('woocommerce-layout');
    wp_dequeue_style('woocommerce-smallscreen');
});
```

**Note:** If you display products or cart widgets outside the shop, you'll need those assets—test thoroughly.

### Plugin Load Filter

The [Plugin Load Filter](https://wordpress.org/plugins/plugin-load-filter/) plugin provides a UI for conditional plugin loading:

- Disable plugins on specific pages/post types
- Enable plugins only where needed
- Desktop vs mobile differentiation
- REST API and AJAX filtering

This is more maintainable than custom `wp_dequeue` code for complex scenarios.

### Database-Heavy Plugins

Plugins with complex queries that don't use caching:

- Related posts plugins scanning full content
- Popular posts without caching
- Complex filtering/search without indexing
- Statistics plugins tracking everything

**Detection:** Query Monitor → Queries by Component. Sort by time or count.

**Solutions:**
- Enable plugin's built-in caching if available
- Add object caching (Redis/Memcached)
- Replace with lighter alternatives
- For custom queries, add proper indexes

### Autoload Bloat

Plugins storing large data in `wp_options` with `autoload='yes'`:

```sql
-- Find largest autoloaded options
SELECT option_name, LENGTH(option_value) as size
FROM wp_options
WHERE autoload = 'yes'
ORDER BY size DESC
LIMIT 20;
```

Every autoloaded option loads on every request. Large serialized arrays here slow down every page.

**Solutions:**
- Some plugins have settings to reduce stored data
- Use transients instead of options for cached data
- Manually set autoload to 'no' for large options (carefully)

## Decision Framework

When you find a slow plugin, decide what to do:

```
Is the plugin necessary?
├── No → Deactivate and delete
└── Yes → Is there a faster alternative?
    ├── Yes → Test alternative, migrate if better
    └── No → Can it be optimized?
        ├── Settings available → Adjust configuration
        ├── Custom code possible → Conditional loading
        └── No options → Accept cost or build custom solution
```

### Evaluating Alternatives

When comparing plugins for the same function:

| Factor | How to Check |
|--------|--------------|
| **Active installations** | WordPress.org stats |
| **Last updated** | Plugin page (avoid >1 year old) |
| **PHP version support** | Check compatibility |
| **Support responsiveness** | Browse support forum |
| **Code quality** | Check source, reviews mentioning bugs |
| **Performance reviews** | Search "[plugin name] slow" |

### Building Custom Alternatives

Sometimes the best plugin is no plugin. Consider custom code when:

- You need 10% of the plugin's features
- The core function is simple (< 100 lines)
- Plugin overhead exceeds feature value
- You have development resources

Example: Replace a full "maintenance mode" plugin with:

```php
// In mu-plugins/maintenance-mode.php
add_action('template_redirect', function() {
    if (!current_user_can('manage_options') && !is_admin()) {
        wp_die('Site under maintenance', 'Maintenance', ['response' => 503]);
    }
});
```

### SHORTINIT for CLI Scripts

When writing custom CLI scripts or utilities that only need database access, skip the full WordPress load:

```php
<?php
// Ensure CLI only
if (PHP_SAPI !== 'cli') {
    exit('CLI only');
}

// Load minimal WordPress
define('SHORTINIT', true);
require_once dirname(__FILE__) . '/wp-load.php';

// Now you have $wpdb but not themes, plugins, or most of WP
global $wpdb;
$results = $wpdb->get_results("SELECT * FROM {$wpdb->posts} LIMIT 10");
```

**What SHORTINIT provides:**
- Database connection (`$wpdb`)
- Core constants and paths
- Basic error handling

**What SHORTINIT skips:**
- Themes and plugins
- Most hooks and filters
- User authentication
- Full WordPress API

Use for maintenance scripts, data migrations, or anything that just needs database access.

## Performance Testing Workflow

### Before Installing New Plugins

1. **Research first** - Check reviews for performance mentions
2. **Test on staging** - Never test performance on production
3. **Baseline measurement** - Record metrics before installing
4. **Install and activate** - One plugin at a time
5. **Clear caches** - Get clean measurements
6. **Test critical paths** - Homepage, key pages, checkout (if WooCommerce)
7. **Check Query Monitor** - Look for red flags
8. **Compare to baseline** - Acceptable impact?

### Regular Plugin Audits

Schedule quarterly reviews:

1. **List all plugins** - `wp plugin list --status=active`
2. **Check for unused** - Features no longer needed?
3. **Check for duplicates** - Multiple plugins doing similar things?
4. **Update everything** - Performance often improves in updates
5. **Re-test impact** - Has anything changed?
6. **Document decisions** - Why is each plugin there?

## Plugin Categories: Typical Impact

General guidance—individual plugins vary widely:

| Category | Typical Impact | Notes |
|----------|----------------|-------|
| **Security** | Low-Medium | Firewall rules add overhead |
| **SEO** | Low | Usually well-optimized |
| **Caching** | Positive | Whole point is performance |
| **Forms** | Low | Unless loading assets everywhere |
| **Page Builders** | High | See dedicated chapter |
| **WooCommerce** | Medium-High | Complex, many queries |
| **Social Sharing** | Low-Medium | Often load external scripts |
| **Analytics** | Low | Unless blocking |
| **Backup** | Low | Runs in background |
| **Image Optimization** | Low | Runs on upload |

## Further Reading

**Internal:**
- [Debugging & Profiling](./10-debugging-profiling.md) - Deep dive into profiling tools
- [Database Optimization](./07-database-optimizations.md) - Fixing slow queries
- [Frontend Asset Optimization](./13-frontend-asset-optimization.md) - Managing plugin CSS/JS
- [Page Builders & DOM Bloat](./16-page-builders-dom-bloat.md) - Special case of heavy plugins

**External:**
- [Query Monitor](https://querymonitor.com/) - Essential debugging plugin documentation
- [GTmetrix](https://gtmetrix.com/) - Performance testing tool
- [WebPageTest](https://www.webpagetest.org/) - Detailed waterfall analysis
- [WordPress Plugin Directory](https://wordpress.org/plugins/) - Check reviews and "tested up to" versions
- [WPScan Vulnerability Database](https://wpscan.com/plugins) - Check plugin security history
