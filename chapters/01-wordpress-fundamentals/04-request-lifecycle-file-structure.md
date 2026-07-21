# WordPress Request Lifecycle & File Structure

Understanding the request lifecycle makes debugging less mysterious. A page is not rendered by one template file; WordPress loads configuration, plugins, the active theme and queried content in a defined order.

## Request Lifecycle

```text
Web server → wp-config.php → wp-settings.php → plugins/mu-plugins
  → parse request and query → template resolution → theme output → response
```

At a high level, the web server routes a request to WordPress; `wp-config.php` provides environment configuration; core loads must-use plugins, normal plugins and the active theme; WordPress builds the main query; and a selected template renders the response. Hooks let themes and plugins change behavior at these stages, so code loaded on every request affects pages even when its visible feature is not used.

## Important Directories

| Path | Purpose | Deployment note |
|------|---------|-----------------|
| `wp-admin/` | Administration code | Managed by WordPress core updates |
| `wp-includes/` | Core libraries | Never edit directly |
| `wp-content/themes/` | Themes | Deploy custom code from version control |
| `wp-content/plugins/` | Standard plugins | Track custom/plugin dependency versions |
| `wp-content/mu-plugins/` | Always-on plugins | Use for required platform controls |
| `wp-content/uploads/` | Media files | Runtime content, not ordinary code |
| `wp-config.php` | Environment configuration | Keep secrets outside version control |

## Debugging with the Lifecycle

Identify the stage before changing code. A wrong URL or 404 suggests rewrite/request parsing. Wrong content often points to the main query. Missing layout suggests template resolution. A slow response can be PHP hooks, database work or an external request.

Do not edit core to test a theory. Use staging, Query Monitor, targeted logging or a temporary must-use plugin, then remove diagnostics after the investigation.

See [Template Hierarchy](../07-theme-development/01-template-hierarchy.md), [Hooks System](../08-plugin-development/02-hooks-system.md) and [Debugging & Profiling Tools](../04-performance/10-debugging-profiling.md).
