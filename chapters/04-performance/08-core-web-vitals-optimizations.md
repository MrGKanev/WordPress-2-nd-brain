# Core Web Vitals Optimization

Core Web Vitals are Google's user experience metrics that directly affect search rankings. Unlike general performance scores, these specific metrics measure what users actually experience: loading speed, interactivity, and visual stability.

## Understanding Core Web Vitals

### The Three Metrics (Plus INP)

| Metric | Measures | Good | Needs Improvement | Poor |
|--------|----------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | Loading | ≤ 2.5s | 2.5s - 4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | Responsiveness | ≤ 200ms | 200ms - 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | Visual stability | ≤ 0.1 | 0.1 - 0.25 | > 0.25 |

**Note:** FID (First Input Delay) was replaced by INP in March 2024. INP measures all interactions throughout the page lifecycle, not just the first one.

### Why These Metrics Matter

Google uses Core Web Vitals as a ranking signal. Pages that pass all three thresholds receive a ranking boost. More importantly, poor scores correlate with:

- Higher bounce rates
- Lower conversion rates
- Reduced user engagement
- Negative brand perception

### Lab Data vs Field Data

Understanding this distinction is critical:

| Type | Source | Use Case |
|------|--------|----------|
| **Lab data** | PageSpeed Insights, Lighthouse | Debugging, development testing |
| **Field data** | Chrome User Experience Report (CrUX) | Actual user experience, what Google uses for ranking |

**Lab data can differ significantly from field data.** A page might score well in Lighthouse but fail in CrUX because:
- Real users have slower devices
- Network conditions vary
- User behavior triggers different code paths
- Third-party scripts load differently in production

Always prioritize field data when making optimization decisions.

---

## Largest Contentful Paint (LCP)

LCP measures when the largest visible element finishes rendering. This is typically:

- Hero images
- Featured images on posts
- Large text blocks (if no images above fold)
- Video poster images

### Identifying Your LCP Element

Different templates have different LCP elements:

```
Homepage      → Hero image or slider first slide
Blog post     → Featured image
Product page  → Main product image
Category page → First product image or page title
```

Use Chrome DevTools to identify LCP:
1. Open DevTools → Performance tab
2. Check "Web Vitals" checkbox
3. Record page load
4. Look for the LCP marker in the timeline

### LCP Optimization Techniques

#### 1. Preload the LCP Image

```php
// Add to functions.php - preload hero image on homepage
function preload_lcp_image() {
    if (is_front_page()) {
        $hero_image = get_theme_mod('hero_image_url');
        if ($hero_image) {
            printf(
                '<link rel="preload" href="%s" as="image" fetchpriority="high">',
                esc_url($hero_image)
            );
        }
    }

    // For single posts, preload featured image
    if (is_singular() && has_post_thumbnail()) {
        $thumbnail_id = get_post_thumbnail_id();
        $image_src = wp_get_attachment_image_src($thumbnail_id, 'large');
        if ($image_src) {
            printf(
                '<link rel="preload" href="%s" as="image" fetchpriority="high">',
                esc_url($image_src[0])
            );
        }
    }
}
add_action('wp_head', 'preload_lcp_image', 1);
```

#### 2. Use fetchpriority="high"

Modern browsers support the `fetchpriority` attribute:

```php
// Add fetchpriority to featured images
function add_fetchpriority_to_featured_image($html, $post_id, $post_thumbnail_id) {
    // Only for above-the-fold images
    if (is_singular() && in_the_loop() && is_main_query()) {
        $html = str_replace('<img', '<img fetchpriority="high"', $html);
        // Also remove lazy loading for LCP images
        $html = str_replace('loading="lazy"', '', $html);
    }
    return $html;
}
add_filter('post_thumbnail_html', 'add_fetchpriority_to_featured_image', 10, 3);
```

#### 3. Optimize Server Response Time (TTFB)

LCP cannot be faster than your server response. Target TTFB under 200ms:

| Optimization | Impact | Difficulty |
|--------------|--------|------------|
| Object caching (Redis/Memcached) | High | Medium |
| Full page caching | Very High | Low |
| PHP 8.x upgrade | Medium | Low |
| OPcache tuning | Medium | Low |
| Database optimization | Medium | Medium |
| Better hosting | Very High | $ |

#### 4. Critical CSS

Inline critical CSS to render above-the-fold content immediately:

```php
// Inline critical CSS in head
function inline_critical_css() {
    $critical_css = '
        /* Minimal styles for above-the-fold content */
        body { margin: 0; font-family: system-ui, sans-serif; }
        .header { /* header styles */ }
        .hero { /* hero section styles */ }
    ';
    echo '<style id="critical-css">' . $critical_css . '</style>';
}
add_action('wp_head', 'inline_critical_css', 1);
```

For automated critical CSS generation, use tools like:
- WP Rocket (built-in)
- Critical CSS by flavor/flavor
- PurgeCSS + Critical (build tools)

#### 5. Image Format Optimization

| Format | Use Case | LCP Impact |
|--------|----------|------------|
| WebP | General images, photos | 25-35% smaller than JPEG |
| AVIF | Photos, complex images | 50% smaller than JPEG |
| SVG | Icons, logos, illustrations | Instant render, no decode |

```php
// Serve WebP with fallback
function webp_upload_mimes($mimes) {
    $mimes['webp'] = 'image/webp';
    $mimes['avif'] = 'image/avif';
    return $mimes;
}
add_filter('upload_mimes', 'webp_upload_mimes');
```

### Common LCP Problems in WordPress

| Problem | Symptom | Solution |
|---------|---------|----------|
| Lazy-loaded LCP image | LCP delayed until scroll | Exclude above-fold images from lazy loading |
| Render-blocking CSS | White screen before content | Inline critical CSS, async non-critical |
| Slow TTFB | Everything delayed | Server optimization, caching |
| Large hero image | Long download time | Resize, compress, use modern formats |
| Web fonts blocking render | Text invisible during load | font-display: swap, preload fonts |

---

## Interaction to Next Paint (INP)

INP replaced FID in March 2024. While FID only measured the first interaction, INP measures **all interactions** and reports the worst one (roughly the 98th percentile).

### Why INP is Harder to Optimize

1. **Happens throughout the page lifecycle** — not just on initial load
2. **Affected by any JavaScript** — even scripts loaded late
3. **Includes visual feedback time** — not just input processing
4. **Real user behavior varies** — lab tests may not trigger the slow paths

### What Counts as an Interaction

- Clicks (mouse, touch, pen)
- Taps (mobile)
- Key presses

**Not counted:** Scrolling, hovering, pinch-zoom

### INP Measurement Breakdown

```
INP = Input Delay + Processing Time + Presentation Delay

Input Delay:       Time from user action to event handler start
Processing Time:   Time spent in event handlers
Presentation Delay: Time from handler completion to next paint
```

### Identifying INP Issues

#### Chrome DevTools Method

1. Open DevTools → Performance tab
2. Enable "Web Vitals" lane
3. Record while interacting with the page
4. Click various elements, open menus, fill forms
5. Look for long tasks (>50ms) during interactions

#### Web Vitals Extension

Install the [Web Vitals Chrome extension](https://chrome.google.com/webstore/detail/web-vitals/ahfhijdlegdabablpippeagghigmibma) for real-time INP monitoring:

- Shows INP value after each interaction
- Logs interaction details to console
- Helps identify which interactions are slowest

#### Search Console

Check Search Console → Core Web Vitals → INP for field data across your site.

### Common INP Problems in WordPress

#### 1. Page Builder JavaScript

Page builders (Elementor, Divi, WPBakery) add significant JavaScript:

```
Elementor: ~200-400KB JS
Divi: ~300-500KB JS
WPBakery: ~200-350KB JS
```

**Solutions:**
- Use lighter alternatives (Gutenberg, GenerateBlocks, Kadence Blocks)
- Disable unused widgets/elements
- Use "Improved Asset Loading" (Elementor 3.0+)
- Consider static HTML for simple pages

#### 2. Analytics and Tracking Scripts

Google Analytics, Facebook Pixel, and other tracking scripts often cause INP issues:

```javascript
// BAD: Synchronous tracking on every click
element.addEventListener('click', function() {
    gtag('event', 'click', { /* data */ }); // Blocks main thread
    // Rest of handler
});

// GOOD: Async tracking with requestIdleCallback
element.addEventListener('click', function() {
    // Do critical work first

    // Track asynchronously
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
            gtag('event', 'click', { /* data */ });
        });
    } else {
        setTimeout(() => {
            gtag('event', 'click', { /* data */ });
        }, 0);
    }
});
```

#### 3. Heavy Click Handlers

```javascript
// BAD: Heavy computation on click
document.querySelector('.filter-btn').addEventListener('click', function() {
    const products = document.querySelectorAll('.product'); // 1000 products
    products.forEach(product => {
        // Complex filtering logic on each product
        // This blocks the main thread
    });
});

// GOOD: Chunked processing with visual feedback
document.querySelector('.filter-btn').addEventListener('click', async function() {
    // Show loading state immediately
    this.classList.add('loading');

    // Yield to browser for paint
    await new Promise(resolve => requestAnimationFrame(resolve));

    // Process in chunks
    const products = Array.from(document.querySelectorAll('.product'));
    const chunkSize = 50;

    for (let i = 0; i < products.length; i += chunkSize) {
        const chunk = products.slice(i, i + chunkSize);
        chunk.forEach(product => {
            // Filter logic
        });

        // Yield between chunks
        if (i + chunkSize < products.length) {
            await new Promise(resolve => setTimeout(resolve, 0));
        }
    }

    this.classList.remove('loading');
});
```

#### 4. Third-Party Scripts

Common offenders:
- Chat widgets (Intercom, Drift, LiveChat)
- Social sharing buttons
- Comment systems (Disqus)
- Video embeds (YouTube, Vimeo)

**Solution: Delay until interaction**

```javascript
// Delay third-party scripts until user interaction
let scriptsLoaded = false;

function loadDeferredScripts() {
    if (scriptsLoaded) return;
    scriptsLoaded = true;

    // Load chat widget
    const chatScript = document.createElement('script');
    chatScript.src = 'https://widget.intercom.io/widget/xxx';
    document.body.appendChild(chatScript);

    // Load other deferred scripts...
}

// Trigger on first interaction
['mousemove', 'touchstart', 'scroll', 'keydown'].forEach(event => {
    window.addEventListener(event, loadDeferredScripts, { once: true, passive: true });
});

// Also load after timeout as fallback
setTimeout(loadDeferredScripts, 5000);
```

#### 5. WordPress Admin Bar

The admin bar adds ~100KB of assets and several event listeners:

```php
// Remove admin bar for non-editors (improves INP for logged-in users)
function remove_admin_bar_for_subscribers() {
    if (!current_user_can('edit_posts')) {
        show_admin_bar(false);
    }
}
add_action('after_setup_theme', 'remove_admin_bar_for_subscribers');
```

### INP Optimization Checklist

1. **Audit event listeners** — Use Chrome DevTools → Elements → Event Listeners
2. **Break up long tasks** — Any task >50ms should be chunked
3. **Provide visual feedback** — Show loading states immediately on interaction
4. **Delay non-critical scripts** — Especially third-party widgets
5. **Optimize main thread** — Reduce JavaScript, use Web Workers for heavy computation
6. **Test real interactions** — Don't just test page load, test clicking, typing, navigating

---

## Cumulative Layout Shift (CLS)

CLS measures unexpected layout shifts during the page lifecycle. It's calculated as:

```
CLS = Impact Fraction × Distance Fraction
```

- **Impact Fraction:** How much of the viewport was affected
- **Distance Fraction:** How far elements moved

### Expected vs Unexpected Shifts

**Expected shifts (don't count toward CLS):**
- User-initiated (clicking a button that expands content)
- Animations using `transform` (not layout properties)
- Shifts within 500ms of user interaction

**Unexpected shifts (count toward CLS):**
- Images loading without dimensions
- Ads/embeds injecting content
- Fonts causing text reflow
- Dynamic content insertion

### CLS Optimization Techniques

#### 1. Always Specify Image Dimensions

```php
// WordPress 5.5+ adds dimensions automatically, but verify your theme uses them
function ensure_image_dimensions($attr, $attachment, $size) {
    if (empty($attr['width']) || empty($attr['height'])) {
        $image_meta = wp_get_attachment_metadata($attachment->ID);
        if ($image_meta) {
            $attr['width'] = $image_meta['width'];
            $attr['height'] = $image_meta['height'];
        }
    }
    return $attr;
}
add_filter('wp_get_attachment_image_attributes', 'ensure_image_dimensions', 10, 3);
```

#### 2. Reserve Space for Ads

```css
/* Reserve space for common ad sizes */
.ad-container-leaderboard {
    min-height: 90px;  /* 728x90 leaderboard */
    width: 100%;
    max-width: 728px;
}

.ad-container-sidebar {
    min-height: 250px; /* 300x250 medium rectangle */
    width: 100%;
    max-width: 300px;
}

/* Use aspect-ratio for responsive ads */
.ad-container-responsive {
    aspect-ratio: 728 / 90;
    width: 100%;
}
```

#### 3. Font Loading Strategy

```css
/* Use font-display: swap to prevent invisible text */
@font-face {
    font-family: 'CustomFont';
    src: url('font.woff2') format('woff2');
    font-display: swap; /* Show fallback immediately, swap when loaded */
}

/* Or use optional for non-critical fonts */
@font-face {
    font-family: 'DecorativeFont';
    src: url('decorative.woff2') format('woff2');
    font-display: optional; /* Only use if already cached */
}
```

Preload critical fonts:

```php
function preload_fonts() {
    echo '<link rel="preload" href="' . get_theme_file_uri('fonts/main.woff2') . '" as="font" type="font/woff2" crossorigin>';
}
add_action('wp_head', 'preload_fonts', 1);
```

#### 4. Prevent Content Injection Shifts

```css
/* Reserve space for dynamically loaded content */
.comments-section {
    min-height: 200px; /* Approximate height when loaded */
}

.related-posts {
    min-height: 300px;
}

/* Better: Use skeleton loaders */
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

#### 5. Use Transform for Animations

```css
/* BAD: Causes layout shift */
.element {
    transition: margin-top 0.3s, height 0.3s;
}
.element.active {
    margin-top: 20px;
    height: 200px;
}

/* GOOD: No layout shift */
.element {
    transition: transform 0.3s;
}
.element.active {
    transform: translateY(20px) scaleY(1.5);
}
```

### Common CLS Problems in WordPress

| Problem | Cause | Solution |
|---------|-------|----------|
| Cookie consent banners | Injected at page load | Reserve space or use non-blocking position |
| Sticky headers | Height changes on scroll | Fixed height, use transform for show/hide |
| Lazy-loaded images | No dimensions reserved | Always include width/height |
| Web font flash | FOUT/FOIT | font-display: swap + preload |
| Above-fold ads | Late-loading ad scripts | Reserve exact space, use placeholders |
| Dynamic navigation | Menu items loading async | Static HTML or skeleton |

---

## Mobile vs Desktop Optimization

Mobile and desktop often have different performance characteristics.

### Why Mobile is Usually Worse

1. **Slower processors** — 2-4x slower than desktop
2. **Network variability** — 3G/4G is slower and less consistent than WiFi
3. **Thermal throttling** — Phones slow down when hot
4. **Different user behavior** — More tapping, more scrolling

### Mobile-Specific Optimizations

#### Reduce JavaScript for Mobile

```php
// Conditionally load scripts
function load_conditional_scripts() {
    // Skip heavy scripts on mobile
    if (wp_is_mobile()) {
        wp_dequeue_script('heavy-animation-library');
        wp_dequeue_script('fancy-slider');
    }
}
add_action('wp_enqueue_scripts', 'load_conditional_scripts', 100);
```

#### Simpler Mobile Layouts

```css
/* Reduce complexity on mobile */
@media (max-width: 768px) {
    /* Disable complex animations */
    .fancy-animation {
        animation: none;
        transform: none;
    }

    /* Simpler grid layouts */
    .complex-grid {
        display: block; /* Instead of complex CSS Grid */
    }

    /* Hide non-essential elements */
    .decorative-element,
    .sidebar-widget {
        display: none;
    }
}
```

#### Touch Event Optimization

Mobile devices have a 300ms delay on click events by default:

```css
/* Remove touch delay */
html {
    touch-action: manipulation;
}
```

---

## Debugging Workflow

### Step 1: Measure Current State

1. **PageSpeed Insights** — Get baseline lab data
2. **Search Console** — Check field data (what Google sees)
3. **CrUX Dashboard** — Historical trends

### Step 2: Identify the Problem

Use Chrome DevTools Performance panel:

1. Open DevTools → Performance
2. Enable "Web Vitals" checkbox
3. Set CPU throttling to 4x (simulates mid-tier mobile)
4. Set Network to "Fast 3G"
5. Record page load
6. Interact with the page (click buttons, open menus)
7. Stop recording

Look for:
- Long tasks (>50ms) in the main thread
- LCP marker timing
- Layout shift markers (red bars)
- Interaction timing

### Step 3: Prioritize Fixes

Address issues in this order (highest impact first):

1. **Server response time** — Affects everything
2. **LCP resource** — Preload, optimize, remove blockers
3. **Render-blocking resources** — Critical CSS, defer JS
4. **CLS issues** — Quick wins, usually CSS-only fixes
5. **INP issues** — Often requires JS refactoring

### Step 4: Test and Verify

After each change:
1. Clear all caches (browser, server, CDN)
2. Test in incognito mode
3. Run PageSpeed Insights
4. Test on real mobile device if possible
5. Wait for field data to update (takes 28 days)

---

## Plugin Recommendations

### Performance Optimization Plugins

| Plugin | Strength | Caveat |
|--------|----------|--------|
| **WP Rocket** | All-in-one, Critical CSS, delay JS | Paid ($59/year) |
| **FlyingPress** | INP-focused, lighter | Paid ($60/year) |
| **Perfmatters** | Granular script control | Paid ($24.95/year) |
| **LiteSpeed Cache** | Free, requires LiteSpeed server | Server-specific |
| **W3 Total Cache** | Free, highly configurable | Complex setup |

### Testing Tools

- [PageSpeed Insights](https://pagespeed.web.dev/) — Lab + field data
- [WebPageTest](https://www.webpagetest.org/) — Detailed waterfall analysis
- [Chrome UX Report](https://developer.chrome.com/docs/crux/) — Real user data
- [Treo](https://treo.sh/) — CrUX visualization and monitoring

---

## Common Misconceptions

### "I need a 100/100 score"

No. Google doesn't use the Lighthouse score for ranking. A site with a 60 score can rank higher than a 90 if its Core Web Vitals are better.

### "Mobile and desktop scores should match"

They won't. Mobile is inherently slower. Focus on passing Core Web Vitals thresholds on both, not matching scores.

### "One optimization plugin will fix everything"

Plugins help, but they can't fix:
- Bad hosting
- Bloated themes
- Too many plugins
- Unoptimized images

### "Lab data and field data should match"

They measure different things. Lab data is synthetic; field data is real users. A page might score 90 in lab but fail in field because real users have slower devices.

### "JS delay fixes all INP issues"

Delaying JavaScript can actually hurt INP. If a user clicks before scripts load, the interaction waits for download + parse + execute. Use delay strategically, not universally.

---

## Quick Wins Checklist

### LCP
- [ ] Preload LCP image with `fetchpriority="high"`
- [ ] Remove lazy loading from above-fold images
- [ ] Enable page caching
- [ ] Use WebP/AVIF images
- [ ] Inline critical CSS

### INP
- [ ] Delay non-essential third-party scripts
- [ ] Remove unused JavaScript
- [ ] Break up long event handlers
- [ ] Provide immediate visual feedback on interactions

### CLS
- [ ] Add width/height to all images
- [ ] Reserve space for ads and embeds
- [ ] Use `font-display: swap`
- [ ] Preload critical fonts
- [ ] Avoid inserting content above existing content

## Further Reading

- [Performance for SEO](../05-seo/04-performance-for-seo.md) — How Core Web Vitals affect search rankings
- [Debugging & Profiling](./10-debugging-profiling.md) — Deep dive into performance debugging
- [Image Optimization](./06-image-optimizations.md) — Critical for LCP improvement
- [Frontend Asset Optimization](./11-frontend-asset-optimization.md) — CSS/JS optimization techniques
- [web.dev Core Web Vitals](https://web.dev/vitals/) — Google's official documentation
