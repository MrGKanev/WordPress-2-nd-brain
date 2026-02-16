# CDN Strategy

A CDN (Content Delivery Network) caches your site's static assets on servers distributed worldwide. When a visitor in Tokyo loads your site hosted in Amsterdam, they get assets from a nearby edge server instead of waiting for a transatlantic round trip. The result: faster load times, lower server load, and better resilience.

## How CDNs Work with WordPress

```
Without CDN:
  Visitor (Tokyo) → Origin Server (Amsterdam) → Response back to Tokyo
  Latency: ~250ms per request

With CDN:
  Visitor (Tokyo) → CDN Edge (Tokyo) → Cached response
  Latency: ~20ms per request

  On cache miss:
  CDN Edge (Tokyo) → Origin Server (Amsterdam) → CDN caches → Response
```

### What Gets Cached

| Content Type | CDN Cacheable? | Notes |
|-------------|---------------|-------|
| Images (jpg, png, webp, avif) | Yes | Biggest bandwidth savings |
| CSS files | Yes | Cache-bust with version query strings |
| JavaScript files | Yes | Same versioning approach |
| Fonts (woff2, woff) | Yes | Watch for CORS headers |
| HTML pages | Sometimes | Only for logged-out visitors, careful with dynamic content |
| Admin pages | Never | Always bypass CDN |
| AJAX/REST API | Usually no | Dynamic responses, but some GET endpoints can be cached |

## CDN Providers Compared

### Full-Stack CDNs (CDN + Security + DNS)

| Provider | Free Tier | Best For | Key Advantage |
|----------|-----------|----------|---------------|
| **Cloudflare** | Yes (generous) | Most WordPress sites | Free WAF, DDoS protection, easy setup |
| **Fastly** | No | High-traffic, real-time purge needs | Instant purge, VCL flexibility |
| **AWS CloudFront** | 1TB/month free first year | AWS-hosted WordPress | Deep AWS integration |

### Specialized CDNs

| Provider | Cost | Best For | Key Advantage |
|----------|------|----------|---------------|
| **Bunny CDN** | ~$0.01/GB | Cost-conscious, global reach | 123+ PoPs, simple pricing |
| **KeyCDN** | $0.04/GB | European focus | Pay-as-you-go, GDPR-friendly |
| **StackPath** | From $15/month | North American sites | MaxCDN successor |

### WordPress-Specific CDN Services

| Service | What It Does |
|---------|-------------|
| **Jetpack Site Accelerator** | Free image and static file CDN via WordPress.com infrastructure |
| **JEsuspended/JEEZ** | Free CDN services bundled with hosting (WP Engine, Kinsta, etc.) |

Most managed WordPress hosts (WP Engine, Kinsta, Cloudways) include CDN as part of their hosting. Check before adding another.

## Cloudflare Setup for WordPress

Cloudflare is the most common CDN for WordPress because the free tier is genuinely useful.

### DNS Setup

1. Add your domain to Cloudflare
2. Update nameservers at your registrar
3. Cloudflare proxies traffic (orange cloud icon)

### Recommended Page Rules (Free Tier: 3 Rules)

| Rule | URL Pattern | Setting |
|------|------------|---------|
| **Bypass admin** | `example.com/wp-admin/*` | Cache Level: Bypass |
| **Bypass login** | `example.com/wp-login.php*` | Cache Level: Bypass |
| **Cache everything** | `example.com/*` | Cache Level: Cache Everything, Edge TTL: 1 month |

### Cache Rules (Better Than Page Rules)

Cloudflare's newer Cache Rules are more flexible:

```
Rule 1: Bypass cache for admin and dynamic
  When: URI Path contains "/wp-admin" OR URI Path contains "/wp-login" OR Cookie contains "wordpress_logged_in"
  Then: Bypass Cache

Rule 2: Cache static assets aggressively
  When: URI Path matches ".*\.(css|js|jpg|jpeg|png|gif|webp|avif|svg|woff2|woff|ico)$"
  Then: Cache, Edge TTL 30 days, Browser TTL 7 days
```

### WordPress Plugin Integration

| Plugin | Purpose |
|--------|---------|
| **Cloudflare** (official) | Settings management, one-click optimizations |
| **WP Cloudflare Super Page Cache** | HTML page caching through Cloudflare |
| **APO for WordPress** | Cloudflare's managed WordPress caching ($5/month) |

**Cloudflare APO** is particularly effective — it caches full HTML pages at the edge, turning your WordPress site into what behaves like a static site for logged-out visitors. This can reduce TTFB from 500ms+ to under 50ms.

## Bunny CDN Setup

Bunny CDN is the best value option for sites needing global distribution without Cloudflare's complexity.

### Setup Steps

1. Create a Pull Zone in Bunny dashboard
2. Set origin URL to your WordPress site
3. Get your Bunny CDN URL (e.g., `yourzone.b-cdn.net`)
4. Configure WordPress to use CDN URL for assets

### WordPress Configuration

Use a CDN rewriter plugin or configure in your caching plugin:

| Caching Plugin | CDN Setting Location |
|---------------|---------------------|
| **WP Super Cache** | Settings → CDN tab |
| **W3 Total Cache** | Performance → CDN |
| **WP Rocket** | Settings → CDN |
| **LiteSpeed Cache** | CDN → CDN Settings |

Or rewrite URLs manually:

```php
// Simple CDN URL rewriting for wp-content assets
add_filter( 'wp_get_attachment_url', function( $url ) {
    if ( is_admin() ) {
        return $url;
    }
    return str_replace(
        'https://example.com/wp-content/',
        'https://yourzone.b-cdn.net/wp-content/',
        $url
    );
} );
```

## Cache Invalidation

The hardest part of CDN management. When you update content, the CDN still serves the old version until the cache expires or you purge it.

### Invalidation Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **TTL-based** | Cache expires after set time | Static assets with versioning |
| **Manual purge** | Trigger purge from dashboard/API | Content updates |
| **Tag-based purge** | Purge by cache tag (e.g., "blog-posts") | Large sites with categorized content |
| **Version strings** | `style.css?v=1.2.3` — new version = new cache entry | CSS/JS updates |

### WordPress Cache Busting

WordPress handles CSS/JS versioning automatically:

```php
// WordPress adds version query string
wp_enqueue_style( 'theme-style', get_stylesheet_uri(), array(), '1.0.0' );
// Output: <link rel="stylesheet" href="/style.css?ver=1.0.0">

// To bust cache on every change during development:
wp_enqueue_style( 'theme-style', get_stylesheet_uri(), array(), filemtime( get_stylesheet_directory() . '/style.css' ) );
```

### Automated Purge on Content Update

Most CDN plugins purge relevant URLs when content changes:

```php
// Hook into post save to purge CDN cache
add_action( 'save_post', function( $post_id ) {
    if ( wp_is_post_revision( $post_id ) ) {
        return;
    }

    $urls_to_purge = array(
        get_permalink( $post_id ),
        home_url( '/' ),
        get_post_type_archive_link( get_post_type( $post_id ) ),
    );

    // Purge via CDN API (example for Bunny CDN)
    foreach ( $urls_to_purge as $url ) {
        wp_remote_request( 'https://api.bunny.net/purge?url=' . urlencode( $url ), array(
            'method'  => 'POST',
            'headers' => array( 'AccessKey' => BUNNY_API_KEY ),
        ) );
    }
} );
```

## CDN for WooCommerce

E-commerce sites need special CDN consideration:

| Page Type | Cache? | Why |
|-----------|--------|-----|
| Product pages | Yes (with care) | High traffic, mostly static |
| Category/archive | Yes | Same as product pages |
| Cart page | No | Dynamic, per-user |
| Checkout | No | Sensitive, per-session |
| My Account | No | Per-user data |
| AJAX cart fragments | No | Dynamic mini-cart updates |

### Excluding WooCommerce Dynamic Content

```
# Cloudflare Cache Rule for WooCommerce
When: Cookie contains "woocommerce_cart_hash" OR
      URI Path contains "/cart" OR
      URI Path contains "/checkout" OR
      URI Path contains "/my-account" OR
      URI Path starts with "/wc-api/"
Then: Bypass Cache
```

## Performance Measurement

### Before/After CDN Metrics

| Metric | Measure With |
|--------|-------------|
| TTFB by region | [KeyCDN Performance Test](https://tools.keycdn.com/performance) |
| Global latency | [Uptrends](https://www.uptrends.com/tools/cdn-performance-check) |
| Cache hit ratio | CDN dashboard analytics |
| Bandwidth savings | CDN dashboard vs origin logs |

A well-configured CDN should show:
- **Cache hit ratio**: 85%+ for static assets
- **TTFB reduction**: 50-80% for distant visitors
- **Bandwidth savings**: 60-80% off origin server

## Multi-CDN Strategy

For high-traffic or globally critical sites, using multiple CDNs adds resilience:

| Approach | Complexity | Use Case |
|----------|-----------|----------|
| **Cloudflare for security + Bunny for media** | Low | Separate concerns |
| **DNS-based failover** | Medium | Availability-critical sites |
| **Multi-CDN load balancing** | High | Enterprise, global audience |

A practical multi-CDN setup for WordPress:
- **Cloudflare**: DNS, WAF, HTML caching (APO)
- **Bunny CDN**: Image/media delivery (often cheaper at scale)
- **Jetpack Site Accelerator**: Free fallback for images

## Common Mistakes

- **Caching logged-in pages** — Users see each other's admin bars or account data
- **Not excluding WooCommerce pages** — Cart/checkout breaks with cached responses
- **Ignoring CORS for fonts** — Fonts fail to load from CDN without proper `Access-Control-Allow-Origin` headers
- **Over-purging** — Purging entire cache on every post update defeats the purpose
- **Forgetting to update CDN URL after domain change** — Assets 404 after migration
- **Stacking CDN plugins** — One CDN rewriter is enough; multiples cause double-rewriting

## Further Reading

- [Frontend Asset Optimization](./13-frontend-asset-optimization.md) — Asset optimization before CDN delivery
- [DNS & HTTP Protocols](./17-dns-http-protocols.md) — DNS and HTTP/2-3 interaction with CDNs
- [Cloudflare Hardening](../03-security/01-cloudflare-hardening.md) — Security configuration
- [Image Optimization](./06-image-optimizations.md) — Optimize before serving via CDN
- [Scaling WordPress](./09-scaling-wordpress.md) — CDN as part of scaling architecture
