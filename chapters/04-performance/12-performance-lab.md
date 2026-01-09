# Performance Lab Plugin

## Overview

Performance Lab is the official WordPress Core Performance Team's testing ground for performance improvements. Like Gutenberg incubates editor features, Performance Lab develops and validates performance optimizations before they merge into WordPress core.

Installing it helps the team validate improvements with real-world data while giving your site immediate performance benefits.

## Why Use Performance Lab

- **Early access** to optimizations heading to WordPress core
- **Modular design** - install only features you need
- **Battle-tested** by the core team before merge proposals
- **Measurable impact** on Core Web Vitals, especially LCP

## The LCP Problem

WordPress sites struggle most with Largest Contentful Paint (LCP)—the time to render the largest visible content element (usually an image or heading).

**The threshold:** 2.5 seconds for "good" LCP.

**The reality:** Many WordPress sites have 1+ second Time to First Byte (TTFB), leaving only 1.5 seconds for everything else.

Performance Lab plugins specifically target LCP improvements.

## Key Plugins and Their Impact

Based on testing with Twenty Twenty-Five theme:

| Plugin | LCP Improvement | Notes |
|--------|-----------------|-------|
| Enhanced Responsive Images | ~25% | Better `sizes` attribute calculation |
| Image Prioritizer | 27-50% | Proper fetch priority for LCP images |
| Speculative Loading | Near-zero possible | Prefetch/prerender navigation |
| Modern Image Formats | ~2.5% | AVIF/WebP conversion |
| Image Placeholders | 0% | UX improvement only |

### Enhanced Responsive Images

WordPress's default `sizes` attribute is inaccurate—it often downloads images larger than needed, especially on desktop.

**Problem:**
```html
<!-- Default: assumes image might be full viewport width -->
<img sizes="(max-width: 1024px) 100vw, 1024px" ...>
```

**Solution:** The plugin calculates actual container width from block structure:

```html
<!-- After: accurate for column layout -->
<img sizes="(max-width: 600px) 100vw, 300px" ...>
```

**Result:** Up to 90% reduction in downloaded image bytes compared to using only modern formats (30% reduction).

### Image Prioritizer

WordPress can't know which image is the LCP element because PHP doesn't render the page. It guesses—often incorrectly.

**What it does:**
- Removes `fetchpriority="high"` from non-LCP images
- Adds `loading="lazy"` to below-fold images
- Preloads actual LCP images with correct media queries
- Handles background images (CSS) which WordPress can't normally prioritize

**Desktop improvement:** 50% LCP reduction in gallery layouts.

```html
<!-- Responsive LCP preloading -->
<link rel="preload" as="image" href="desktop-hero.jpg" media="(min-width: 768px)">
<link rel="preload" as="image" href="mobile-hero.jpg" media="(max-width: 767px)">
```

### Speculative Loading

Prefetch or prerender links before users click them.

| Mode | Trigger | Result |
|------|---------|--------|
| Conservative prefetch | Mouse down/touch | Faster TTFB |
| Moderate prefetch | Hover (desktop) | Zero TTFB possible |
| Moderate prerender | Hover | Near-zero LCP possible |
| Eager prerender | Page load | Instant navigation |

**WordPress 6.8+ default:** Conservative prefetch (safest option).

**Plugin unlocks:** More aggressive modes for sites with proper caching.

**Compatibility note:** Prerendering may cause issues with analytics/ads that aren't aware of prerendered state. Test carefully.

### Modern Image Formats

Converts uploads to AVIF or WebP automatically.

**Impact:** Smaller files, but only ~2.5% LCP improvement because download time is often not the bottleneck.

**Verdict:** Important for bandwidth, but not the highest-impact optimization.

### Image Placeholders

Shows dominant color background while images load.

**Impact:** Zero LCP improvement (LCP measures when image finishes loading, not when placeholder appears).

**Value:** Better perceived performance and user experience.

## Additional Optimizations

### Script Module Deprioritization

Interactivity API script modules load with high priority by default, competing with LCP resources.

**Fix:** Add `fetchpriority="low"` and move to footer.

**Result:** ~9% LCP improvement.

### CSS Inlining

External stylesheets block rendering. Inlining eliminates render-blocking requests.

```php
// Increase inline limit from default 20kb to 30kb
add_filter( 'styles_inline_size_limit', function() {
    return 30000;
});
```

**Result:** 36-45% LCP improvement on text-heavy pages.

### BF Cache Optimization

Back/forward cache provides instant navigation history—but WordPress disables it for logged-in users.

**New plugin:** Enables BF cache safely with proper invalidation on logout.

**Impact:** Near-zero LCP for 10-20% of page views (back/forward navigations).

## Measuring Performance

### Don't Trust Single Lighthouse Scores

Lighthouse varies significantly between runs. A score of 100 doesn't mean perfect.

**Better approach:** Multiple measurements, take the median.

```bash
# Using WPP Research CLI tool
npx wpp-research benchmark-url \
  --url="https://example.com" \
  --iterations=10 \
  --device=mobile \
  --connection=4g
```

### Lab vs. Field Data

| Type | Source | Use Case |
|------|--------|----------|
| Lab | Lighthouse, WebPageTest | Development, debugging |
| Field | Chrome UX Report (CrUX) | Real user impact |

**Field data is truth.** Lab data helps diagnose issues.

### Page Speed Insights

Shows both:
1. **Field metrics** (CrUX data) - what real users experience
2. **Lab data** (Lighthouse) - controlled test results

Sites with sufficient traffic get historical trend data.

## Installation

```bash
# Via WP-CLI
wp plugin install performance-lab --activate

# Then activate specific feature plugins
wp plugin activate enhanced-responsive-images
wp plugin activate image-prioritizer
wp plugin activate speculative-loading
```

Or install from WordPress admin → Plugins → Add New → search "Performance Lab".

## Classic Theme Compatibility

Most plugins work with classic (non-block) themes:

| Plugin | Block Themes | Classic Themes |
|--------|--------------|----------------|
| Enhanced Responsive Images | ✅ | ❌ (needs block structure) |
| Image Prioritizer | ✅ | ✅ |
| Speculative Loading | ✅ | ✅ |
| Modern Image Formats | ✅ | ✅ |
| Image Placeholders | ✅ | ✅ |

## When to Be Aggressive

**Enable more aggressive optimizations when:**
- Page caching is active
- Object cache (Redis/Memcached) is configured
- Server can handle increased speculative requests
- Analytics/ads are speculation-rules compatible

**Stay conservative when:**
- Shared hosting with limited resources
- No page caching
- Uncertain about third-party script compatibility

## Further Reading

- [Performance Lab on WordPress.org](https://wordpress.org/plugins/performance-lab/)
- [Core Web Vitals Optimization](./08-core-web-vitals-optimizations.md)
- [Image Optimization](./06-image-optimizations.md)
- [Weston Ruter's detailed blog post](https://developer.wordpress.org/news/) - Search for "Site Speed Frontier"
- [Chrome UX Report](https://developer.chrome.com/docs/crux/)
