# Theme Development

## Overview

Themes control how WordPress displays content. Understanding theme architecture helps you customize existing themes safely, build child themes for clients, and know when code belongs in a theme versus a plugin.

This chapter focuses on practical theme knowledge—not comprehensive theme building, but the fundamentals every WordPress developer needs.

## Theme vs. Plugin: Where Does Code Belong?

The most common mistake: putting everything in `functions.php`.

| Put in Theme | Put in Plugin |
|--------------|---------------|
| Presentation and layout | Functionality |
| Template markup | Custom post types |
| Theme-specific styles | Shortcodes |
| Menu locations | AJAX handlers |
| Widget areas | Database operations |
| Theme customizer options | Admin features |

**The test:** If you switch themes, should this feature disappear?
- **Yes** → Theme (e.g., header layout)
- **No** → Plugin (e.g., contact form)

## What This Chapter Covers

### [Template Hierarchy](./01-template-hierarchy.md)

How WordPress decides which template file to use. Understanding this is fundamental—it's how you control what displays where. Covers:

- The complete hierarchy
- Template parts and includes
- Conditional tags
- Debugging which template is used

### [Child Themes](./02-child-themes.md)

Safely customizing themes without losing changes on update. Essential for client work. Covers:

- When and why to use child themes
- Proper setup and structure
- Overriding templates and functions
- Common pitfalls

### [Block Themes (FSE)](./03-block-themes.md)

The new WordPress theme paradigm using Full Site Editing. Covers:

- theme.json configuration
- Block templates vs. PHP templates
- Template parts in block themes
- Migrating from classic to block themes

### [Accessibility](./04-accessibility.md)

Building websites everyone can use. Accessibility isn't optional—it's ethical, often legal, and improves experience for everyone. Covers:

- WCAG principles and conformance levels
- Common WordPress accessibility issues
- Testing methods (automated and manual)
- Quick wins for accessibility

## Theme Fundamentals

### Required Files

A valid WordPress theme needs only two files:

```
my-theme/
├── style.css      (with theme header)
└── index.php      (fallback template)
```

**style.css header:**
```css
/*
Theme Name: My Theme
Theme URI: https://example.com/my-theme
Author: Your Name
Author URI: https://example.com
Description: A custom WordPress theme.
Version: 1.0.0
Requires at least: 6.0
Tested up to: 6.4
Requires PHP: 7.4
License: GPL-2.0-or-later
License URI: https://www.gnu.org/licenses/gpl-2.0.html
Text Domain: my-theme
*/
```

### Common Theme Structure

```
my-theme/
├── style.css
├── functions.php          # Theme setup, hooks
├── index.php              # Fallback template
├── front-page.php         # Homepage
├── single.php             # Single posts
├── page.php               # Pages
├── archive.php            # Archives
├── search.php             # Search results
├── 404.php                # Not found
├── header.php             # Site header
├── footer.php             # Site footer
├── sidebar.php            # Sidebar
├── comments.php           # Comments template
├── screenshot.png         # Theme preview (1200x900)
├── template-parts/        # Reusable components
│   ├── content.php
│   ├── content-excerpt.php
│   └── content-none.php
├── inc/                   # PHP includes
│   ├── customizer.php
│   └── template-tags.php
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── languages/             # Translation files
```

### Theme Setup in functions.php

```php
<?php
/**
 * Theme setup and configuration
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Theme setup - runs after theme is loaded
 */
function my_theme_setup() {
    // Add theme support features
    add_theme_support( 'title-tag' );
    add_theme_support( 'post-thumbnails' );
    add_theme_support( 'html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ) );
    add_theme_support( 'custom-logo', array(
        'height'      => 100,
        'width'       => 400,
        'flex-height' => true,
        'flex-width'  => true,
    ) );
    add_theme_support( 'editor-styles' );
    add_theme_support( 'responsive-embeds' );

    // Register navigation menus
    register_nav_menus( array(
        'primary' => __( 'Primary Menu', 'my-theme' ),
        'footer'  => __( 'Footer Menu', 'my-theme' ),
    ) );

    // Set content width
    $GLOBALS['content_width'] = 1200;

    // Load text domain for translations
    load_theme_textdomain( 'my-theme', get_template_directory() . '/languages' );
}
add_action( 'after_setup_theme', 'my_theme_setup' );

/**
 * Enqueue scripts and styles
 */
function my_theme_scripts() {
    // Main stylesheet
    wp_enqueue_style(
        'my-theme-style',
        get_stylesheet_uri(),
        array(),
        wp_get_theme()->get( 'Version' )
    );

    // Additional CSS
    wp_enqueue_style(
        'my-theme-main',
        get_template_directory_uri() . '/assets/css/main.css',
        array(),
        wp_get_theme()->get( 'Version' )
    );

    // JavaScript
    wp_enqueue_script(
        'my-theme-navigation',
        get_template_directory_uri() . '/assets/js/navigation.js',
        array(),
        wp_get_theme()->get( 'Version' ),
        true
    );

    // Comment reply script
    if ( is_singular() && comments_open() && get_option( 'thread_comments' ) ) {
        wp_enqueue_script( 'comment-reply' );
    }
}
add_action( 'wp_enqueue_scripts', 'my_theme_scripts' );

/**
 * Register widget areas
 */
function my_theme_widgets_init() {
    register_sidebar( array(
        'name'          => __( 'Sidebar', 'my-theme' ),
        'id'            => 'sidebar-1',
        'description'   => __( 'Add widgets here.', 'my-theme' ),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h2 class="widget-title">',
        'after_title'   => '</h2>',
    ) );

    register_sidebar( array(
        'name'          => __( 'Footer', 'my-theme' ),
        'id'            => 'footer-1',
        'description'   => __( 'Footer widget area.', 'my-theme' ),
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ) );
}
add_action( 'widgets_init', 'my_theme_widgets_init' );
```

## Theme Support Features

Common features to enable:

```php
// Let WordPress manage the <title> tag
add_theme_support( 'title-tag' );

// Featured images
add_theme_support( 'post-thumbnails' );
add_image_size( 'featured-large', 1200, 600, true );

// Custom logo in Customizer
add_theme_support( 'custom-logo' );

// Custom header image
add_theme_support( 'custom-header', array(
    'default-image' => '',
    'width'         => 1920,
    'height'        => 500,
    'flex-width'    => true,
    'flex-height'   => true,
) );

// Custom background
add_theme_support( 'custom-background' );

// Block editor features
add_theme_support( 'align-wide' );
add_theme_support( 'editor-styles' );
add_editor_style( 'assets/css/editor-style.css' );

// Block color palette
add_theme_support( 'editor-color-palette', array(
    array(
        'name'  => __( 'Primary', 'my-theme' ),
        'slug'  => 'primary',
        'color' => '#0073aa',
    ),
    array(
        'name'  => __( 'Secondary', 'my-theme' ),
        'slug'  => 'secondary',
        'color' => '#23282d',
    ),
) );

// WooCommerce support
add_theme_support( 'woocommerce' );
add_theme_support( 'wc-product-gallery-zoom' );
add_theme_support( 'wc-product-gallery-lightbox' );
add_theme_support( 'wc-product-gallery-slider' );
```

## The Loop

The fundamental pattern for displaying content:

```php
<?php if ( have_posts() ) : ?>

    <?php while ( have_posts() ) : the_post(); ?>

        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <header>
                <h2>
                    <a href="<?php the_permalink(); ?>">
                        <?php the_title(); ?>
                    </a>
                </h2>
                <p class="meta">
                    <?php echo get_the_date(); ?> by <?php the_author(); ?>
                </p>
            </header>

            <div class="content">
                <?php the_excerpt(); ?>
            </div>

            <footer>
                <?php the_category( ', ' ); ?>
            </footer>
        </article>

    <?php endwhile; ?>

    <?php the_posts_navigation(); ?>

<?php else : ?>

    <p><?php esc_html_e( 'No posts found.', 'my-theme' ); ?></p>

<?php endif; ?>
```

## Common Template Tags

```php
// Site information
bloginfo( 'name' );           // Site title
bloginfo( 'description' );    // Tagline
home_url( '/' );              // Homepage URL
get_template_directory_uri(); // Theme URL (parent)
get_stylesheet_directory_uri(); // Theme URL (child if active)

// Post information
the_title();                  // Post title
the_permalink();              // Post URL
the_content();                // Post content
the_excerpt();                // Post excerpt
the_post_thumbnail();         // Featured image
the_date();                   // Post date
the_author();                 // Author name
the_category( ', ' );         // Categories
the_tags( 'Tags: ', ', ' );   // Tags
get_the_ID();                 // Post ID

// Conditional tags
is_front_page();              // Is homepage
is_home();                    // Is blog posts page
is_single();                  // Is single post
is_page();                    // Is page
is_archive();                 // Is archive
is_category();                // Is category archive
is_tag();                     // Is tag archive
is_search();                  // Is search results
is_404();                     // Is 404 page
is_user_logged_in();          // Is logged in

// Navigation
wp_nav_menu( array(
    'theme_location' => 'primary',
    'container'      => 'nav',
    'container_class'=> 'main-navigation',
) );

// Sidebar
get_sidebar();                // Include sidebar.php
get_sidebar( 'footer' );      // Include sidebar-footer.php
dynamic_sidebar( 'sidebar-1' ); // Output widget area

// Template parts
get_header();                 // Include header.php
get_footer();                 // Include footer.php
get_template_part( 'template-parts/content', get_post_type() );
```

## Classic vs. Block Themes

| Aspect | Classic Theme | Block Theme |
|--------|---------------|-------------|
| Templates | PHP files | HTML files |
| Styling | style.css | theme.json + CSS |
| Header/Footer | header.php, footer.php | Block template parts |
| Customization | Customizer | Site Editor |
| Theme support | add_theme_support() | theme.json |

**Block theme minimum structure:**
```
my-block-theme/
├── style.css
├── theme.json           # Configuration
├── templates/
│   └── index.html       # Fallback template
└── parts/               # Reusable parts
    ├── header.html
    └── footer.html
```

## Debugging Themes

### Find Active Template

```php
// Add to functions.php temporarily
add_action( 'wp_head', function() {
    if ( current_user_can( 'manage_options' ) ) {
        global $template;
        echo '<!-- Template: ' . basename( $template ) . ' -->';
    }
} );
```

### Query Monitor

Shows which template is being used and why, template parts loaded, and template hierarchy.

### Common Issues

**Styles not loading:**
```php
// Check enqueue is correct
wp_enqueue_style( 'handle', get_template_directory_uri() . '/style.css' );

// For child themes, use:
wp_enqueue_style( 'handle', get_stylesheet_directory_uri() . '/style.css' );
```

**Template not being used:**
- Check filename spelling
- Verify template hierarchy
- Clear any caching
- Check for template redirect filters

## Further Reading

- [Plugin Architecture](../08-plugin-development/README.md) - When to use plugins instead
- [Block Development](../08-plugin-development/08-block-development.md) - Creating blocks for themes
- [WordPress Theme Handbook](https://developer.wordpress.org/themes/) - Official documentation
- [Theme Developer Checklist](https://developer.wordpress.org/themes/releasing-your-theme/required-theme-files/) - Requirements for WordPress.org
