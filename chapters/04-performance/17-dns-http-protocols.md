# DNS & HTTP Protocols

## Overview

Before your server processes a single line of PHP, two things must happen: DNS resolution and connection establishment. These "invisible" steps add latency to every first visit. Understanding DNS, TLS, and HTTP protocol versions helps you optimize the path from browser to server.

## DNS Fundamentals

DNS (Domain Name System) translates your domain name to an IP address. When someone types `yoursite.com`, their browser needs to find the actual server IP (like `192.168.1.1`) before it can send any request. Every first-time visitor pays this cost—and unlike server-side optimizations covered in [PHP Optimization](./02-php-optimization.md) or [Database Optimization](./07-database-optimizations.md), DNS resolution happens before your server is even contacted.

### The DNS Resolution Chain

The lookup process cascades through multiple servers, each adding potential latency:

```
Browser → Local Cache → OS Cache → Router Cache → ISP Resolver → Root Servers → TLD Servers → Authoritative DNS
```

**How this works in practice:**

1. **Browser cache** - Chrome, Firefox, etc. remember recent lookups for minutes
2. **Operating system cache** - Windows/macOS/Linux maintain their own DNS cache
3. **Router cache** - Your home/office router may cache results
4. **ISP resolver** - Your internet provider's DNS servers (often the slowest step)
5. **Root servers** - The top of the DNS hierarchy, know where to find `.com`, `.org`, etc.
6. **TLD servers** - Handle specific extensions (`.com` servers, `.org` servers)
7. **Authoritative DNS** - Your domain's actual DNS provider with the real answer

Each step adds latency. Typical DNS resolution takes 20-120ms, but can exceed 200ms for cold lookups (when nothing is cached). For a returning visitor with cached DNS, this step is essentially free. For a first-time visitor from a different country using a slow ISP resolver, it can be a significant chunk of your total page load time.

### TTL (Time to Live)

TTL determines how long DNS records are cached at each level of the resolution chain. Think of it as an expiration date—once the TTL passes, the cached record is considered stale and must be looked up again.

The trade-off is simple: longer TTLs mean fewer DNS lookups (faster for returning visitors) but slower propagation when you change your DNS records (like during a server migration).

| TTL Value | Use Case |
|-----------|----------|
| 300 (5 min) | During migrations, DNS changes |
| 3600 (1 hour) | Standard for most sites |
| 86400 (24 hours) | Stable sites, maximum caching |

**Recommendation:** Use longer TTLs for stable sites. Shorter TTLs mean more DNS lookups. If you're not planning any server migrations or DNS changes, there's no reason not to use 24-hour TTLs. Before a migration, lower the TTL a few days in advance so the old long-cached values expire.

```bash
# Check current TTL
dig example.com +noall +answer
```

The TTL value appears in the output (in seconds). If you see `3600`, your record is cached for one hour.

### DNS Provider Performance

Your DNS provider is the authoritative source for your domain's records. When someone's ISP resolver needs to find your IP address, it ultimately asks your DNS provider. The speed and global distribution of your provider's servers directly affects lookup times for visitors worldwide.

DNS providers vary significantly in speed:

| Provider | Typical Resolution | Notes |
|----------|-------------------|-------|
| Cloudflare | 10-15ms | Fastest, free tier available |
| Google Cloud DNS | 15-25ms | Good performance |
| Route 53 (AWS) | 20-30ms | Integrates with AWS |
| Traditional registrars | 50-100ms+ | Often slower |

The difference comes down to infrastructure. Cloudflare operates servers in hundreds of cities worldwide—a visitor in Tokyo reaches a nearby Cloudflare server. Traditional registrar DNS might only have servers in a few locations, forcing that Tokyo visitor to reach across the Pacific.

Consider a dedicated DNS provider rather than your registrar's default. You can keep your domain registered at GoDaddy, Namecheap, or wherever, but point the nameservers to [Cloudflare](https://www.cloudflare.com/dns/) for actual DNS resolution. This is free and takes about 15 minutes to set up.

If you're already using Cloudflare as a CDN (see [Security Hardening with Cloudflare](../03-security/01-cloudflare-hardening.md)), you're automatically using their DNS. For comparison of DNS provider speeds, check [DNSPerf](https://www.dnsperf.com/) which tracks real-world resolution times globally.

## DNS Prefetching

Since DNS resolution takes time, you can tell browsers to do it early—before the resource is actually needed. When the browser sees a `dns-prefetch` hint in your HTML head, it immediately starts the DNS lookup in the background. By the time the browser encounters the actual resource request later in the page, the DNS is already resolved.

This is particularly valuable for third-party resources that appear later in your page. Without prefetching, the browser discovers Google Fonts halfway through parsing, then waits for DNS resolution before it can even start downloading fonts. With prefetching, DNS is already done.

```html
<!-- Prefetch DNS for resources you'll load later -->
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="dns-prefetch" href="//www.google-analytics.com">
<link rel="dns-prefetch" href="//cdn.example.com">
```

Notice the `//` prefix without `http:` or `https:`—this protocol-relative format works for both secure and non-secure contexts.

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

Preconnect goes further than DNS prefetch—it establishes the full connection before it's needed. This includes DNS lookup, TCP handshake (establishing the communication channel), and TLS negotiation (setting up encryption). For HTTPS resources, this can save 200-300ms.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

The `crossorigin` attribute is required for resources that will be fetched with CORS (like fonts). Without it, the browser establishes a connection, but then can't reuse it for the actual font request because CORS requires different connection settings.

**Preconnect vs DNS-prefetch:**

| Resource Hint | What It Does | Cost |
|---------------|--------------|------|
| `dns-prefetch` | DNS lookup only | Very low |
| `preconnect` | DNS + TCP + TLS handshake | Low-medium |

Use `preconnect` for critical third-party resources (fonts, CDN). Use `dns-prefetch` for less critical resources to save connection overhead.

**Caution:** Don't preconnect to too many origins. Each connection has CPU/memory cost—the browser maintains an open connection waiting for use, consuming memory. Limit to 2-4 critical domains. If you preconnect to 15 domains, you're hurting performance rather than helping.

## TLS Performance

Every HTTPS connection requires a TLS handshake—a cryptographic negotiation where browser and server agree on encryption methods and exchange keys. This happens before any actual data transfers and adds latency to every new connection. The latency is non-negotiable (you need HTTPS for security and SEO), but the version of TLS you use affects how much latency.

### TLS 1.3 vs TLS 1.2

TLS 1.2 requires two round trips between browser and server to establish encryption. TLS 1.3 achieves the same security with just one round trip by redesigning the handshake process. On a 50ms latency connection, that's 50ms saved—noticeable on every new connection.

| Version | Handshake Round Trips | Notes |
|---------|----------------------|-------|
| TLS 1.2 | 2 | Legacy, still common |
| TLS 1.3 | 1 | Modern, faster |

TLS 1.3 reduces handshake time by ~100ms on average. Most modern servers and CDNs support it by default—but some older hosting providers haven't upgraded. Check your hosting if you're using managed WordPress hosting, or verify your server configuration if self-managed. You can test your site's TLS configuration with [SSL Labs Server Test](https://www.ssllabs.com/ssltest/) which gives detailed analysis of your SSL/TLS setup.

**Check your TLS version:**
```bash
curl -svo /dev/null https://example.com 2>&1 | grep "SSL connection"
```

### Session Resumption

The full TLS handshake only needs to happen once. Returning visitors can skip most of it by resuming a previous session. The browser essentially says "we talked before, here's proof" instead of starting fresh.

Two mechanisms exist for this:

- **Session IDs** - Server stores session state in memory, gives browser an ID to reference it. Works well for single servers but requires sticky sessions or shared storage in load-balanced setups (see [Scaling WordPress](./09-scaling-wordpress.md) for session handling)
- **Session Tickets** - Server encrypts the session state and gives it to the browser. Browser sends it back to resume. More scalable because server doesn't store anything

Most modern servers support both by default. Session tickets are preferred for scalability. With either mechanism, a returning visitor's connection is established much faster.

### Certificate Optimization

Your SSL certificate itself affects performance in several ways:

| Factor | Impact | Recommendation |
|--------|--------|----------------|
| Chain length | More certs = more data | Use short chains |
| OCSP | Extra request for revocation check | Enable OCSP stapling |
| Certificate size | RSA 4096 vs 2048 | 2048 is sufficient |
| ECC certificates | Smaller, faster | Use if supported |

**Chain length** refers to the certificate hierarchy. Your certificate is signed by an intermediate certificate, which is signed by a root certificate. The browser needs to verify the entire chain. Some certificates have multiple intermediates, each adding data to transfer and verify. Let's Encrypt uses a short chain by default.

**OCSP (Online Certificate Status Protocol)** is how browsers check if a certificate has been revoked. Without stapling, the browser makes a separate request to the certificate authority for every new visitor—a blocking request that adds latency. With OCSP stapling, your server pre-fetches the OCSP response and includes it in the TLS handshake. The browser gets proof the certificate is valid without making an extra request.

```nginx
# Nginx OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
```

**ECC (Elliptic Curve Cryptography)** certificates use smaller keys for equivalent security. A 256-bit ECC key provides similar security to a 3072-bit RSA key, meaning less data to transfer and faster cryptographic operations. Most modern setups use ECDSA certificates by default.

## HTTP Protocol Versions

Understanding HTTP versions helps you make sense of performance recommendations. Many older "best practices" (like domain sharding or sprite images) were workarounds for HTTP/1.1 limitations that are counterproductive with modern protocols.

### HTTP/1.1

The workhorse since 1997, HTTP/1.1 was designed when web pages had a dozen resources. Modern WordPress pages might request 50-100 resources, exposing the protocol's limitations:

- **One request per connection** - Each connection handles one request/response at a time. Browsers work around this by opening 6 connections per domain, but that's still a hard limit
- **Head-of-line blocking** - Requests queue up on each connection. If one response is slow (large image), everything behind it waits
- **No header compression** - HTTP headers (cookies, user-agent, etc.) are sent with every request, often 1-2KB repeated dozens of times
- **No server push** - Server is reactive only—it waits for the browser to request each resource

These limitations led to HTTP/1.1-era optimization techniques: combining CSS/JS files (fewer requests), using sprite images (fewer requests), domain sharding (more parallel connections). With HTTP/2, these techniques are often unnecessary or counterproductive.

### HTTP/2

HTTP/2 (standardized in 2015, based on Google's SPDY protocol) fundamentally redesigned how requests work:

| Feature | Benefit |
|---------|---------|
| Multiplexing | Multiple requests on single connection |
| Header compression | HPACK reduces header overhead |
| Stream prioritization | Important resources first |
| Server push | Proactive resource delivery |

**Multiplexing** is the key improvement. Instead of one request at a time per connection, HTTP/2 sends all requests simultaneously over a single connection. The browser can request 50 files, and they all download in parallel without waiting for each other. This eliminates the need for domain sharding and reduces the benefit of file concatenation.

**Header compression (HPACK)** maintains a dictionary of header fields. Instead of sending full headers with every request, HTTP/2 references the dictionary. First request sends full headers; subsequent requests just say "same as before plus these changes."

**Stream prioritization** lets browsers indicate which resources are most important. CSS and fonts that block rendering can be prioritized over images that don't. Not all servers implement prioritization well, but when it works, critical resources arrive first.

**Result:** Faster page loads, especially for resource-heavy pages. A WordPress page with 40 requests benefits much more from HTTP/2 than a minimal page with 5 requests.

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

HTTP/3 (standardized in 2022) represents a more fundamental change: it abandons TCP entirely in favor of QUIC, a protocol built on UDP. This might sound like a minor technical detail, but it solves HTTP/2's remaining head-of-line blocking problem.

With HTTP/2 over TCP, a single lost packet blocks the entire connection until retransmission. All 50 streams wait for that one packet. With HTTP/3 over QUIC, a lost packet only blocks the specific stream it belongs to—the other 49 continue unaffected.

| Feature | Benefit |
|---------|---------|
| 0-RTT connections | Returning visitors connect instantly |
| No head-of-line blocking | Packet loss doesn't stall everything |
| Connection migration | Survives network changes (mobile) |
| Built-in encryption | TLS 1.3 integrated |

**0-RTT (Zero Round Trip Time)** is transformative for returning visitors. QUIC remembers previous connections and can send data immediately, before the handshake completes. A returning visitor's first request starts transmitting during connection establishment rather than after.

**Connection migration** matters most on mobile. When your phone switches from WiFi to cellular (or moves between cell towers), TCP connections break and must restart. QUIC identifies connections by ID rather than IP address, so the connection survives network changes seamlessly. Users scrolling while walking don't experience interruptions.

**Current state:** Supported by [Cloudflare](https://www.cloudflare.com/learning/performance/what-is-http3/), Google Cloud, AWS CloudFront, Fastly. Browser support is widespread (Chrome, Firefox, Safari, Edge all support HTTP/3). If you're using a modern CDN, you likely have HTTP/3 already. Check your site's HTTP version support with [HTTP/3 Check](https://http3check.net/) or look at the protocol column in browser DevTools Network panel.

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

Every external domain requires its own DNS lookup and connection establishment. With HTTP/2's multiplexing, multiple requests to the *same* domain are cheap. But each *new* domain requires full DNS + TCP + TLS setup.

A typical WordPress site with plugins might connect to 10+ external domains:

```
Page with 10 external domains:
- fonts.googleapis.com (DNS + connect)
- fonts.gstatic.com (DNS + connect)
- www.google-analytics.com (DNS + connect)
- googletagmanager.com (DNS + connect)
- facebook.net (DNS + connect)
- ... etc
```

Each connection adds 100-300ms latency. Ten domains could mean 1-3 seconds of connection overhead before any real content transfers. This is why "reduce external requests" often matters more than "reduce request count"—one domain with 20 requests is faster than 10 domains with 2 requests each.

**Solutions:**
- Self-host fonts instead of Google Fonts (see [Frontend Asset Optimization](./13-frontend-asset-optimization.md) for font handling)
- Use a tag manager to consolidate scripts—one connection to Google Tag Manager instead of separate connections to Analytics, Ads, etc.
- Proxy external analytics through your domain using a simple plugin or Cloudflare Workers
- Audit plugins for external calls—see [Plugin Performance Evaluation](./15-plugin-performance.md) for finding "phone home" plugins

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

Understanding where time is spent helps you optimize effectively. Is your site slow because of DNS? TLS? Server processing? The tools below help you diagnose.

### Browser DevTools

The Network tab breaks down each request into timing phases. Click any request to see the detailed timing:

- **DNS Lookup** - Time for DNS resolution (should be near-zero for your main domain after first request)
- **Initial Connection** - TCP handshake time (network latency dependent)
- **SSL** - TLS handshake time (should be shorter with TLS 1.3)
- **Waiting (TTFB)** - Time to first byte from server (this is your server processing time plus network latency)

If DNS Lookup is consistently high, check your DNS provider. If SSL is high, verify TLS 1.3 is enabled. If TTFB is high, that's server-side work—see [Debugging & Profiling](./10-debugging-profiling.md).

### WebPageTest

[WebPageTest](https://www.webpagetest.org/) provides the most detailed connection waterfall available:

- DNS timing per domain (shows which external domains are slow)
- Connection reuse patterns (see if HTTP/2 is working—should see connection reuse)
- Protocol version used (verify HTTP/2 or HTTP/3)
- TLS negotiation details (cipher suite, certificate chain)

Test from different geographic locations to understand how distance affects connection times. A site hosted in Europe will show different patterns when tested from Asia versus Germany.

### Testing Tools

```bash
# Measure DNS resolution
time dig example.com

# Measure full connection with timing
curl -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" -o /dev/null -s https://example.com
```

## Further Reading

**Internal:**
- [Scaling WordPress](./09-scaling-wordpress.md) - CDN and edge caching
- [Core Web Vitals](./08-core-web-vitals-optimizations.md) - How connection speed affects metrics
- [Cloudflare Hardening](../03-security/01-cloudflare-hardening.md) - CDN configuration

**External:**
- [web.dev - Optimize resource loading](https://web.dev/articles/prioritize-resources) - Google's guide to preconnect, prefetch, and preload
- [KeyCDN HTTP/2 Test](https://tools.keycdn.com/http2-test) - Check if your site supports HTTP/2
- [Mozilla Observatory](https://observatory.mozilla.org/) - Security headers and TLS configuration scanner
- [High Performance Browser Networking](https://hpbn.co/) - Ilya Grigorik's comprehensive book (free online)
