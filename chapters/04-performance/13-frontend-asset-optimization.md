# Frontend Asset Optimization

## Overview

Beyond images and database queries, frontend assets—fonts, icons, scripts, and stylesheets—significantly impact page weight and rendering performance. This chapter covers techniques for optimizing these assets that are often overlooked.

## Font Optimization

Fonts typically account for 6% of page weight on mobile. Poor font loading causes invisible text (FOIT) or layout shifts (FOUT).

### Limit Font Variations

Every font weight and style requires a separate file download:

| What You Load | Files | Typical Size |
|--------------|-------|--------------|
| Single font, one weight | 1 | ~20-50KB |
| Single font, 3 weights | 3 | ~60-150KB |
| Two fonts, multiple weights | 6+ | ~120-300KB |

**Recommendation:** Use at most 2 font families with 2-3 weights each.

### Host Fonts Locally

Google Fonts are convenient but suboptimal:

1. **Extra DNS lookup** - Adds ~100ms to load time
2. **No browser cache sharing** - Chrome partitions cache by site since 2020
3. **GDPR concerns** - User IPs sent to Google servers

**Local hosting benefits:**
- Served from your CDN with your caching headers
- No third-party request
- Full control over font formats and subsetting

```php
// Dequeue Google Fonts loaded by themes/plugins
add_action( 'wp_enqueue_scripts', function() {
    wp_dequeue_style( 'google-fonts' );
    wp_deregister_style( 'google-fonts' );
}, 100 );
```

**Tools for local fonts:**
- [Google Webfonts Helper](https://gwfh.mranftl.com/fonts) - Download optimized packages
- [Transfonter](https://transfonter.org/) - Convert and subset fonts
- [OMGF Plugin](https://wordpress.org/plugins/host-webfonts-local/) - Automatically downloads and hosts Google Fonts

### System Font Stacks

The fastest font is one you don't load. System fonts are pre-installed:

```css
/* Modern system font stack */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
}

/* Monospace system stack */
code {
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo,
                 Consolas, "Liberation Mono", monospace;
}
```

**Trade-off:** Fonts look slightly different across operating systems, but load time is zero.

### Font Display Strategy

Control text visibility during font loading:

```css
@font-face {
    font-family: 'CustomFont';
    src: url('font.woff2') format('woff2');
    font-display: swap; /* Show fallback immediately, swap when loaded */
}
```

| Value | Behavior | Use Case |
|-------|----------|----------|
| `swap` | Show fallback immediately | Most body text |
| `optional` | Show fallback, may skip custom font | Performance-critical |
| `fallback` | Brief invisible period, then fallback | Balance |
| `block` | Invisible until loaded | Icons, logos |

**WordPress implementation:**

```php
// Add font-display: swap to Google Fonts
add_filter( 'style_loader_tag', function( $html, $handle ) {
    if ( strpos( $html, 'fonts.googleapis.com' ) !== false ) {
        $html = str_replace( "googleapis.com/css", "googleapis.com/css2", $html );
        $html = preg_replace( '/family=([^&\'"]+)/', 'family=$1&display=swap', $html );
    }
    return $html;
}, 10, 2 );
```

### Preload Critical Fonts

Fonts discovered late in the render process cause delays:

```php
// Preload primary font
add_action( 'wp_head', function() {
    echo '<link rel="preload" href="/wp-content/themes/theme/fonts/primary.woff2" as="font" type="font/woff2" crossorigin>';
}, 1 );
```

**Limit to 1-2 fonts**—excessive preloading delays other resources.

## Icon Optimization

Icon libraries like Font Awesome load hundreds of icons when you use only a few.

### The Font Awesome Problem

| Library Version | Full Size | Typical Usage |
|----------------|-----------|---------------|
| Font Awesome 6 Free | ~150KB | 5-10 icons |
| Font Awesome 5 | ~100KB | 5-10 icons |
| Material Icons | ~200KB+ | 5-10 icons |

Loading 150KB for 5 icons (< 5KB) is wasteful.

### Solution 1: SVG Icons

Use inline SVGs instead of icon fonts:

```html
<!-- Icon font approach (loads entire library) -->
<i class="fas fa-search"></i>

<!-- SVG approach (only what you need) -->
<svg width="20" height="20" viewBox="0 0 512 512">
    <path d="M416 208c0 45.9..."/>
</svg>
```

**Benefits:**
- Only load icons you use
- Better accessibility (can add title/desc)
- Crisp at any size
- Style with CSS

**WordPress block editor:** Use the core Icons block or GenerateBlocks which outputs inline SVGs.

### Solution 2: Custom Icon Fonts

Build a custom font with only the icons you need:

1. [IcoMoon](https://icomoon.io/) - Select individual icons, export custom font
2. [Fontello](https://fontello.com/) - Similar icon picker and builder

Result: 5-10KB instead of 100KB+.

### Solution 3: Remove Unused Icon Loading

Many plugins load Font Awesome unnecessarily:

```php
// Dequeue Font Awesome loaded by plugins
add_action( 'wp_enqueue_scripts', function() {
    wp_dequeue_style( 'font-awesome' );
    wp_dequeue_style( 'fontawesome' );
    wp_dequeue_script( 'font-awesome' );
}, 100 );
```

**Check with Query Monitor** which plugins enqueue icon libraries.

## Script Management

Not every script needs to load on every page. A contact form script doesn't belong on your blog posts.

### Per-Page Asset Loading

The concept: Disable scripts and styles on pages where they're not needed.

**Plugins for this:**

| Plugin | Approach | Complexity |
|--------|----------|------------|
| [Asset CleanUp](https://wordpress.org/plugins/wp-asset-clean-up/) | Per-page disable | Medium |
| [Perfmatters](https://perfmatters.io/) | Per-page + global rules | Low |
| [Gonzalez](https://developer.developer.developer/) | Simple per-page | Low |

**Manual approach:**

```php
// Only load Contact Form 7 assets on contact page
add_action( 'wp_enqueue_scripts', function() {
    // Check if not on contact page
    if ( ! is_page( 'contact' ) ) {
        wp_dequeue_script( 'contact-form-7' );
        wp_dequeue_style( 'contact-form-7' );
    }
}, 100 );

// Only load WooCommerce scripts on shop pages
add_action( 'wp_enqueue_scripts', function() {
    if ( ! is_woocommerce() && ! is_cart() && ! is_checkout() ) {
        wp_dequeue_script( 'wc-cart-fragments' );
        wp_dequeue_style( 'woocommerce-general' );
    }
}, 100 );
```

### Defer Non-Critical JavaScript

Scripts that don't affect above-the-fold content should defer:

```php
// Add defer to all scripts
add_filter( 'script_loader_tag', function( $tag, $handle, $src ) {
    // Exclude critical scripts
    $exclude = array( 'jquery', 'wp-hooks' );

    if ( in_array( $handle, $exclude ) ) {
        return $tag;
    }

    // Don't double-add
    if ( strpos( $tag, 'defer' ) !== false ) {
        return $tag;
    }

    return str_replace( ' src=', ' defer src=', $tag );
}, 10, 3 );
```

### Delay JavaScript Until Interaction

Third-party scripts (analytics, chat widgets, ads) can delay interactivity. Load them only after user interaction:

```javascript
// Delay scripts until user interaction
const delayedScripts = [
    'https://www.googletagmanager.com/gtag/js',
    'https://static.hotjar.com/',
    'https://connect.facebook.net/'
];

let scriptsLoaded = false;

function loadDelayedScripts() {
    if (scriptsLoaded) return;
    scriptsLoaded = true;

    delayedScripts.forEach(src => {
        const script = document.createElement('script');
        script.src = src;
        script.async = true;
        document.body.appendChild(script);
    });
}

// Trigger on first interaction
['scroll', 'click', 'touchstart', 'mouseover'].forEach(event => {
    window.addEventListener(event, loadDelayedScripts, { once: true, passive: true });
});

// Fallback: load after 5 seconds anyway
setTimeout(loadDelayedScripts, 5000);
```

**Caution:** Delayed scripts affect INP if the first interaction also triggers heavy JavaScript.

### Local Analytics

Hosting Google Analytics locally eliminates a third-party request:

**Benefits:**
- No DNS lookup to google-analytics.com
- Script served from your CDN
- Better cache control

**Tools:**
- [CAOS (Complete Analytics Optimization Suite)](https://wordpress.org/plugins/host-analyticsjs-local/) - Hosts GA locally
- [Flying Analytics](https://developer.developer.developer/) - Similar approach

**Manual approach:**

```php
// Download and enqueue local analytics
add_action( 'wp_enqueue_scripts', function() {
    wp_enqueue_script(
        'google-analytics',
        get_template_directory_uri() . '/js/analytics.js',
        array(),
        null,
        true
    );
});
```

## Unused CSS Removal

Themes and plugins load CSS for features you may not use. Page builders are notorious for this.

### The Problem

| Source | Typical CSS Size | Actually Used |
|--------|-----------------|---------------|
| Page builder (Elementor) | 200-400KB | 20-50KB |
| Theme framework | 100-200KB | 30-60KB |
| Plugin styles | 50-100KB each | 5-20KB |

### Solution: Remove Unused CSS

**Per-page unused CSS removal:**

```php
// Use a plugin like Perfmatters, WP Rocket, or FlyingPress
// They generate used CSS per page and inline it
```

**Tools:**
- [PurgeCSS](https://purgecss.com/) - Build tool for removing unused CSS
- [WP Rocket](https://wp-rocket.me/) - "Remove Unused CSS" feature
- [FlyingPress](https://flyingpress.com/) - Per-page CSS optimization

### Critical CSS

Load only above-the-fold CSS initially, defer the rest:

```html
<!-- Inline critical CSS -->
<style>
/* Only styles needed for above-the-fold content */
.header { ... }
.hero { ... }
</style>

<!-- Defer full stylesheet -->
<link rel="preload" href="style.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="style.css"></noscript>
```

**WordPress plugins with critical CSS:**
- WP Rocket
- FlyingPress
- Perfmatters (with Critical CSS add-on)

## Server Compression

Text-based assets should be compressed before transfer.

### Compression Methods

| Method | Compression Ratio | Browser Support |
|--------|------------------|-----------------|
| gzip | ~70% reduction | Universal |
| Brotli | ~80% reduction | All modern browsers |
| Zstandard | ~85% reduction | Growing support |

### Enable Brotli

**Nginx:**
```nginx
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
```

**Apache (.htaccess):**
```apache
<IfModule mod_brotli.c>
    AddOutputFilterByType BROTLI_COMPRESS text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>
```

**Verify:** Check response headers in DevTools Network panel for `Content-Encoding: br`.

## Additional Best Practices

### Avoid Unnecessary Redirects

Each redirect adds a round-trip (~100-300ms):

```
example.com → www.example.com → https://www.example.com
```

**Fix:** Configure canonical domain at server level, not via WordPress plugins.

### Replace Sliders with Static Content

Sliders are performance killers:
- Multiple large images loaded
- JavaScript for animation
- Layout shifts during load
- Often poor UX anyway

**Alternative:** Static hero image with clear call-to-action.

### Limit Animations

Animations above the fold impact LCP and CLS:

```css
/* Reduce motion for users who prefer it */
@media (prefers-reduced-motion: reduce) {
    * {
        animation: none !important;
        transition: none !important;
    }
}

/* Use transform/opacity instead of layout properties */
.animate {
    /* Good - GPU accelerated */
    transform: translateX(100px);
    opacity: 0.5;

    /* Bad - triggers layout */
    /* left: 100px; */
    /* width: 200px; */
}
```

### reCAPTCHA Alternatives

Google reCAPTCHA loads ~500KB of JavaScript. Alternatives:

| Solution | Size | Effectiveness |
|----------|------|--------------|
| Honeypot fields | 0KB | Good for simple bots |
| [Cloudflare Turnstile](https://www.cloudflare.com/products/turnstile/) | ~50KB | Excellent |
| [hCaptcha](https://www.hcaptcha.com/) | ~100KB | Good |
| Time-based validation | 0KB | Moderate |

```php
// Simple honeypot field
add_action( 'comment_form_after_fields', function() {
    echo '<p class="hp-field" style="display:none !important;">';
    echo '<label>Leave empty</label>';
    echo '<input type="text" name="hp_check" value="" tabindex="-1" autocomplete="off">';
    echo '</p>';
});

add_action( 'pre_comment_on_post', function() {
    if ( ! empty( $_POST['hp_check'] ) ) {
        wp_die( 'Spam detected' );
    }
});
```

### Optimize Gravatars

Gravatars add external requests for each commenter:

```php
// Disable Gravatars entirely
add_filter( 'option_show_avatars', '__return_false' );

// Or lazy load them
add_filter( 'get_avatar', function( $avatar ) {
    return str_replace( '<img', '<img loading="lazy"', $avatar );
});
```

**Alternative:** Use local avatars with [Simple Local Avatars](https://wordpress.org/plugins/simple-local-avatars/).

## Testing Tools

Beyond PageSpeed Insights and Lighthouse:

| Tool | Best For |
|------|----------|
| [DebugBear](https://www.debugbear.com/) | LCP debugging, real user monitoring |
| [Yellow Lab Tools](https://yellowlab.tools/) | Finding duplicate libraries, unused code |
| [HTML Size Analyzer](https://www.debugbear.com/html-size-analyzer) | Oversized inline code detection |
| [WebPageTest](https://www.webpagetest.org/) | Detailed waterfall analysis |
| [Bundlephobia](https://bundlephobia.com/) | JavaScript package size analysis |

## Quick Wins Checklist

- [ ] Host fonts locally or use system fonts
- [ ] Add `font-display: swap` to custom fonts
- [ ] Replace icon fonts with inline SVGs
- [ ] Disable unused plugin scripts per page
- [ ] Enable Brotli compression
- [ ] Remove or replace reCAPTCHA
- [ ] Lazy load Gravatars or disable them
- [ ] Replace sliders with static images
- [ ] Test with WebPageTest waterfall view

## Further Reading

- [Core Web Vitals Optimization](./08-core-web-vitals-optimizations.md) - LCP, CLS, INP techniques
- [Image Optimization](./06-image-optimizations.md) - Image compression and formats
- [Performance Lab Plugin](./12-performance-lab.md) - Official WordPress optimizations
- [Debugging & Profiling](./10-debugging-profiling.md) - Finding what's actually slow
