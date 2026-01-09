# Template Hierarchy

## Overview

The template hierarchy is WordPress's system for choosing which template file to use when displaying a page. Understanding it lets you control exactly what displays where, without complex conditional logic.

WordPress checks for templates in a specific order. The first one found wins.

## How It Works

```
Request → WordPress determines query type → Checks for templates in order → Uses first match → Falls back to index.php
```

For example, viewing a single post:
1. WordPress detects "single post" query
2. Checks for `single-{post-type}-{slug}.php`
3. Then `single-{post-type}.php`
4. Then `single.php`
5. Finally `index.php`

## Complete Hierarchy

### Single Post

```
single-{post-type}-{slug}.php
single-{post-type}.php
single.php
singular.php
index.php
```

**Examples:**
- Post "hello-world" → `single-post-hello-world.php`
- Custom post type "product" → `single-product.php`
- Any single post → `single.php`

### Page

```
{custom-template}.php          (if selected in editor)
page-{slug}.php
page-{id}.php
page.php
singular.php
index.php
```

**Examples:**
- Page with slug "about" → `page-about.php`
- Page with ID 42 → `page-42.php`
- Any page → `page.php`

### Custom Post Type Archive

```
archive-{post-type}.php
archive.php
index.php
```

**Example:**
- Products archive (`/products/`) → `archive-product.php`

### Category Archive

```
category-{slug}.php
category-{id}.php
category.php
archive.php
index.php
```

**Example:**
- Category "news" → `category-news.php`

### Tag Archive

```
tag-{slug}.php
tag-{id}.php
tag.php
archive.php
index.php
```

### Custom Taxonomy Archive

```
taxonomy-{taxonomy}-{term}.php
taxonomy-{taxonomy}.php
taxonomy.php
archive.php
index.php
```

**Example:**
- Taxonomy "genre", term "fiction" → `taxonomy-genre-fiction.php`

### Author Archive

```
author-{nicename}.php
author-{id}.php
author.php
archive.php
index.php
```

### Date Archives

```
date.php
archive.php
index.php
```

### Search Results

```
search.php
index.php
```

### 404 Page

```
404.php
index.php
```

### Homepage

The homepage is special:

**If "Your homepage displays: Your latest posts":**
```
front-page.php
home.php
index.php
```

**If "Your homepage displays: A static page":**
```
front-page.php
page-{slug}.php (of selected page)
page-{id}.php
page.php
index.php
```

**Blog posts page (when using static front page):**
```
home.php
index.php
```

### Attachments

```
{mimetype}-{subtype}.php      (image-jpeg.php)
{subtype}.php                  (jpeg.php)
{mimetype}.php                 (image.php)
attachment.php
single-attachment-{slug}.php
single-attachment.php
single.php
singular.php
index.php
```

## Visual Hierarchy Chart

```
                                    index.php
                                        ↑
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
               singular.php        archive.php          search.php
                    ↑                   ↑                   │
            ┌───────┴───────┐   ┌───────┴───────┐          │
            │               │   │               │          │
         single.php      page.php  category.php  tag.php   │
            ↑               ↑         ↑           ↑        │
   single-{type}.php  page-{slug}.php  │           │        │
            ↑               ↑    category-{slug}.php       │
single-{type}-{slug}.php  page-{id}.php                    │
                                                           │
                              404.php ─────────────────────┘
```

## Template Parts

Reusable template components:

```php
// Include header.php
get_header();

// Include footer.php
get_footer();

// Include sidebar.php
get_sidebar();

// Include template-parts/content.php
get_template_part( 'template-parts/content' );

// Include template-parts/content-{post-format}.php
get_template_part( 'template-parts/content', get_post_format() );

// Include template-parts/content-product.php
get_template_part( 'template-parts/content', 'product' );

// Pass data to template part (WP 5.5+)
get_template_part( 'template-parts/card', null, array(
    'title' => $title,
    'image' => $image_url,
) );

// In the template part, access with:
$args['title'];
$args['image'];
```

### Header/Footer Variants

```php
// header.php (default)
get_header();

// header-home.php
get_header( 'home' );

// header-shop.php
get_header( 'shop' );
```

## Custom Page Templates

Create templates selectable in the page editor:

```php
<?php
/**
 * Template Name: Full Width
 * Template Post Type: page, post
 */

get_header();
?>

<main class="full-width">
    <?php while ( have_posts() ) : the_post(); ?>
        <?php the_content(); ?>
    <?php endwhile; ?>
</main>

<?php get_footer(); ?>
```

The `Template Name` comment makes it appear in the editor dropdown.

`Template Post Type` specifies which post types can use this template.

## Conditional Tags

When the hierarchy isn't enough:

```php
// In a template file
if ( is_front_page() && is_home() ) {
    // Default homepage (latest posts)
} elseif ( is_front_page() ) {
    // Static homepage
} elseif ( is_home() ) {
    // Blog page
}

// Post type checks
if ( is_singular( 'product' ) ) {
    // Single product
}

if ( is_post_type_archive( 'product' ) ) {
    // Products archive
}

// Taxonomy checks
if ( is_tax( 'genre', 'fiction' ) ) {
    // Fiction genre archive
}

if ( has_term( 'featured', 'product_tag' ) ) {
    // Post has "featured" product tag
}

// Page checks
if ( is_page( 'about' ) ) {
    // About page (by slug)
}

if ( is_page( array( 42, 'contact', 'About Us' ) ) ) {
    // Page 42, or slug "contact", or title "About Us"
}

// Ancestor checks (useful for sections)
if ( is_page() && $post->post_parent === 42 ) {
    // Direct child of page 42
}

// Category in single post
if ( in_category( 'news' ) ) {
    // Post is in news category
}
```

## Debugging Template Selection

### Using Query Monitor

Query Monitor shows:
- Current template file
- Template hierarchy (what was checked)
- Why each was skipped
- Template parts loaded

### Manual Debug

```php
// Add to functions.php
add_action( 'wp_head', function() {
    if ( ! current_user_can( 'manage_options' ) ) {
        return;
    }

    global $template;
    echo '<!-- Template: ' . esc_html( $template ) . ' -->';
} );
```

### template_include Filter

See what WordPress selected:

```php
add_filter( 'template_include', function( $template ) {
    error_log( 'Template: ' . $template );
    return $template;
}, 9999 );
```

## Common Patterns

### Different Layouts by Category

```
themes/my-theme/
├── single.php              # Default single post
├── single-post.php         # All posts
└── category/
    └── news/
        └── single.php      # Won't work! Not in hierarchy
```

**Solution:** Use conditional in single.php:

```php
// single.php
if ( in_category( 'news' ) ) {
    get_template_part( 'template-parts/single', 'news' );
} else {
    get_template_part( 'template-parts/single', 'default' );
}
```

### Custom Post Type with Taxonomy

```
archive-product.php              # /products/
taxonomy-product-category.php    # /product-category/clothing/
single-product.php               # /product/blue-shirt/
```

### Section-Based Templates

For a site with sections like `/services/web-design/`:

```php
// page.php
$ancestors = get_post_ancestors( $post );
$root_id   = $ancestors ? end( $ancestors ) : $post->ID;
$root_slug = get_post_field( 'post_name', $root_id );

get_template_part( 'template-parts/page', $root_slug );
// Loads template-parts/page-services.php for any page under Services
```

## Block Theme Templates

In block themes, templates are HTML:

```
templates/
├── index.html
├── single.html
├── single-product.html
├── page.html
├── archive.html
├── archive-product.html
├── 404.html
└── search.html
```

The hierarchy works the same, but files contain block markup:

```html
<!-- templates/single.html -->
<!-- wp:template-part {"slug":"header"} /-->

<!-- wp:group {"tagName":"main"} -->
<main class="wp-block-group">
    <!-- wp:post-title /-->
    <!-- wp:post-content /-->
</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer"} /-->
```

## Further Reading

- [Child Themes](./02-child-themes.md) - Overriding parent templates
- [Block Themes](./03-block-themes.md) - Template hierarchy in block themes
- [WordPress Template Hierarchy](https://developer.wordpress.org/themes/basics/template-hierarchy/) - Official documentation
- [Visual Template Hierarchy](https://developer.wordpress.org/files/2014/10/Screenshot-2019-01-23-00.20.04.png) - Interactive diagram
