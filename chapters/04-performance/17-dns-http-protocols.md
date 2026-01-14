# DNS & HTTP Protocols

## Overview

Before your server processes a single line of PHP, two things must happen: DNS resolution and connection establishment. These "invisible" steps add latency to every first visit. Understanding DNS, TLS, and HTTP protocol versions helps you optimize the path from browser to server.

## DNS Fundamentals

DNS (Domain Name System) translates your domain name to an IP address. Every first-time visitor pays this cost.

### The DNS Resolution Chain

```
Browser → Local Cache → OS Cache → Router Cache → ISP Resolver → Root Servers → TLD Servers → Authoritative DNS
```

Each step adds latency. Typical DNS resolution takes 20-120ms, but can exceed 200ms for cold lookups.

### TTL (Time to Live)

TTL determines how long DNS records are cached:

| TTL Value | Use Case |
|-----------|----------|
| 300 (5 min) | During migrations, DNS changes |
| 3600 (1 hour) | Standard for most sites |
| 86400 (24 hours) | Stable sites, maximum caching |

**Recommendation:** Use longer TTLs for stable sites. Shorter TTLs mean more DNS lookups.

```
# Check current TTL
dig example.com +noall +answer
```

### DNS Provider Performance

DNS providers vary significantly in speed:

| Provider | Typical Resolution | Notes |
|----------|-------------------|-------|
| Cloudflare | 10-15ms | Fastest, free tier available |
| Google Cloud DNS | 15-25ms | Good performance |
| Route 53 (AWS) | 20-30ms | Integrates with AWS |
| Traditional registrars | 50-100ms+ | Often slower |

Consider a dedicated DNS provider rather than your registrar's default.

## DNS Prefetching

Tell browsers to resolve DNS for third-party domains before they're needed:

```html
<!-- Prefetch DNS for resources you'll load later -->
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="dns-prefetch" href="//www.google-analytics.com">
<link rel="dns-prefetch" href="//cdn.example.com">
```

Add to WordPress:

```php
add_action('wp_head', function() {
    $domains = [
        '//fonts.googleapis.com',
        '//fonts.gstatic.com',
        '//www.googletagmanager.com',
    ];

    foreach ($domains as $domain) {
        echo '<link rel="dns-prefetch" href="' . esc_url($domain) . '">' . "\n";
    }
}, 1);
```

**When to use:** Any third-party domain that appears on most pages.

## Preconnect

Go further than DNS—establish the full connection (DNS + TCP + TLS) before it's needed:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

**Preconnect vs DNS-prefetch:**

| Resource Hint | What It Does | Cost |
|---------------|--------------|------|
| `dns-prefetch` | DNS lookup only | Very low |
| `preconnect` | DNS + TCP + TLS handshake | Low-medium |

Use `preconnect` for critical third-party resources (fonts, CDN). Use `dns-prefetch` for less critical resources to save connection overhead.

**Caution:** Don't preconnect to too many origins. Each connection has CPU/memory cost. Limit to 2-4 critical domains.

## TLS Performance

HTTPS requires a TLS handshake before data transfers. This adds latency but is non-negotiable for security and SEO.

### TLS 1.3 vs TLS 1.2

| Version | Handshake Round Trips | Notes |
|---------|----------------------|-------|
| TLS 1.2 | 2 | Legacy, still common |
| TLS 1.3 | 1 | Modern, faster |

TLS 1.3 reduces handshake time by ~100ms on average. Most modern servers support it—ensure yours does.

**Check your TLS version:**
```bash
curl -svo /dev/null https://example.com 2>&1 | grep "SSL connection"
```

### Session Resumption

Returning visitors can skip the full TLS handshake if sessions are cached:

- **Session IDs** - Server stores session state
- **Session Tickets** - Client stores encrypted session state

Ensure your server supports TLS session resumption. Most modern configurations do by default.

### Certificate Optimization

| Factor | Impact | Recommendation |
|--------|--------|----------------|
| Chain length | More certs = more data | Use short chains |
| OCSP | Extra request for revocation check | Enable OCSP stapling |
| Certificate size | RSA 4096 vs 2048 | 2048 is sufficient |
| ECC certificates | Smaller, faster | Use if supported |

OCSP stapling is particularly important—it eliminates a blocking request to the certificate authority:

```nginx
# Nginx OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
```

## HTTP Protocol Versions

### HTTP/1.1

The workhorse since 1997. Limitations:

- **One request per connection** - Browsers open 6 connections per domain
- **Head-of-line blocking** - One slow response blocks others
- **No header compression** - Repeated headers waste bandwidth
- **No server push** - Server can only respond to requests

### HTTP/2

Major improvements (2015):

| Feature | Benefit |
|---------|---------|
| Multiplexing | Multiple requests on single connection |
| Header compression | HPACK reduces header overhead |
| Stream prioritization | Important resources first |
| Server push | Proactive resource delivery |

**Result:** Faster page loads, especially for resource-heavy pages.

**Enable HTTP/2:**

Most CDNs and modern servers enable it by default. Check:
```bash
curl -sI https://example.com | grep -i "HTTP/"
```

**Nginx:**
```nginx
listen 443 ssl http2;
```

**Apache:**
```bash
# Enable mod_http2
sudo a2enmod http2
```

```apache
<VirtualHost *:443>
    Protocols h2 http/1.1
    # ... rest of config
</VirtualHost>
```

### HTTP/2 Server Push

Server Push allows the server to send resources before the browser requests them. When the browser requests `/page.html`, the server can immediately push `/style.css` and `/script.js` without waiting for the browser to parse the HTML and discover these resources.

**How it works:**

```
Traditional:
Browser: GET /page.html
Server:  200 OK (page.html)
Browser: (parses HTML, discovers CSS)
Browser: GET /style.css
Server:  200 OK (style.css)

With Server Push:
Browser: GET /page.html
Server:  200 OK (page.html) + PUSH /style.css
(CSS arrives before browser even parses HTML)
```

**PHP implementation using Link headers:**

```php
// Push critical resources via Link header
function push_critical_resources() {
    if (headers_sent()) return;

    $resources = [
        get_template_directory_uri() . '/css/critical.css' => 'style',
        get_template_directory_uri() . '/js/app.js' => 'script',
        get_template_directory_uri() . '/fonts/primary.woff2' => 'font',
    ];

    foreach ($resources as $path => $type) {
        header("Link: <{$path}>; rel=preload; as={$type}", false);
    }
}
add_action('send_headers', 'push_critical_resources');
```

**Nginx configuration:**

```nginx
# Enable push preload (reads Link headers)
http2_push_preload on;

# Or push specific resources directly
location = /index.html {
    http2_push /css/style.css;
    http2_push /js/app.js;
}
```

**Apache configuration:**

```apache
# mod_http2 automatically handles Link headers with rel=preload
H2Push on

# Or push directly
<Location /index.html>
    H2PushResource /css/style.css
    H2PushResource /js/app.js
</Location>
```

**When to use Server Push:**

| Use Case | Recommendation |
|----------|----------------|
| Critical CSS | Good candidate |
| Hero images | Consider for LCP |
| Fonts | Good for preventing FOIT |
| JavaScript | Careful—may waste bandwidth |
| Subsequent pages | Don't push—likely cached |

**Caveats:**

1. **Cache-awareness** - Push doesn't know what's cached. Returning visitors receive already-cached resources again.
2. **Bandwidth** - Pushing too much wastes bandwidth, especially on slow connections.
3. **CDN support** - Not all CDNs pass through push. Check your CDN's documentation.
4. **Deprecation concerns** - Chrome removed support for server push in 2022, favoring `103 Early Hints` instead.

**Modern alternative: 103 Early Hints**

Early Hints is the modern replacement for Server Push:

```
Browser: GET /page.html
Server:  103 Early Hints
         Link: </style.css>; rel=preload; as=style
Server:  200 OK (page.html)
```

The browser starts fetching hinted resources while the server is still generating the response. Cloudflare supports this automatically for preload hints.

### HTTP/3 (QUIC)

The newest protocol (2022), built on UDP:

| Feature | Benefit |
|---------|---------|
| 0-RTT connections | Returning visitors connect instantly |
| No head-of-line blocking | Packet loss doesn't stall everything |
| Connection migration | Survives network changes (mobile) |
| Built-in encryption | TLS 1.3 integrated |

**Current state:** Supported by Cloudflare, Google Cloud, AWS CloudFront, Fastly. Browser support is widespread.

### Which Protocol Matters Most?

| Scenario | Impact of HTTP/2+ |
|----------|-------------------|
| Few resources per page | Minimal improvement |
| Many small resources | Significant improvement |
| High latency connections | Major improvement |
| Mobile users | Very noticeable |
| Already using CDN | CDN handles it |

For most WordPress sites, HTTP/2 is the practical target. HTTP/3 provides incremental gains, especially for mobile users.

## WordPress-Specific Optimizations

### Reduce External Requests

Every external domain requires DNS lookup + connection:

```
Page with 10 external domains:
- fonts.googleapis.com (DNS + connect)
- fonts.gstatic.com (DNS + connect)
- www.google-analytics.com (DNS + connect)
- googletagmanager.com (DNS + connect)
- facebook.net (DNS + connect)
- ... etc
```

**Solutions:**
- Self-host fonts instead of Google Fonts
- Use a tag manager to consolidate scripts
- Proxy external analytics through your domain
- Combine services where possible

### Resource Hints in WordPress

Add systematically:

```php
add_action('wp_head', function() {
    // Critical third-party origins - preconnect
    $preconnect = [
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com',
    ];

    // Less critical - dns-prefetch only
    $prefetch = [
        '//www.google-analytics.com',
        '//www.googletagmanager.com',
    ];

    foreach ($preconnect as $url) {
        echo '<link rel="preconnect" href="' . esc_url($url) . '">' . "\n";
    }

    foreach ($prefetch as $url) {
        echo '<link rel="dns-prefetch" href="' . esc_url($url) . '">' . "\n";
    }
}, 1);
```

### Early Hints (103)

HTTP 103 Early Hints let the server send preload hints while still generating the response:

```
Browser: GET /page
Server: 103 Early Hints
        Link: </style.css>; rel=preload; as=style
Server: 200 OK
        <html>...
```

The browser starts fetching CSS before the HTML even arrives.

**Support:** Cloudflare, some CDNs. WordPress doesn't natively support it, but CDN-level implementation works automatically.

## Measuring Connection Performance

### Browser DevTools

Network tab shows:
- **DNS Lookup** - Time for DNS resolution
- **Initial Connection** - TCP handshake
- **SSL** - TLS handshake
- **Waiting (TTFB)** - Time to first byte from server

### WebPageTest

Provides detailed connection waterfall:
- DNS timing per domain
- Connection reuse patterns
- Protocol version used
- TLS negotiation details

### Testing Tools

```bash
# Measure DNS resolution
time dig example.com

# Measure full connection with timing
curl -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" -o /dev/null -s https://example.com
```

## Further Reading

- [Scaling WordPress](./09-scaling-wordpress.md) - CDN and edge caching
- [Core Web Vitals](./08-core-web-vitals-optimizations.md) - How connection speed affects metrics
- [Cloudflare Hardening](../03-security/01-cloudflare-hardening.md) - CDN configuration
