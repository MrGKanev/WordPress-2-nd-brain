# Plugin Recommendations

## Overview

Plugin selection significantly impacts WordPress performance, security, and maintainability. This section outlines key considerations and links to topic-specific recommendations throughout the book.

The guiding principle: **fewer plugins, better quality**. A plugin can be 2 lines of efficient code or a massive resource hog. Quantity matters less than whether each plugin earns its place.

## Topic-Specific Recommendations

Plugins are covered within their relevant topic areas:

| Topic | Location | Examples |
|-------|----------|----------|
| Image optimization | [Image Optimizations](../04-performance/06-image-optimizations.md) | ShortPixel, EWWW, Converter for Media |
| Database maintenance | [Database Optimization](../04-performance/07-database-optimizations.md) | WP-Sweep, Index WP MySQL For Speed |
| Caching | [PHP Optimization](../04-performance/02-php-optimization.md) | Redis Object Cache, LiteSpeed Cache |
| Security | [Server Hardening](../03-security/02-server-hardening.md) | Two-Factor, Simple Cloudflare Turnstile |
| SEO | [Technical SEO](../05-seo/01-technical-seo-fundamentals.md) | Rank Math, Slim SEO, SEOPress |
| WooCommerce | [WooCommerce Performance](../06-e-commerce/03-woocommerce-performance.md) | Disable Cart Fragments, Product filters |
| Debugging | [Debugging & Profiling](../04-performance/10-debugging-profiling.md) | Query Monitor, Code Profiler |

## Essential Plugins by Role

### Every WordPress Site

| Plugin | Purpose | Why Essential |
|--------|---------|---------------|
| [Query Monitor](https://wordpress.org/plugins/query-monitor/) | Debugging | Understand what's slowing your site |
| Backup solution | Recovery | UpdraftPlus, WPvivid, or host backups |
| Object cache | Performance | Redis Object Cache (if Redis available) |

### Content-Heavy Sites

| Plugin | Purpose |
|--------|---------|
| [Safe SVG](https://wordpress.org/plugins/safe-svg/) | Secure SVG uploads |
| [Enable Media Replace](https://wordpress.org/plugins/enable-media-replace/) | Update images without changing URLs |
| [Media Cleaner](https://wordpress.org/plugins/media-cleaner/) | Remove unused media |

### Developer Sites

| Plugin | Purpose |
|--------|---------|
| [Code Snippets](https://wordpress.org/plugins/code-snippets/) | Manage custom PHP without theme editing |
| [ACF](https://wordpress.org/plugins/advanced-custom-fields/) or Meta Box | Custom fields |
| [Custom Post Type UI](https://wordpress.org/plugins/custom-post-type-ui/) | Register post types without code |

### Client Sites

| Plugin | Purpose |
|--------|---------|
| [Admin and Site Enhancements](https://wordpress.org/plugins/admin-site-enhancements/) | Simplify admin, hide clutter |
| [Simple History](https://wordpress.org/plugins/simple-history/) | Track user changes |
| [LoginWP](https://wordpress.org/plugins/peter-login-redirect/) | Role-based login redirects |

## Plugins to Avoid

### Heavy Security Plugins

Plugins like Wordfence scan every request through PHP. Server-level security (Cloudflare, Nginx rules) provides better protection with less overhead. See [Server Hardening](../03-security/02-server-hardening.md).

### Bloated All-in-One Solutions

Plugins that do "everything" usually mean:
- 90% of features unused
- Higher attack surface
- Performance overhead from unused code
- Settings complexity

Choose focused plugins that do one thing well.

### Outdated or Abandoned Plugins

WordPress and its ecosystem evolve rapidly. Core updates, PHP version changes, and major plugin updates (especially WooCommerce) can break plugins that haven't kept pace. While there are exceptions—simple plugins that do one thing may not need frequent updates—the risk grows with complexity.

**The HPOS Example**: When WooCommerce introduced High-Performance Order Storage (HPOS), many popular plugins that integrated with orders weren't updated in time. Sites that enabled HPOS found major functionality broken—order management, reporting, shipping integrations. Even well-established plugins with hundreds of thousands of installs caused problems because they weren't updated for this architectural change.

This pattern repeats with every major change: Gutenberg's introduction broke page builders, PHP 8 compatibility issues affected countless plugins, and WooCommerce's block-based checkout continues to cause integration issues.

**Check before installing:**

- **Last updated**: Within 6-12 months ideally, 18 months maximum
- **Support forum**: Active responses to issues
- **Compatibility**: Tested with your WordPress and WooCommerce versions
- **Changelog**: Shows awareness of ecosystem changes (HPOS support, PHP 8 compatibility, etc.)

**For WooCommerce integrations specifically**, verify HPOS compatibility before installing. Check the plugin's documentation or support forum for "HPOS", "High-Performance Order Storage", or "Custom Order Tables" mentions.

## Plugin Selection Criteria

When evaluating any plugin:

| Factor | What to Check |
|--------|---------------|
| **Necessity** | Can this be done without a plugin? |
| **Reputation** | Active installations, reviews, known developer |
| **Performance** | Does Query Monitor show impact? |
| **Updates** | Regular maintenance, security patches |
| **Alternatives** | Are there lighter options? |
| **Exit strategy** | Can you remove it without breaking the site? |

## Plugin Audit Process

Quarterly, review installed plugins:

1. **Is it still needed?** Remove if not actively used
2. **Is it still maintained?** Check for updates and support activity
3. **Is there a better option?** Ecosystem evolves constantly
4. **Does it conflict?** Multiple plugins doing similar things cause issues

## Implementation Strategy

1. **Start minimal** - Add plugins only when necessary
2. **Test impact** - Use Query Monitor before and after
3. **Document why** - Note why each plugin was added
4. **Audit regularly** - Review quarterly

> **Expert insight**: "It's all about the plugins themselves. A plugin can be 2 lines of code, or a huge monster like WooCommerce. Or it can also be 2 lines of code that are anything but efficient. So it's not about the quantity, but the quality."

## Further Reading

- [Hosting Selection](./02-hosting-selection.md) - Host-provided functionality vs plugins
- [Performance Optimization](../04-performance/README.md) - Measuring plugin impact
