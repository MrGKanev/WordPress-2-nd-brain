# Performance-First Theming

A theme's performance impact is often larger than any plugin's. Every template, stylesheet, script, and font choice affects load time. The difference between a well-built theme and a bloated one can be 2-3 seconds of load time — the difference between a site that converts and one that bounces visitors.

## Conditional Asset Loading

The biggest theme performance mistake: loading every CSS and JS file on every page.

### Load Assets Only Where Needed

```php
add_action( 'wp_enqueue_scripts', function() {
    // Global styles — always needed
    wp_enqueue_style( 'theme-main', get_stylesheet_uri(), array(), '1.0.0' );

    // Contact form styles — only on pages with the form
    if ( is_page( 'contact' ) || has_shortcode( get_post()->post_content ?? '', 'contact-form' ) ) {
        wp_enqueue_style( 'theme-contact', get_template_directory_uri() . '/css/contact.css', array(), '1.0.0' );
    }

    // Comment reply script — only when needed
    if ( is_singular() && comments_open() && get_option( 'thread_comments' ) ) {
        wp_enqueue_script( 'comment-reply' );
    }

    // WooCommerce styles — only on shop pages
    if ( function_exists( 'is_woocommerce' ) && ! is_woocommerce() && ! is_cart() && ! is_checkout() && ! is_account_page() ) {
        wp_dequeue_style( 'woocommerce-general' );
        wp_dequeue_style( 'woocommerce-layout' );
        wp_dequeue_style( 'woocommerce-smallscreen' );
        wp_dequeue_script( 'wc-cart-fragments' );
    }
} );
```

### Dequeue Unnecessary Defaults

```php
add_action( 'wp_enqueue_scripts', function() {
    // Remove block library CSS if not using blocks
    // (Careful: only if you truly don't use any blocks)
    // wp_dequeue_style( 'wp-block-library' );

    // Remove global styles if using classic theme
    // wp_dequeue_style( 'global-styles' );

    // Remove emoji detection script (rarely needed)
    remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
    remove_action( 'wp_print_styles', 'print_emoji_styles' );
}, 20 );
```

## Critical CSS

Critical CSS is the minimum CSS needed to render above-the-fold content. It's inlined in `<head>` so the browser doesn't wait for external stylesheets.

### Strategy

```
1. Generate critical CSS for key templates (home, single, archive)
2. Inline critical CSS in <head>
3. Load full stylesheet asynchronously
```

### Implementation

```php
add_action( 'wp_head', function() {
    $template_type = 'default';
    if ( is_front_page() ) {
        $template_type = 'home';
    } elseif ( is_singular() ) {
        $template_type = 'single';
    } elseif ( is_archive() ) {
        $template_type = 'archive';
    }

    $critical_css_file = get_template_directory() . "/css/critical/{$template_type}.css";
    if ( file_exists( $critical_css_file ) ) {
        echo '<style>' . file_get_contents( $critical_css_file ) . '</style>';
    }
}, 1 );

// Load full stylesheet with low priority
add_filter( 'style_loader_tag', function( $html, $handle ) {
    if ( 'theme-main' === $handle ) {
        // Use media="print" trick to load asynchronously
        return str_replace( "media='all'", "media='print' onload=\"this.media='all'\"", $html );
    }
    return $html;
}, 10, 2 );
```

### Generating Critical CSS

| Tool | Type | Best For |
|------|------|----------|
| **Critical** (npm package) | Build tool | Automated in build pipeline |
| **WP Rocket** | Plugin | Automatic generation, no build step |
| **LiteSpeed Cache** | Plugin + server | LiteSpeed hosting environments |
| **Perfmatters** | Plugin | Manual critical CSS per page/template |

## Font Optimization

Fonts are often the heaviest render-blocking resource in a theme.

### Self-Hosting vs CDN

| Approach | Pros | Cons |
|----------|------|------|
| **Google Fonts CDN** | Easy, auto-optimized | Privacy concerns (GDPR), extra DNS lookup |
| **Self-hosted** | GDPR-friendly, faster (same origin) | Manual updates, more setup |
| **System fonts** | Zero download, instant render | Limited design options |

### Self-Hosting Google Fonts

1. Download fonts from [google-webfonts-helper](https://gwfh.mranftl.com/fonts)
2. Place in theme's `fonts/` directory
3. Declare with `@font-face`

```css
@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('./fonts/inter-v13-latin-regular.woff2') format('woff2');
}
```

### Key Font Optimizations

| Optimization | How | Impact |
|-------------|-----|--------|
| `font-display: swap` | Shows fallback font until custom font loads | Eliminates FOIT |
| `woff2` only | Modern format, best compression | 30% smaller than woff |
| Preload critical fonts | `<link rel="preload">` | Starts download early |
| Subset fonts | Only include needed characters | 50-80% smaller files |
| Limit font weights | 2-3 weights max | Fewer files to download |

```php
// Preload critical font files
add_action( 'wp_head', function() {
    echo '<link rel="preload" href="' . esc_url( get_template_directory_uri() . '/fonts/inter-v13-latin-regular.woff2' ) . '" as="font" type="font/woff2" crossorigin>';
}, 1 );
```

### System Font Stack

For maximum performance, skip web fonts entirely:

```css
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
}

code, pre {
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas,
                 "Liberation Mono", monospace;
}
```

## Image Handling in Themes

### Responsive Images

WordPress generates `srcset` automatically for images inserted through the editor. For theme images, use `wp_get_attachment_image()`:

```php
// Instead of manually building <img> tags:
echo wp_get_attachment_image( $image_id, 'large', false, array(
    'class'   => 'hero-image',
    'loading' => 'lazy',
    'sizes'   => '(max-width: 768px) 100vw, 50vw',
) );
```

### Lazy Loading

WordPress 5.5+ adds `loading="lazy"` to images and iframes by default. But the first visible image (LCP candidate) should NOT be lazy loaded:

```php
// Remove lazy loading from hero/above-fold images
add_filter( 'wp_img_tag_add_loading_attr', function( $value, $image, $context ) {
    // Don't lazy-load the first image in content (likely LCP)
    static $count = 0;
    $count++;
    if ( 'the_content' === $context && 1 === $count ) {
        return false; // No loading attribute = eager load
    }
    return $value;
}, 10, 3 );
```

### Featured Image Sizes

Register only the sizes your theme actually uses:

```php
add_action( 'after_setup_theme', function() {
    add_image_size( 'hero', 1200, 600, true );
    add_image_size( 'card', 400, 300, true );
    add_image_size( 'thumbnail-small', 150, 150, true );

    // Remove sizes you don't use
    remove_image_size( '1536x1536' );
    remove_image_size( '2048x2048' );
} );
```

Every registered image size means another file generated per upload. If you have 10 sizes and upload 1000 images, that's 10,000 files on disk.

## Reducing DOM Output

Excessive DOM nodes slow rendering. Page builders are the worst offenders (see [Page Builders & DOM Bloat](../04-performance/16-page-builders-dom-bloat.md)), but themes contribute too.

### Common DOM Bloat Sources

| Source | Problem | Solution |
|--------|---------|----------|
| Wrapper divs | Unnecessary nesting | Flatten markup |
| Social sharing buttons | 50+ elements per button set | Load on interaction |
| Related posts | Full post markup for each | Simpler card markup |
| Comment avatars | Gravatar request per comment | Lazy load or disable |
| Sidebar widgets | Complex markup per widget | Simplify widget output |

### Template Simplification

```php
// Bloated approach: wrapping everything
<div class="post-wrapper">
    <div class="post-inner">
        <div class="post-content-wrapper">
            <article class="post">
                <div class="entry-content">
                    <?php the_content(); ?>
                </div>
            </article>
        </div>
    </div>
</div>

// Clean approach: minimal wrappers
<article <?php post_class(); ?>>
    <?php the_content(); ?>
</article>
```

## Script Loading Strategies

### Defer and Async

```php
// Add defer to non-critical scripts
add_filter( 'script_loader_tag', function( $tag, $handle ) {
    $defer_scripts = array( 'theme-navigation', 'theme-lightbox' );

    if ( in_array( $handle, $defer_scripts, true ) ) {
        return str_replace( ' src', ' defer src', $tag );
    }

    return $tag;
}, 10, 2 );
```

WordPress 6.3+ supports the `strategy` parameter natively:

```php
wp_enqueue_script(
    'theme-navigation',
    get_template_directory_uri() . '/js/navigation.js',
    array(),
    '1.0.0',
    array(
        'strategy' => 'defer',
        'in_footer' => true,
    )
);
```

| Strategy | Behavior | Use For |
|----------|----------|---------|
| `defer` | Download parallel, execute after HTML parsed | Most scripts |
| `async` | Download parallel, execute immediately when ready | Analytics, tracking |
| Neither | Blocks rendering until downloaded and executed | Critical functionality |

### Inline Small Scripts

For scripts under 1KB, inlining saves an HTTP request:

```php
add_action( 'wp_footer', function() {
    $script = file_get_contents( get_template_directory() . '/js/tiny-utility.js' );
    if ( $script ) {
        echo '<script>' . $script . '</script>';
    }
} );
```

## Theme Performance Checklist

- [ ] Assets load conditionally (not every CSS/JS on every page)
- [ ] No render-blocking scripts in `<head>` (use `defer` or footer)
- [ ] Fonts self-hosted with `font-display: swap`
- [ ] Maximum 2-3 font weights loaded
- [ ] Critical CSS inlined for key templates
- [ ] Images use `srcset` and proper `sizes` attributes
- [ ] Above-fold images NOT lazy loaded (LCP optimization)
- [ ] Unused image sizes removed
- [ ] DOM output is clean (minimal wrapper divs)
- [ ] Third-party scripts loaded conditionally or deferred
- [ ] WooCommerce assets dequeued on non-shop pages (if applicable)

## Further Reading

- [Frontend Asset Optimization](../04-performance/13-frontend-asset-optimization.md) — CSS/JS minification and bundling
- [Core Web Vitals](../04-performance/08-core-web-vitals-optimizations.md) — LCP, FID, CLS optimization
- [Image Optimization](../04-performance/06-image-optimizations.md) — Format selection, compression
- [Page Builders & DOM Bloat](../04-performance/16-page-builders-dom-bloat.md) — When page builders hurt performance
- [Plugin Performance](../04-performance/15-plugin-performance.md) — Evaluating theme/plugin impact
