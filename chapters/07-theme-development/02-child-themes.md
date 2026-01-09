# Child Themes

## Overview

A child theme inherits functionality from a parent theme while allowing customizations. Updates to the parent don't overwrite your changes. This is the recommended approach for customizing any third-party theme.

## Why Use Child Themes

| Direct Theme Modification | Child Theme |
|--------------------------|-------------|
| Changes lost on update | Changes preserved |
| No version control separation | Clean separation of customizations |
| Hard to track what changed | Only your changes exist in child |
| Can't easily revert | Parent intact as fallback |

**Use a child theme when:**
- Customizing any theme you didn't build
- Making template overrides
- Adding theme-specific functions
- Client projects using commercial themes

**Skip child theme when:**
- Building a theme from scratch
- Making plugin-territory changes (use a plugin instead)
- Only adding custom CSS (use Customizer Additional CSS)

## Creating a Child Theme

### Minimum Structure

```
themes/
├── parent-theme/           # Original theme (don't modify)
└── parent-theme-child/     # Your child theme
    ├── style.css           # Required: theme header
    └── functions.php       # Required: enqueue parent styles
```

### style.css

```css
/*
Theme Name: Parent Theme Child
Theme URI: https://example.com
Description: Child theme for Parent Theme
Author: Your Name
Author URI: https://example.com
Template: parent-theme
Version: 1.0.0
License: GPL-2.0-or-later
License URI: https://www.gnu.org/licenses/gpl-2.0.html
Text Domain: parent-theme-child
*/

/* Custom styles go below */
```

The `Template` line must exactly match the parent theme's folder name.

### functions.php

```php
<?php
/**
 * Child theme functions
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Enqueue parent and child styles
 */
function child_theme_enqueue_styles() {
    // Parent stylesheet
    wp_enqueue_style(
        'parent-style',
        get_template_directory_uri() . '/style.css',
        array(),
        wp_get_theme( 'parent-theme' )->get( 'Version' )
    );

    // Child stylesheet
    wp_enqueue_style(
        'child-style',
        get_stylesheet_uri(),
        array( 'parent-style' ),
        wp_get_theme()->get( 'Version' )
    );
}
add_action( 'wp_enqueue_scripts', 'child_theme_enqueue_styles' );
```

## Key Functions

```php
// Parent theme directory
get_template_directory();       // /themes/parent-theme
get_template_directory_uri();   // https://site.com/wp-content/themes/parent-theme

// Child theme directory (active theme)
get_stylesheet_directory();     // /themes/parent-theme-child
get_stylesheet_directory_uri(); // https://site.com/wp-content/themes/parent-theme-child

// In parent, these are identical
// In child, stylesheet functions return child paths
```

## Overriding Templates

### Complete Override

Copy the template file from parent to child with the same path:

```
parent-theme/
└── single.php              # Parent version

parent-theme-child/
└── single.php              # Your version (completely replaces parent)
```

WordPress loads the child's version instead of the parent's.

### Template Hierarchy Still Applies

```
parent-theme-child/
├── single-product.php      # Used for products
└── single.php              # Fallback for other singles
```

If child doesn't have a template, WordPress checks parent, then falls back to index.php.

### Subfolder Templates

Match the exact path:

```
parent-theme/
└── template-parts/
    └── content.php

parent-theme-child/
└── template-parts/
    └── content.php         # Overrides parent's version
```

### WooCommerce Templates

WooCommerce follows a specific override pattern:

```
parent-theme-child/
└── woocommerce/
    ├── single-product.php
    └── cart/
        └── cart.php
```

## Overriding Functions

### Pluggable Functions

Well-designed parent themes wrap functions in `function_exists()`:

```php
// In parent theme
if ( ! function_exists( 'parent_theme_setup' ) ) {
    function parent_theme_setup() {
        // Default setup
    }
}

// In child theme - your version runs instead
function parent_theme_setup() {
    // Your custom setup
}
```

### Hook Priority

Override by using higher priority:

```php
// Parent theme (priority 10, default)
add_action( 'wp_head', 'parent_add_meta', 10 );

// Child theme - remove parent's, add yours
remove_action( 'wp_head', 'parent_add_meta', 10 );
add_action( 'wp_head', 'child_add_meta', 10 );
```

### Removing Parent Actions

Must match exact function name and priority:

```php
// This works
add_action( 'after_setup_theme', 'remove_parent_features', 20 );
function remove_parent_features() {
    remove_action( 'wp_head', 'parent_function', 10 );
}

// This fails (wrong priority)
remove_action( 'wp_head', 'parent_function' ); // Assumes priority 10
```

For class methods:

```php
// Parent registers like this:
add_action( 'init', array( $this, 'some_method' ) );

// Child must remove with exact reference
global $parent_class_instance;
remove_action( 'init', array( $parent_class_instance, 'some_method' ) );
```

## Overriding Styles

### Order Matters

```php
function child_enqueue_styles() {
    // Parent first
    wp_enqueue_style( 'parent', get_template_directory_uri() . '/style.css' );

    // Child after (loads second, can override)
    wp_enqueue_style( 'child', get_stylesheet_uri(), array( 'parent' ) );
}
```

### Specificity

Child CSS needs equal or higher specificity:

```css
/* Parent */
.site-header .main-navigation a {
    color: blue;
}

/* Child - same specificity, loads later, wins */
.site-header .main-navigation a {
    color: red;
}

/* Or increase specificity */
body .site-header .main-navigation a {
    color: red;
}
```

### Targeting Parent Styles

Inspect element to find exact selectors the parent uses.

## Extended Child Theme Structure

```
parent-theme-child/
├── style.css
├── functions.php
├── screenshot.png              # Custom preview image
├── header.php                  # Override header
├── footer.php                  # Override footer
├── single.php                  # Override single posts
├── page-contact.php            # Template for contact page
├── template-parts/
│   └── content.php             # Override content partial
├── inc/
│   ├── customizer.php          # Additional Customizer options
│   └── template-functions.php  # Helper functions
├── assets/
│   ├── css/
│   │   └── custom.css
│   └── js/
│       └── custom.js
└── languages/
    └── parent-theme-child.pot
```

## Common Patterns

### Adding Custom Post Type Templates

```php
// In child functions.php
function child_custom_templates( $templates ) {
    $templates['template-portfolio.php'] = 'Portfolio Layout';
    return $templates;
}
add_filter( 'theme_page_templates', 'child_custom_templates' );
```

### Modifying Parent Theme Options

```php
// Modify parent's color palette
function child_modify_colors() {
    add_theme_support( 'editor-color-palette', array(
        array(
            'name'  => 'Brand Primary',
            'slug'  => 'primary',
            'color' => '#ff6600',  // Your client's color
        ),
    ) );
}
add_action( 'after_setup_theme', 'child_modify_colors', 20 );
```

### Adding Widget Areas

```php
function child_widgets_init() {
    register_sidebar( array(
        'name'          => 'Child Footer Widget',
        'id'            => 'child-footer-widget',
        'before_widget' => '<div class="widget">',
        'after_widget'  => '</div>',
    ) );
}
add_action( 'widgets_init', 'child_widgets_init' );
```

## Common Pitfalls

### 1. Wrong Template Name

```css
/* Wrong - Template must match folder name exactly */
Template: Parent Theme

/* Correct */
Template: parent-theme
```

### 2. Not Enqueueing Parent Styles

```php
// Wrong - parent styles missing
function child_styles() {
    wp_enqueue_style( 'child', get_stylesheet_uri() );
}

// Correct - enqueue parent first
function child_styles() {
    wp_enqueue_style( 'parent', get_template_directory_uri() . '/style.css' );
    wp_enqueue_style( 'child', get_stylesheet_uri(), array( 'parent' ) );
}
```

### 3. Using @import (Slow)

```css
/* Bad - blocks rendering */
@import url("../parent-theme/style.css");

/* Good - enqueue in PHP */
```

### 4. Hardcoding Parent Paths

```php
// Wrong - breaks if parent folder renamed
include '/parent-theme/inc/file.php';

// Correct
include get_template_directory() . '/inc/file.php';
```

### 5. Not Handling Parent Updates

Parent updates might:
- Change function names (breaks your remove_action)
- Restructure templates (your override looks wrong)
- Add new features (you might want)

**Solution:** Keep child changes minimal and document what you modified.

## Debugging Child Themes

### Template Loading

```php
// In child functions.php
add_action( 'wp_head', function() {
    if ( ! current_user_can( 'manage_options' ) ) return;

    global $template;
    echo '<!-- Template: ' . str_replace( ABSPATH, '', $template ) . ' -->';
} );
```

### Check Which Theme Files Load

Use Query Monitor plugin - shows exact template hierarchy and which file was used.

### Stylesheet Load Order

Browser DevTools → Network tab → filter CSS → check load order.

## Child Themes with Block Themes

Block themes work similarly:

```
parent-block-theme-child/
├── style.css           # Same header format
├── theme.json          # Extends/overrides parent settings
└── templates/
    └── single.html     # Override template
```

**theme.json in child:**

```json
{
    "$schema": "https://schemas.wp.org/trunk/theme.json",
    "version": 2,
    "settings": {
        "color": {
            "palette": [
                {
                    "slug": "primary",
                    "color": "#ff6600",
                    "name": "Primary"
                }
            ]
        }
    }
}
```

Child theme.json merges with parent's, allowing selective overrides.

## Further Reading

- [Template Hierarchy](./01-template-hierarchy.md) - Understanding which templates load
- [Block Themes](./03-block-themes.md) - Child themes in FSE context
- [WordPress Child Theme Handbook](https://developer.wordpress.org/themes/advanced-topics/child-themes/) - Official documentation
