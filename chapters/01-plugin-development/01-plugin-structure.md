# Plugin Structure

## Overview

Plugin structure determines how maintainable, performant, and extendable your code will be. While WordPress accepts any PHP file with the right header as a plugin, thoughtful organization separates amateur code from professional solutions.

> **Key principle**: Start simple, add structure as needed. A single-file plugin isn't wrong - it's appropriate for simple functionality. Over-engineering a small plugin is as problematic as under-engineering a large one.

## What Makes a WordPress Plugin?

At its simplest, a WordPress plugin is a PHP file with a special comment header. That's it. One file, a few lines of metadata, and you have a working plugin.

```php
<?php
/**
 * Plugin Name: My Plugin
 * Description: What my plugin does
 * Version: 1.0.0
 * Author: Your Name
 */
```

Everything beyond this is organization and best practices.

## The Plugin Header

The header comment isn't just documentation - WordPress parses it to display plugin information in the admin area.

| Field | Required | Purpose |
|-------|----------|---------|
| Plugin Name | Yes | Display name in admin |
| Description | No | Brief explanation shown in plugin list |
| Version | No | Current version number |
| Author | No | Developer name/company |
| Author URI | No | Link to developer website |
| Plugin URI | No | Link to plugin homepage |
| Text Domain | No | For internationalization |
| Requires at least | No | Minimum WordPress version |
| Requires PHP | No | Minimum PHP version |

**Version numbers matter.** WordPress compares versions for update notifications. Use semantic versioning: `MAJOR.MINOR.PATCH` (e.g., 2.1.3).

## Single File vs. Multi-File Plugins

### When Single File Works

A single-file plugin makes sense when:
- The functionality is simple and focused
- There's minimal code (under ~300 lines)
- No admin interface needed
- No assets (CSS, JavaScript, images)

Many useful plugins are single files: adding a shortcode, modifying a behavior, integrating a small feature.

### When to Use Multiple Files

As plugins grow, single files become unwieldy. Split your code when:
- You have separate concerns (admin vs. frontend)
- You need to include assets
- The codebase exceeds a few hundred lines
- Multiple developers will work on it
- You want automated testing

## Recommended Directory Structure

For plugins beyond a single file, this structure balances organization with simplicity:

```
my-plugin/
├── my-plugin.php          # Main plugin file (bootstrap)
├── readme.txt             # WordPress.org readme
├── uninstall.php          # Cleanup on deletion
│
├── includes/              # PHP classes and functions
│   ├── class-plugin.php   # Main plugin class
│   ├── class-admin.php    # Admin functionality
│   └── class-public.php   # Frontend functionality
│
├── admin/                 # Admin-specific assets
│   ├── css/
│   ├── js/
│   └── views/             # Admin page templates
│
├── public/                # Frontend assets
│   ├── css/
│   └── js/
│
├── languages/             # Translation files
│   └── my-plugin.pot
│
└── templates/             # User-overridable templates
```

**Why this structure?**

- **Separation of concerns**: Admin and public code load only where needed
- **Asset organization**: Easy to find and manage CSS/JS
- **Template overrides**: Users can customize output in their theme
- **Internationalization ready**: Languages folder prepared for translations

## The Main Plugin File

The main file should do minimal work - just bootstrap the plugin:

```php
<?php
/**
 * Plugin Name: My Plugin
 * Version: 1.0.0
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define constants
define('MY_PLUGIN_VERSION', '1.0.0');
define('MY_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('MY_PLUGIN_URL', plugin_dir_url(__FILE__));

// Load the main class
require_once MY_PLUGIN_PATH . 'includes/class-plugin.php';

// Initialize
function my_plugin_init() {
    return My_Plugin::instance();
}
my_plugin_init();
```

**Key principles:**

1. **Security check first** - `ABSPATH` check prevents direct file access
2. **Define constants** - Makes paths available throughout plugin
3. **Single entry point** - One place to understand initialization
4. **Delayed initialization** - Use hooks, don't execute on file load

## Plugin Lifecycle

### Activation

Runs once when the plugin is activated. Use for:
- Creating database tables
- Setting default options
- Flushing rewrite rules
- Checking requirements

### Deactivation

Runs when the plugin is deactivated. Use for:
- Temporary cleanup
- Flushing rewrite rules
- Clearing scheduled events

**Important**: Don't delete data on deactivation. Users may reactivate the plugin.

### Uninstallation

Runs when the plugin is deleted (not just deactivated). This is where you clean up:
- Delete options
- Remove database tables
- Clear user meta
- Remove uploaded files

Use `uninstall.php` or `register_uninstall_hook()`. The file approach is preferred as it runs in a clean environment.

## Common Patterns

### The Singleton Pattern

Ensures only one instance of your main class exists. This is common in WordPress plugins because it mirrors how WordPress itself works.

**Controversy**: Some developers argue singletons are an anti-pattern. They make testing harder and hide dependencies. For testable code, consider dependency injection instead.

### Modular Architecture

Split functionality into independent modules that register themselves:
- Each module handles one feature
- Modules can be enabled/disabled independently
- Easier to test and maintain

## File Naming Conventions

WordPress follows naming conventions for files:

| Type | Convention | Example |
|------|-----------|---------|
| Classes | `class-{name}.php` | `class-admin.php` |
| Interfaces | `interface-{name}.php` | `interface-handler.php` |
| Traits | `trait-{name}.php` | `trait-singleton.php` |
| Functions | `functions-{name}.php` | `functions-helpers.php` |
| Templates | `{name}.php` | `single-product.php` |

Classes themselves use underscores and title case: `class My_Plugin_Admin {}`

## Security Considerations

### Prevent Direct Access

Every PHP file should check for WordPress:

```php
defined('ABSPATH') || exit;
```

### File Permissions

- PHP files: 644 (readable by all, writable by owner)
- Directories: 755 (executable by all, writable by owner)
- Never 777 - this is a security risk

### User Capabilities

Always check permissions before performing actions. Never trust that a request comes from an authorized user just because they reached your code.

## Common Mistakes

### Loading Everything Everywhere

**Problem**: Loading admin code on the frontend wastes resources and can expose admin-only functionality.

**Solution**: Check context before loading code. Use `is_admin()` for admin-only code.

### Hardcoding Paths

**Problem**: Using absolute paths that break on different servers.

**Solution**: Use WordPress path functions like `plugin_dir_path()` and `plugin_dir_url()`.

### Not Prefixing

**Problem**: Generic function/class names that conflict with other plugins.

**Solution**: Prefix everything with your plugin name. Use namespaces in modern PHP (7.0+).

### Executing on File Load

**Problem**: Running code when the file loads instead of on appropriate hooks.

**Solution**: Initialize on `plugins_loaded` or later hooks. Let WordPress finish loading first.

## Further Reading

- [Hooks System](./02-hooks-system.md) - How to connect your plugin to WordPress
- [Database Operations](./03-database-operations.md) - Working with custom data
