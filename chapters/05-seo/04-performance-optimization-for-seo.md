# Performance Optimization for SEO

## Overview

Site performance is a confirmed Google ranking factor. While content quality remains paramount, performance directly impacts user experience signals, crawl efficiency, and ultimately, search rankings. This chapter covers the SEO-specific aspects of performance optimization for WordPress sites.

> **Note:** For technical implementation details of Core Web Vitals optimizations, see [Core Web Vitals Optimization](../04-performance/08-core-web-vitals-optimizations.md). This chapter focuses on how performance metrics affect SEO specifically.

> **Key insight**: Performance optimization for SEO is not about achieving a perfect PageSpeed score. It's about ensuring your site meets Google's thresholds for Core Web Vitals and provides a good user experience that keeps visitors engaged.

## How Google Uses Performance in Rankings

### Page Experience as a Ranking Signal

Google's Page Experience update consolidated several user experience signals into ranking factors:

| Signal | Description | SEO Impact |
|--------|-------------|------------|
| **Core Web Vitals** | LCP, FID/INP, CLS metrics | Direct ranking factor |
| **Mobile-friendliness** | Responsive design, touch targets | Required for mobile rankings |
| **HTTPS** | Secure connection | Baseline requirement |
| **No intrusive interstitials** | Avoiding aggressive popups | Can demote rankings |
| **Safe Browsing** | No malware or deceptive content | Can remove from index |

### The Real Impact of Performance on Rankings

Performance is a **tie-breaker** ranking factor, not a dominant one. This means:

1. **Content quality still wins** - A slower site with better content will outrank a faster site with poor content
2. **Thresholds matter more than scores** - Meeting "Good" thresholds is what counts, not getting 100/100
3. **Poor performance hurts more than good performance helps** - Failing Core Web Vitals can demote you; passing them maintains your position

```
Google's Core Web Vitals Thresholds:
┌─────────────────────────────────────────────────┐
│ Metric │  Good    │ Needs Improvement │  Poor  │
├─────────────────────────────────────────────────┤
│ LCP    │  ≤2.5s   │    2.5s - 4s      │  >4s   │
│ INP    │  ≤200ms  │   200ms - 500ms   │ >500ms │
│ CLS    │  ≤0.1    │    0.1 - 0.25     │ >0.25  │
└─────────────────────────────────────────────────┘
```

## Mobile-First Indexing and Performance

Since Google predominantly uses mobile content for indexing, mobile performance is critical for SEO.

### Mobile Performance Priorities

1. **Mobile-specific LCP optimization**
   - Mobile hero images should be appropriately sized (not desktop images scaled down)
   - Consider different LCP elements for mobile vs desktop

2. **Touch responsiveness (INP)**
   - Mobile interactions must respond quickly
   - Avoid JavaScript that blocks the main thread

3. **Viewport stability (CLS)**
   - Mobile layouts are more susceptible to layout shifts
   - Ad placements on mobile require careful consideration

### WordPress Mobile Performance Checklist

```php
// Serve different image sizes for mobile vs desktop
function responsive_hero_image() {
    ?>
    <picture>
        <source media="(max-width: 768px)"
                srcset="<?php echo get_template_directory_uri(); ?>/images/hero-mobile.webp">
        <source media="(min-width: 769px)"
                srcset="<?php echo get_template_directory_uri(); ?>/images/hero-desktop.webp">
        <img src="<?php echo get_template_directory_uri(); ?>/images/hero-desktop.webp"
             alt="Hero image"
             width="1200"
             height="600"
             fetchpriority="high">
    </picture>
    <?php
}
```

## Crawl Budget Optimization

For larger WordPress sites, performance directly affects how efficiently Google crawls your content.

### What Affects Crawl Budget

| Factor | Impact | WordPress Solution |
|--------|--------|-------------------|
| **Server response time** | Slow TTFB = fewer pages crawled | Better hosting, caching |
| **Page size** | Large pages = slower crawling | Image optimization, code minification |
| **Duplicate content** | Wasted crawl budget | Canonical tags, proper redirects |
| **Soft 404 errors** | Crawl budget waste | Fix or remove thin content |
| **Infinite URL spaces** | Calendar archives, filters | robots.txt, noindex |

### WordPress Crawl Budget Best Practices

```php
// Prevent crawling of low-value WordPress pages
// Add to functions.php

// Noindex paginated archive pages beyond page 2
function noindex_deep_pagination() {
    if (is_paged() && get_query_var('paged') > 2) {
        echo '<meta name="robots" content="noindex, follow">';
    }
}
add_action('wp_head', 'noindex_deep_pagination');

// Noindex search results
function noindex_search_results() {
    if (is_search()) {
        echo '<meta name="robots" content="noindex, follow">';
    }
}
add_action('wp_head', 'noindex_search_results');
```

### Managing Faceted Navigation and Filters

For WooCommerce or sites with filters:

```
# robots.txt additions for filter URLs
User-agent: *
Disallow: /*?orderby=
Disallow: /*?filter_
Disallow: /*?min_price=
Disallow: /*?max_price=
```

## Server Response Time (TTFB) for SEO

Time To First Byte directly impacts both user experience and crawl efficiency.

### TTFB Targets for SEO

| TTFB | Rating | SEO Impact |
|------|--------|------------|
| < 200ms | Excellent | Optimal crawling, great UX |
| 200-500ms | Good | Acceptable for most sites |
| 500-1000ms | Needs work | May affect crawl rate |
| > 1000ms | Poor | Significant SEO impact |

### WordPress TTFB Optimization Stack

Priority order for TTFB improvement:

1. **Hosting quality** - The foundation; no optimization compensates for poor hosting
2. **Full-page caching** - Serve static HTML instead of executing PHP
3. **Object caching** - Redis/Memcached for database query caching
4. **PHP version** - PHP 8.2+ offers significant performance improvements
5. **Database optimization** - Clean transients, optimize tables, proper indexing

```php
// Check TTFB in WordPress (add to functions.php for debugging)
function log_page_generation_time() {
    if (defined('WP_DEBUG') && WP_DEBUG) {
        global $timestart;
        $time = microtime(true) - $timestart;
        error_log('Page generated in: ' . round($time * 1000) . 'ms');
    }
}
add_action('shutdown', 'log_page_generation_time');
```

## Render-Blocking Resources and SEO

Search engines increasingly render JavaScript, making render performance SEO-relevant.

### Critical Rendering Path for SEO

```
Browser Request → TTFB → HTML Parse → CSS/JS Download → Render → Interactive
                                          ↑
                              Render-blocking resources delay this
```

### WordPress Solutions for Render-Blocking

```php
// Defer non-critical JavaScript
function defer_parsing_of_js($tag, $handle, $src) {
    // Don't defer critical scripts
    $no_defer = array('jquery-core', 'jquery-migrate');

    if (in_array($handle, $no_defer)) {
        return $tag;
    }

    // Don't defer admin scripts
    if (is_admin()) {
        return $tag;
    }

    return str_replace(' src=', ' defer src=', $tag);
}
add_filter('script_loader_tag', 'defer_parsing_of_js', 10, 3);

// Async load non-critical CSS
function async_load_css($html, $handle, $href, $media) {
    // Keep critical styles synchronous
    $sync_styles = array('main-style', 'critical-css');

    if (in_array($handle, $sync_styles) || is_admin()) {
        return $html;
    }

    // Use media="print" trick for async CSS loading
    $async_css = '<link rel="stylesheet" id="' . $handle . '-css" href="' . $href . '" media="print" onload="this.media=\'all\'">';
    $async_css .= '<noscript>' . $html . '</noscript>';

    return $async_css;
}
add_filter('style_loader_tag', 'async_load_css', 10, 4);
```

## Image Optimization for SEO

Images often account for the largest portion of page weight and directly impact LCP.

### Image SEO Best Practices

| Aspect | Best Practice | WordPress Implementation |
|--------|--------------|-------------------------|
| **Format** | WebP/AVIF with fallbacks | Use a plugin like ShortPixel or Imagify |
| **Sizing** | Serve appropriately sized images | WordPress srcset + sizes attributes |
| **Lazy loading** | Defer off-screen images | Native `loading="lazy"` (WP 5.5+) |
| **LCP image** | Eager load above-fold images | `fetchpriority="high"` + no lazy load |
| **Alt text** | Descriptive, keyword-relevant | Always fill in alt attributes |

### LCP Image Optimization

```php
// Preload LCP image and disable lazy loading for it
function optimize_lcp_image() {
    // Only on front page or specific templates
    if (!is_front_page()) {
        return;
    }

    // Preload the hero image
    $hero_image = get_template_directory_uri() . '/images/hero.webp';
    echo '<link rel="preload" as="image" href="' . esc_url($hero_image) . '">';
}
add_action('wp_head', 'optimize_lcp_image', 1);

// Remove lazy loading from above-fold images
function remove_lazy_load_from_lcp($attr, $attachment, $size) {
    // Check if this is an LCP candidate (e.g., featured image on single posts)
    if (is_singular() && has_post_thumbnail() && $attachment->ID === get_post_thumbnail_id()) {
        $attr['loading'] = 'eager';
        $attr['fetchpriority'] = 'high';
    }
    return $attr;
}
add_filter('wp_get_attachment_image_attributes', 'remove_lazy_load_from_lcp', 10, 3);
```

## Measuring Performance for SEO

### Essential Tools

| Tool | Purpose | Frequency |
|------|---------|-----------|
| **Google Search Console** | Field data, aggregate Core Web Vitals | Weekly |
| **PageSpeed Insights** | Lab + Field data per URL | After changes |
| **Chrome UX Report** | Historical performance trends | Monthly |
| **Web Vitals Extension** | Real-time testing during development | During development |

### Setting Up Performance Monitoring

```php
// Add performance marks for debugging (development only)
function add_performance_marks() {
    if (!defined('WP_DEBUG') || !WP_DEBUG) {
        return;
    }
    ?>
    <script>
    // Mark when DOM is interactive
    document.addEventListener('DOMContentLoaded', function() {
        performance.mark('dom-interactive');
    });

    // Mark when page is fully loaded
    window.addEventListener('load', function() {
        performance.mark('page-loaded');

        // Log Core Web Vitals
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                console.log('[CWV]', entry.name, entry.value);
            }
        }).observe({type: 'largest-contentful-paint', buffered: true});
    });
    </script>
    <?php
}
add_action('wp_head', 'add_performance_marks');
```

## Common WordPress Performance Issues Affecting SEO

### Plugin Bloat

Every plugin adds potential overhead:

```php
// Audit plugin impact on page load
// Add to wp-config.php temporarily for debugging
define('SAVEQUERIES', true);

// Then in footer.php or via a custom plugin:
function debug_plugin_queries() {
    if (!current_user_can('manage_options')) return;

    global $wpdb;
    echo '<!-- Total queries: ' . count($wpdb->queries) . ' -->';
    echo '<!-- Total query time: ' . array_sum(array_column($wpdb->queries, 1)) . 's -->';
}
add_action('wp_footer', 'debug_plugin_queries');
```

### Database Optimization

Slow database queries hurt TTFB:

```sql
-- Find slow queries (run in phpMyAdmin or CLI)
-- These are common WordPress tables that grow large

-- Clean post revisions (keep last 5 per post)
DELETE FROM wp_posts
WHERE post_type = 'revision'
AND ID NOT IN (
    SELECT * FROM (
        SELECT ID FROM wp_posts
        WHERE post_type = 'revision'
        ORDER BY post_date DESC
        LIMIT 5
    ) AS t
);

-- Clean expired transients
DELETE FROM wp_options
WHERE option_name LIKE '%_transient_%'
AND option_name NOT LIKE '%_transient_timeout_%';

-- Optimize tables
OPTIMIZE TABLE wp_posts, wp_postmeta, wp_options, wp_comments;
```

## Performance and E-E-A-T

While not directly related to technical metrics, performance affects perceived quality:

1. **Experience** - Fast sites demonstrate technical competence
2. **Expertise** - Professional sites are expected to load quickly
3. **Authoritativeness** - Slow sites undermine authority
4. **Trustworthiness** - Users trust fast, professional experiences

## Implementation Priority for SEO

When optimizing performance for SEO, prioritize in this order:

1. **Fix failing Core Web Vitals** - Address any metrics in "Poor" range first
2. **Improve TTFB** - Often the biggest bang for buck
3. **Optimize LCP** - Usually the most visible metric
4. **Fix CLS issues** - Prevents frustrating user experiences
5. **Address INP** - Important but often hardest to fix
6. **Reduce render-blocking resources** - Improves perceived performance
7. **Implement advanced optimizations** - Resource hints, service workers, etc.

## Further Reading

For detailed technical implementation of Core Web Vitals optimizations, see [Core Web Vitals Optimization](../04-performance/08-core-web-vitals-optimizations.md).

For PHP and server-level optimizations, see [PHP Optimization](../04-performance/02-php-optimization.md).
