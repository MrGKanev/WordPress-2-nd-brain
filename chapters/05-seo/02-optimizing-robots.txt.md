# Optimizing robots.txt

The robots.txt file tells search engine crawlers which parts of your site to access. While it's simple in concept, improper configuration can hurt SEO by blocking important content or wasting crawl budget on low-value pages.

## How robots.txt Works

When a crawler visits your site, it first requests `/robots.txt`:

```
1. Googlebot requests: https://example.com/robots.txt
2. Server returns robots.txt rules
3. Googlebot checks rules before crawling each URL
4. Googlebot respects (or ignores) the rules
```

**Important:** robots.txt is a suggestion, not a security measure. Well-behaved bots follow it; malicious bots ignore it. Never use robots.txt to hide sensitive content.

### What robots.txt Can and Cannot Do

| Can Do | Cannot Do |
|--------|-----------|
| Suggest which URLs to crawl | Prevent indexing (use noindex for that) |
| Point to sitemaps | Block malicious bots |
| Save crawl budget | Hide content from search results |
| Reduce server load from bots | Protect private data |

## WordPress Default robots.txt

WordPress generates a virtual robots.txt at your domain root:

```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
```

This file isn't physically stored—it's generated dynamically. The default is minimal and often insufficient.

### Checking Your Current robots.txt

```bash
# Via command line
curl https://yoursite.com/robots.txt

# Or simply visit in browser
https://yoursite.com/robots.txt
```

## Creating a Custom robots.txt

### Option 1: Physical File (Recommended)

Create a `robots.txt` file in your WordPress root directory:

```bash
# Connect via SFTP and create file
touch /var/www/yoursite.com/robots.txt
```

A physical file overrides WordPress's virtual robots.txt.

### Option 2: SEO Plugin

Most SEO plugins include robots.txt editors:

- **Yoast SEO:** SEO → Tools → File editor
- **Rank Math:** General Settings → Edit robots.txt
- **SEOPress:** SEO → XML/HTML Sitemap → robots.txt

### Option 3: Filter Hook

Modify the virtual robots.txt via code:

```php
add_filter( 'robots_txt', function( $output, $public ) {
    $custom_rules = "
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Disallow: /cart/
Disallow: /checkout/

Sitemap: https://example.com/sitemap_index.xml
";
    return $custom_rules;
}, 10, 2 );
```

---

## Optimized robots.txt Examples

### Basic WordPress Blog

```
# robots.txt for WordPress blog
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

# Non-essential paths
Disallow: /trackback/
Disallow: /comments/feed/
Disallow: */embed/
Disallow: /wp-login.php
Disallow: /wp-register.php

# Search results (low value, duplicate content risk)
Disallow: /?s=
Disallow: /search/

# Pagination beyond page 10 (optional, saves crawl budget)
Disallow: /page/1[0-9]/
Disallow: /page/[2-9][0-9]/

# Tag archives (often thin content)
Disallow: /tag/

# Query parameters
Disallow: /*?replytocom=
Disallow: /*?preview=true

# Sitemap reference
Sitemap: https://example.com/sitemap_index.xml
```

### WooCommerce Store

```
# robots.txt for WooCommerce store
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

# WooCommerce private pages
Disallow: /cart/
Disallow: /checkout/
Disallow: /my-account/
Disallow: /order-received/
Disallow: /order/

# Filter/sorting URLs (prevent crawl budget waste)
Disallow: /*?orderby=
Disallow: /*?filter_
Disallow: /*?min_price=
Disallow: /*?max_price=
Disallow: /*?pa_*
Disallow: /*add-to-cart=*

# Faceted navigation creates duplicate content
Disallow: /product-category/*?

# Thank you pages
Disallow: /*order-received*
Disallow: /*view-order*

# WordPress defaults
Disallow: /trackback/
Disallow: /comments/feed/
Disallow: /?s=
Disallow: /tag/

# Sitemaps
Sitemap: https://example.com/sitemap_index.xml
Sitemap: https://example.com/product-sitemap.xml
```

### Multisite / Multi-domain

```
# robots.txt for WordPress Multisite (subdirectory install)
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

# Site 1
Disallow: /site1/wp-admin/
Allow: /site1/wp-admin/admin-ajax.php
Disallow: /site1/tag/

# Site 2
Disallow: /site2/wp-admin/
Allow: /site2/wp-admin/admin-ajax.php
Disallow: /site2/tag/

# Sitemaps for each site
Sitemap: https://example.com/sitemap_index.xml
Sitemap: https://example.com/site1/sitemap_index.xml
Sitemap: https://example.com/site2/sitemap_index.xml
```

### Staging Environment

```
# robots.txt for staging (block everything)
User-agent: *
Disallow: /

# Also enable in WordPress:
# Settings → Reading → Discourage search engines
```

**Remember:** Remove this before going live.

---

## What NOT to Block

### Common Mistakes

| Path | Why NOT to Block |
|------|------------------|
| `/wp-content/uploads/` | Contains images you want indexed |
| `/wp-content/plugins/` | May contain CSS/JS needed for rendering |
| `/wp-includes/` | Contains core CSS/JS needed for rendering |
| `/wp-content/themes/` | Contains CSS/JS needed for rendering |
| `*.css` | Blocks page rendering for bots |
| `*.js` | Blocks page rendering for bots |

Blocking CSS and JavaScript can cause Google to see a broken page, hurting your rankings.

### Testing in Search Console

Use Google Search Console's URL Inspection tool to see how Google renders your pages. If you've blocked CSS/JS, the preview will look broken.

---

## Crawl Budget Considerations

"Crawl budget" is how many pages Googlebot will crawl in a given time. For most small sites, this isn't a concern. For large sites (10,000+ pages), it matters.

### Signs of Crawl Budget Issues

- New content takes weeks to get indexed
- Pages deep in site structure never indexed
- Crawl stats in Search Console show low pages/day
- Server logs show repeated crawling of low-value URLs

### Strategies to Save Crawl Budget

#### 1. Block Low-Value URLs

```
# Internal search results
Disallow: /?s=
Disallow: /search/

# Calendar/archive pages
Disallow: /2023/
Disallow: /2024/

# Author archives (if multiple authors with thin content)
Disallow: /author/
```

#### 2. Use Clean URL Structures

```
# Block URLs with tracking parameters
Disallow: /*?utm_*
Disallow: /*?fbclid=
Disallow: /*?gclid=
Disallow: /*?ref=

# Block session IDs
Disallow: /*?sid=
Disallow: /*?session_id=
```

#### 3. Consolidate Duplicate Content

Instead of blocking, use canonical tags. But you can still reduce crawl requests:

```
# Pagination alternatives
Disallow: /*?page=
Disallow: /*&page=
```

---

## Bot-Specific Rules

Different search engines have different crawlers. You can set specific rules for each.

### Major Search Engine Bots

| Bot | User-agent | Notes |
|-----|------------|-------|
| Google | Googlebot | Primary web crawler |
| Google Images | Googlebot-Image | Image search |
| Google Ads | AdsBot-Google | Landing page quality |
| Bing | Bingbot | Microsoft search |
| Yandex | Yandex | Russian search |
| Baidu | Baiduspider | Chinese search |
| DuckDuckGo | DuckDuckBot | Privacy-focused |

### Bot-Specific Configuration

```
# Allow all for Googlebot (recommended default)
User-agent: Googlebot
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

# Block image crawling (if you don't want images indexed)
User-agent: Googlebot-Image
Disallow: /wp-content/uploads/private/

# Slower crawl for Bingbot (if causing server issues)
User-agent: Bingbot
Crawl-delay: 10

# Block specific bots entirely
User-agent: AhrefsBot
Disallow: /

User-agent: SemrushBot
Disallow: /

# Default for all others
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
```

### Crawl-Delay Directive

`Crawl-delay` tells bots to wait N seconds between requests. **Googlebot ignores this**—use Search Console instead.

```
User-agent: Bingbot
Crawl-delay: 5
```

---

## Sitemap References

Always include your sitemaps in robots.txt:

```
# Single sitemap
Sitemap: https://example.com/sitemap.xml

# Sitemap index (if using one)
Sitemap: https://example.com/sitemap_index.xml

# Multiple sitemaps
Sitemap: https://example.com/post-sitemap.xml
Sitemap: https://example.com/page-sitemap.xml
Sitemap: https://example.com/product-sitemap.xml
Sitemap: https://example.com/category-sitemap.xml
```

**Note:** You can reference sitemaps from different subdomains in the same robots.txt:

```
Sitemap: https://example.com/sitemap.xml
Sitemap: https://shop.example.com/sitemap.xml
```

---

## Testing and Validation

### Google Search Console

1. Go to Search Console → Settings → robots.txt Tester
2. Enter URLs to test
3. Check if blocked or allowed

### robots.txt Validators

- [Google robots.txt Tester](https://www.google.com/webmasters/tools/robots-testing-tool)
- [Bing Webmaster Tools](https://www.bing.com/webmasters/robotstxt)
- [Technical SEO robots.txt validator](https://technicalseo.com/tools/robots-txt/)

### Manual Testing

```bash
# Check if a specific path is blocked
curl -A "Googlebot" https://example.com/blocked-path/
```

---

## Common Mistakes

### 1. Blocking Everything Accidentally

```
# WRONG - blocks entire site
User-agent: *
Disallow: /

# Correct - only blocks admin
User-agent: *
Disallow: /wp-admin/
```

### 2. Using Disallow to Prevent Indexing

robots.txt only controls crawling, not indexing. Google can still index a URL from links even if blocked.

**To prevent indexing, use:**

```html
<meta name="robots" content="noindex">
```

Or HTTP header:
```
X-Robots-Tag: noindex
```

### 3. Forgetting Trailing Slashes

```
# These are different:
Disallow: /folder    # Blocks /folder, /folder-name, /folder123
Disallow: /folder/   # Only blocks /folder/ and /folder/*
```

### 4. Case Sensitivity

URLs are case-sensitive. `/Admin/` is different from `/admin/`:

```
# May need both if your site has inconsistent casing
Disallow: /wp-admin/
Disallow: /wp-Admin/
```

### 5. Blocking CSS/JS

```
# WRONG - breaks page rendering for bots
Disallow: *.css
Disallow: *.js

# Just don't block these at all
```

---

## Checking Crawl Activity

### Server Logs

```bash
# Find Googlebot requests in Apache logs
grep "Googlebot" /var/log/apache2/access.log | tail -100

# Count crawls per day
grep "Googlebot" /var/log/apache2/access.log | cut -d[ -f2 | cut -d: -f1 | sort | uniq -c
```

### Google Search Console

1. Settings → Crawl stats
2. See total requests, response times, file types
3. Identify if low-value pages are being crawled

---

## Dynamic robots.txt

For advanced use cases, generate robots.txt dynamically:

```php
// In functions.php or a plugin
add_filter( 'robots_txt', function( $output, $public ) {
    // Different rules for different environments
    if ( defined( 'WP_ENV' ) && WP_ENV === 'staging' ) {
        return "User-agent: *\nDisallow: /";
    }

    // Dynamic sitemap URLs
    $sitemaps = '';
    if ( function_exists( 'yoast_get_sitemap_urls' ) ) {
        foreach ( yoast_get_sitemap_urls() as $url ) {
            $sitemaps .= "Sitemap: $url\n";
        }
    }

    $rules = "User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Disallow: /cart/
Disallow: /checkout/

$sitemaps";

    return $rules;
}, 10, 2 );
```

## Further Reading

- [XML Sitemaps and Structured Data](./03-xml-sitemaps-and-structured-data.md) — Sitemap configuration
- [Technical SEO Fundamentals](./01-technical-seo-fundamentals.md) — Broader SEO context
- [Google robots.txt Specification](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt)
- [Robots Exclusion Standard](https://en.wikipedia.org/wiki/Robots_exclusion_standard)
