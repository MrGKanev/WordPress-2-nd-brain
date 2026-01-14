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

### Font Splitting (Unicode Range Subsetting)

Large fonts like CJK (Chinese, Japanese, Korean) can be 10+ MB. Split them into subsets that load on-demand based on characters used.

**How Google Fonts does it:**

Google Fonts splits Noto Sans JP (Japanese) into 120+ subsets. Only subsets containing characters on the page are downloaded.

```css
/* Google serves rules like this */
@font-face {
    font-family: 'Noto Sans JP';
    font-style: normal;
    font-weight: 400;
    src: url(/fonts/noto-jp-subset-1.woff2) format('woff2');
    unicode-range: U+4E00-4E9F;  /* Only these characters */
}

@font-face {
    font-family: 'Noto Sans JP';
    font-style: normal;
    font-weight: 400;
    src: url(/fonts/noto-jp-subset-2.woff2) format('woff2');
    unicode-range: U+4EA0-4EFF;  /* Different character range */
}
```

**Creating your own subsets:**

Using [font-range](https://github.com/nicholasgriffintn/font-ranger):

```bash
npm install -g font-ranger

# Split font by Unicode ranges
font-ranger -f NotoSansJP-Regular.otf -o output/ -s
```

Using [glyphhanger](https://github.com/filamentgroup/glyphhanger):

```bash
npm install -g glyphhanger

# Analyze what characters a page uses
glyphhanger https://example.com/

# Create subset with only needed characters
glyphhanger --subset=*.ttf --whitelist="ABC123" --formats=woff2
```

**For Latin fonts:** Usually unnecessary—woff2 compression is efficient. Subset CJK and other large character sets.

## CSS Performance Tips

### Modern Flexbox vs Legacy

Old flexbox syntax (`display: box`) is **2x slower** than modern flexbox:

```css
/* OLD - Avoid */
.container {
    display: -webkit-box;
    display: -ms-flexbox;
    -webkit-box-orient: horizontal;
    -webkit-box-pack: center;
}

/* MODERN - Use this */
.container {
    display: flex;
    justify-content: center;
}
```

If you're using autoprefixer, ensure it's not adding legacy prefixes unnecessarily:

```javascript
// postcss.config.js
module.exports = {
    plugins: [
        require('autoprefixer')({
            flexbox: 'no-2009'  // Skip legacy flexbox
        })
    ]
};
```

### CSS Specificity Optimization

Lower specificity = faster selector matching and easier overrides:

```css
/* HIGH specificity (slow, hard to override) */
#main-content .article-list .article-card .card-title a:hover { }

/* LOW specificity (fast, maintainable) */
.card-title-link:hover { }
```

**Specificity order:** `[IDs], [Classes], [Tags]`

- `#id` = `1,0,0`
- `.class` = `0,1,0`
- `element` = `0,0,1`

Avoid `!important` except for utility classes—it indicates specificity problems.

### Mobile-First Media Queries

Load base styles for mobile, then enhance for larger screens:

```css
/* Base: Mobile */
.container {
    width: 100%;
    padding: 1rem;
}

/* Tablet and up */
@media (min-width: 768px) {
    .container {
        width: 750px;
        padding: 2rem;
    }
}

/* Desktop */
@media (min-width: 1200px) {
    .container {
        width: 1140px;
    }
}
```

**Benefits:**
- Mobile users download only mobile CSS
- No overriding needed for small screens
- Progressive enhancement pattern

### Avoid Expensive CSS Properties

Some CSS properties trigger expensive repaints or reflows:

| Property | Impact | Alternative |
|----------|--------|-------------|
| `box-shadow` (large blur) | Repaint | Use subtle shadows |
| `filter: blur()` | Repaint | Limit to small areas |
| `position: fixed` (with transforms) | Composite layer | Use sparingly |
| `width`/`height` animations | Reflow | Use `transform: scale()` |
| `top`/`left` animations | Reflow | Use `transform: translate()` |

**GPU-accelerated (prefer these for animations):**
- `transform`
- `opacity`
- `filter`

## Validation and Accessibility

### HTML Validation

Valid HTML parses faster and renders more predictably:

**Tools:**
- [W3C Validator](https://validator.w3.org/) - Official HTML validator
- [Nu Html Checker](https://validator.w3.org/nu/) - Modern HTML5 validator

**Common issues affecting performance:**
- Unclosed tags causing DOM parser recovery
- Invalid nesting triggering layout recalculation
- Missing doctype forcing quirks mode

**Validate programmatically:**

```bash
# Install vnu (Nu Html Checker)
npm install -g vnu-jar

# Validate a file
vnu-jar path/to/file.html

# Validate URL
curl -s https://example.com/ | vnu-jar -
```

### CSS Validation

- [W3C CSS Validator](https://jigsaw.w3.org/css-validator/)

Invalid CSS causes parsing errors and unpredictable rendering.

### Accessibility Testing

Accessibility issues often indicate performance-affecting DOM problems:

**Tools:**
- [WAVE](https://wave.webaim.org/) - Browser extension and API
- [axe DevTools](https://www.deque.com/axe/) - Chrome/Firefox extension
- [Lighthouse Accessibility](https://developer.chrome.com/docs/lighthouse/accessibility/) - Built into Chrome

**WordPress-specific:**

```bash
# Test with pa11y
npm install -g pa11y
pa11y https://example.com/

# Test WordPress admin
pa11y https://example.com/wp-admin/ --ignore "color-contrast"
```

**Quick accessibility wins that also improve performance:**
- Add `alt` attributes (screen readers + SEO)
- Use semantic HTML (cleaner DOM)
- Ensure sufficient color contrast (no need for larger text)
- Add `lang` attribute to `<html>` (faster parsing)

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

**Process for Font Awesome extraction:**
1. Download Font Awesome's SVG files
2. Upload only needed icons to IcoMoon
3. Export as custom font (select woff2 format)
4. Preload the custom font:

```html
<link rel="preload" href="/fonts/custom-icons.woff2" as="font" type="font/woff2" crossorigin>
```

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

## Framework Optimization

### Bootstrap Trimming

Many themes include all of Bootstrap when only the grid system is used:

| What You Load | Size |
|---------------|------|
| Full Bootstrap CSS | ~190KB |
| Bootstrap Grid only | ~50KB |
| Custom build (grid + utilities) | ~30-60KB |

**Use grid-only build:**
```php
// Replace full Bootstrap with grid-only
wp_dequeue_style( 'bootstrap' );
wp_enqueue_style( 'bootstrap-grid', 'path/to/bootstrap-grid.min.css' );
```

**Build custom Bootstrap:**
1. Clone Bootstrap source
2. Edit `scss/bootstrap.scss`
3. Comment out unused imports:
```scss
// Core (keep)
@import "functions";
@import "variables";
@import "mixins";
@import "grid";
@import "utilities";

// Components (comment out what you don't use)
// @import "carousel";
// @import "modal";
// @import "tooltip";
```
4. Compile: `npm run css`

This approach works for any SCSS-based framework.

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

## WordPress Core Caching Tricks

Some overhead comes from WordPress core operations that can be cached.

### Translation File Caching

WordPress parses `.mo` translation files on every page load using PHP's `unpack()` function. For sites with many translations, this adds measurable overhead.

**The impact:** One test showed 168,000 function calls reduced to 360, and 3.3 seconds reduced to 146ms—just by caching parsed translations.

**Solution:** Use an mu-plugin that caches parsed translations:

```php
<?php
/**
 * Plugin Name: MO Cache
 * Description: Caches parsed .mo files to avoid repeated parsing
 */

add_filter( 'override_load_textdomain', function( $override, $domain, $mofile ) {
    global $l10n;

    if ( ! is_readable( $mofile ) ) {
        return false;
    }

    $cache_key = 'mo_' . md5( $mofile );
    $data = get_transient( $cache_key );

    if ( false === $data ) {
        // Parse the MO file normally
        $mo = new MO();
        if ( ! $mo->import_from_file( $mofile ) ) {
            return false;
        }

        // Cache the entries
        $data = $mo->entries;
        set_transient( $cache_key, $data, DAY_IN_SECONDS );
    }

    // Restore from cache
    $mo = new MO();
    $mo->entries = $data;

    if ( isset( $l10n[ $domain ] ) ) {
        $mo->merge_with( $l10n[ $domain ] );
    }

    $l10n[ $domain ] = &$mo;

    return true;
}, 10, 3 );
```

**Note:** Clear transients when updating translations or plugins.

### Menu Caching

Navigation menus trigger multiple database queries on every page load. For complex menus, this adds up.

**Cache the rendered menu:**

```php
function get_cached_menu( $location, $args = array() ) {
    $cache_key = 'nav_menu_' . $location . '_' . md5( serialize( $args ) );
    $menu = get_transient( $cache_key );

    if ( false === $menu ) {
        $args['echo'] = false;
        $args['theme_location'] = $location;
        $menu = wp_nav_menu( $args );
        set_transient( $cache_key, $menu, HOUR_IN_SECONDS );
    }

    return $menu;
}

// Usage in theme
echo get_cached_menu( 'primary', array( 'container' => 'nav' ) );
```

**Clear on menu update:**

```php
add_action( 'wp_update_nav_menu', function() {
    global $wpdb;
    $wpdb->query(
        "DELETE FROM {$wpdb->options}
         WHERE option_name LIKE '_transient_nav_menu_%'
         OR option_name LIKE '_transient_timeout_nav_menu_%'"
    );
});
```

**When to use:** Sites with complex menus (50+ items) or many submenus. Simple menus won't see significant benefit.

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
