# Block Themes (Full Site Editing)

## Overview

Block themes represent WordPress's new theme paradigm. Instead of PHP templates, they use HTML files with block markup. The Site Editor replaces the Customizer, allowing visual editing of headers, footers, and templates.

Block themes require WordPress 5.9+ and are the default for new theme development.

## Classic vs. Block Themes

| Aspect | Classic Theme | Block Theme |
|--------|---------------|-------------|
| Templates | PHP files | HTML files |
| Styling control | style.css, Customizer | theme.json, Site Editor |
| Header/Footer | header.php, footer.php | Template parts (HTML) |
| The Loop | PHP while loop | Query Loop block |
| Widgets | Widget areas | Block patterns |
| Menus | wp_nav_menu() | Navigation block |

## Minimum Block Theme

```
my-block-theme/
├── style.css
├── theme.json
├── templates/
│   └── index.html
└── parts/
    ├── header.html
    └── footer.html
```

### style.css

Same format as classic themes:

```css
/*
Theme Name: My Block Theme
Theme URI: https://example.com
Author: Your Name
Description: A minimal block theme.
Version: 1.0.0
Requires at least: 6.0
Tested up to: 6.4
Requires PHP: 7.4
License: GPL-2.0-or-later
Text Domain: my-block-theme
*/
```

### templates/index.html

```html
<!-- wp:template-part {"slug":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main"} -->
<main class="wp-block-group">
    <!-- wp:query -->
    <div class="wp-block-query">
        <!-- wp:post-template -->
            <!-- wp:post-title {"isLink":true} /-->
            <!-- wp:post-excerpt /-->
        <!-- /wp:post-template -->

        <!-- wp:query-pagination -->
            <!-- wp:query-pagination-previous /-->
            <!-- wp:query-pagination-next /-->
        <!-- /wp:query-pagination -->
    </div>
    <!-- /wp:query -->
</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","tagName":"footer"} /-->
```

### parts/header.html

```html
<!-- wp:group {"tagName":"header","className":"site-header"} -->
<header class="wp-block-group site-header">
    <!-- wp:site-title /-->
    <!-- wp:navigation /-->
</header>
<!-- /wp:group -->
```

### parts/footer.html

```html
<!-- wp:group {"tagName":"footer","className":"site-footer"} -->
<footer class="wp-block-group site-footer">
    <!-- wp:paragraph -->
    <p>© 2024 My Site</p>
    <!-- /wp:paragraph -->
</footer>
<!-- /wp:group -->
```

## theme.json

The central configuration file for block themes. Controls:
- Global styles (colors, typography, spacing)
- Block-specific settings
- Layout defaults
- Custom CSS properties

### Basic Structure

```json
{
    "$schema": "https://schemas.wp.org/trunk/theme.json",
    "version": 2,
    "settings": {},
    "styles": {},
    "customTemplates": [],
    "templateParts": [],
    "patterns": []
}
```

### Settings

Define what options are available:

```json
{
    "settings": {
        "appearanceTools": true,
        "color": {
            "palette": [
                {
                    "slug": "primary",
                    "color": "#0073aa",
                    "name": "Primary"
                },
                {
                    "slug": "secondary",
                    "color": "#23282d",
                    "name": "Secondary"
                },
                {
                    "slug": "background",
                    "color": "#ffffff",
                    "name": "Background"
                },
                {
                    "slug": "foreground",
                    "color": "#1a1a1a",
                    "name": "Foreground"
                }
            ],
            "gradients": [],
            "duotone": [],
            "custom": true,
            "customGradient": true,
            "defaultPalette": false
        },
        "typography": {
            "fontFamilies": [
                {
                    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    "slug": "system",
                    "name": "System"
                },
                {
                    "fontFamily": "'Source Serif Pro', Georgia, serif",
                    "slug": "serif",
                    "name": "Serif"
                }
            ],
            "fontSizes": [
                {
                    "slug": "small",
                    "size": "0.875rem",
                    "name": "Small"
                },
                {
                    "slug": "medium",
                    "size": "1rem",
                    "name": "Medium"
                },
                {
                    "slug": "large",
                    "size": "1.5rem",
                    "name": "Large"
                }
            ],
            "customFontSize": true,
            "lineHeight": true,
            "dropCap": false
        },
        "spacing": {
            "units": ["px", "em", "rem", "%", "vw"],
            "padding": true,
            "margin": true,
            "blockGap": true
        },
        "layout": {
            "contentSize": "800px",
            "wideSize": "1200px"
        }
    }
}
```

### Styles

Set default values:

```json
{
    "styles": {
        "color": {
            "background": "var(--wp--preset--color--background)",
            "text": "var(--wp--preset--color--foreground)"
        },
        "typography": {
            "fontFamily": "var(--wp--preset--font-family--system)",
            "fontSize": "var(--wp--preset--font-size--medium)",
            "lineHeight": "1.6"
        },
        "spacing": {
            "blockGap": "1.5rem"
        },
        "elements": {
            "link": {
                "color": {
                    "text": "var(--wp--preset--color--primary)"
                }
            },
            "h1": {
                "typography": {
                    "fontSize": "2.5rem",
                    "fontWeight": "700"
                }
            },
            "h2": {
                "typography": {
                    "fontSize": "2rem"
                }
            }
        },
        "blocks": {
            "core/button": {
                "color": {
                    "background": "var(--wp--preset--color--primary)",
                    "text": "var(--wp--preset--color--background)"
                },
                "border": {
                    "radius": "4px"
                }
            },
            "core/navigation": {
                "typography": {
                    "fontSize": "var(--wp--preset--font-size--small)"
                }
            }
        }
    }
}
```

### Custom Templates

```json
{
    "customTemplates": [
        {
            "name": "blank",
            "title": "Blank",
            "postTypes": ["page", "post"]
        },
        {
            "name": "full-width",
            "title": "Full Width",
            "postTypes": ["page"]
        }
    ]
}
```

Create corresponding files: `templates/blank.html`, `templates/full-width.html`.

### Template Parts

```json
{
    "templateParts": [
        {
            "name": "header",
            "title": "Header",
            "area": "header"
        },
        {
            "name": "footer",
            "title": "Footer",
            "area": "footer"
        },
        {
            "name": "sidebar",
            "title": "Sidebar",
            "area": "uncategorized"
        }
    ]
}
```

## Template Hierarchy

Block themes follow the same hierarchy, but with HTML files:

```
templates/
├── index.html            # Fallback
├── singular.html         # Single content
├── single.html           # Single posts
├── single-post.html      # Posts specifically
├── single-product.html   # Product CPT
├── page.html             # Pages
├── archive.html          # Archives
├── archive-product.html  # Product archive
├── category.html         # Category archives
├── search.html           # Search results
├── 404.html              # Not found
├── front-page.html       # Homepage (static)
└── home.html             # Blog posts page
```

## Common Blocks for Templates

### Query Loop

Replaces the PHP loop:

```html
<!-- wp:query {"queryId":1,"query":{"perPage":10,"postType":"post"}} -->
<div class="wp-block-query">
    <!-- wp:post-template -->
        <!-- wp:post-featured-image /-->
        <!-- wp:post-title {"isLink":true} /-->
        <!-- wp:post-date /-->
        <!-- wp:post-excerpt /-->
    <!-- /wp:post-template -->

    <!-- wp:query-pagination -->
        <!-- wp:query-pagination-previous /-->
        <!-- wp:query-pagination-numbers /-->
        <!-- wp:query-pagination-next /-->
    <!-- /wp:query-pagination -->

    <!-- wp:query-no-results -->
        <!-- wp:paragraph -->
        <p>No posts found.</p>
        <!-- /wp:paragraph -->
    <!-- /wp:query-no-results -->
</div>
<!-- /wp:query -->
```

### Post Content

For single templates:

```html
<!-- wp:post-title /-->
<!-- wp:post-featured-image /-->
<!-- wp:post-content /-->
<!-- wp:post-terms {"term":"category"} /-->
<!-- wp:post-terms {"term":"post_tag"} /-->
<!-- wp:comments /-->
```

### Site Elements

```html
<!-- wp:site-title /-->
<!-- wp:site-tagline /-->
<!-- wp:site-logo /-->
<!-- wp:navigation /-->
```

## CSS Custom Properties

theme.json generates CSS properties:

```css
/* Generated from palette */
--wp--preset--color--primary: #0073aa;
--wp--preset--color--secondary: #23282d;

/* Generated from font sizes */
--wp--preset--font-size--small: 0.875rem;
--wp--preset--font-size--large: 1.5rem;

/* Generated from spacing */
--wp--preset--spacing--20: 0.5rem;
--wp--preset--spacing--40: 1rem;
```

Use in custom CSS:

```css
.my-component {
    color: var(--wp--preset--color--primary);
    font-size: var(--wp--preset--font-size--medium);
    padding: var(--wp--preset--spacing--40);
}
```

## Adding Custom CSS

### Via theme.json

```json
{
    "styles": {
        "css": ".site-header { border-bottom: 1px solid #eee; }"
    }
}
```

### Via style.css

Still works, but loads after theme.json styles:

```css
/* In style.css */
.wp-block-navigation {
    gap: 2rem;
}
```

### Block-specific CSS

```json
{
    "styles": {
        "blocks": {
            "core/quote": {
                "css": "& cite { font-style: normal; }"
            }
        }
    }
}
```

## Block Patterns

Reusable block combinations:

```
patterns/
└── hero-section.php
```

```php
<?php
/**
 * Title: Hero Section
 * Slug: my-theme/hero-section
 * Categories: featured
 * Block Types: core/group
 */
?>
<!-- wp:cover {"dimRatio":50,"minHeight":500} -->
<div class="wp-block-cover" style="min-height:500px">
    <div class="wp-block-cover__inner-container">
        <!-- wp:heading {"textAlign":"center","level":1} -->
        <h1 class="has-text-align-center">Welcome to Our Site</h1>
        <!-- /wp:heading -->
        <!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
        <div class="wp-block-buttons">
            <!-- wp:button -->
            <div class="wp-block-button"><a class="wp-block-button__link">Get Started</a></div>
            <!-- /wp:button -->
        </div>
        <!-- /wp:buttons -->
    </div>
</div>
<!-- /wp:cover -->
```

Register in theme.json:

```json
{
    "patterns": ["my-theme/hero-section"]
}
```

Or register from WordPress.org pattern directory:

```json
{
    "patterns": ["starter-content/hero-section"]
}
```

## functions.php in Block Themes

Still valid for:

```php
<?php
// Enqueue additional scripts
function my_theme_scripts() {
    wp_enqueue_script(
        'my-theme-scripts',
        get_template_directory_uri() . '/assets/js/scripts.js',
        array(),
        '1.0.0',
        true
    );
}
add_action( 'wp_enqueue_scripts', 'my_theme_scripts' );

// Register custom block styles
function my_theme_block_styles() {
    register_block_style( 'core/button', array(
        'name'  => 'outline-primary',
        'label' => __( 'Outline Primary', 'my-theme' ),
    ) );
}
add_action( 'init', 'my_theme_block_styles' );

// Add custom pattern categories
function my_theme_pattern_categories() {
    register_block_pattern_category( 'my-theme', array(
        'label' => __( 'My Theme', 'my-theme' ),
    ) );
}
add_action( 'init', 'my_theme_pattern_categories' );
```

## Migrating from Classic to Block

### Hybrid Approach

A theme can support both:

```
my-hybrid-theme/
├── style.css
├── theme.json            # Block theme features
├── templates/
│   └── index.html        # Block templates
├── index.php             # PHP fallback
├── header.php            # Classic fallback
└── functions.php
```

Add in functions.php:

```php
// Enable block template parts in classic templates
function my_theme_block_setup() {
    add_theme_support( 'block-template-parts' );
}
add_action( 'after_setup_theme', 'my_theme_block_setup' );
```

### Converting Templates

Classic PHP:

```php
<?php get_header(); ?>

<main>
    <?php if ( have_posts() ) : ?>
        <?php while ( have_posts() ) : the_post(); ?>
            <article>
                <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
                <?php the_excerpt(); ?>
            </article>
        <?php endwhile; ?>
    <?php endif; ?>
</main>

<?php get_footer(); ?>
```

Block HTML:

```html
<!-- wp:template-part {"slug":"header"} /-->

<!-- wp:group {"tagName":"main"} -->
<main class="wp-block-group">
    <!-- wp:query -->
    <div class="wp-block-query">
        <!-- wp:post-template -->
        <article>
            <!-- wp:post-title {"isLink":true} /-->
            <!-- wp:post-excerpt /-->
        </article>
        <!-- /wp:post-template -->
    </div>
    <!-- /wp:query -->
</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer"} /-->
```

## Limitations and Workarounds

### No PHP Logic in Templates

**Problem:** Can't use PHP conditionals in HTML templates.

**Solution:** Create separate templates or use block variations:

```
templates/
├── single.html           # Default single
├── single-product.html   # Products
└── single-event.html     # Events
```

### Limited Query Customization

**Problem:** Query Loop block has limited parameters.

**Solution:** Create a custom block or use render callback:

```php
register_block_type( 'my-theme/custom-query', array(
    'render_callback' => 'my_theme_custom_query_render',
) );
```

### Complex Layouts

**Problem:** Some layouts are hard to achieve with blocks.

**Solution:** Create block patterns or custom blocks for complex layouts.

## Debugging Block Themes

### Template Resolution

```php
add_action( 'template_redirect', function() {
    if ( ! current_user_can( 'manage_options' ) ) return;

    error_log( 'Template: ' . get_page_template_slug() );
} );
```

### theme.json Validation

Use the schema for IDE validation:

```json
{
    "$schema": "https://schemas.wp.org/trunk/theme.json"
}
```

### Site Editor Issues

- Clear browser cache
- Deactivate caching plugins
- Check for JavaScript errors in console
- Verify file permissions on templates/parts folders

## Further Reading

- [Template Hierarchy](./01-template-hierarchy.md) - How templates are selected
- [Child Themes](./02-child-themes.md) - Block theme child themes
- [Block Development](../08-plugin-development/08-block-development.md) - Creating custom blocks
- [WordPress Block Theme Documentation](https://developer.wordpress.org/themes/block-themes/) - Official docs
- [theme.json Reference](https://developer.wordpress.org/themes/advanced-topics/theme-json-reference/) - Complete settings reference
