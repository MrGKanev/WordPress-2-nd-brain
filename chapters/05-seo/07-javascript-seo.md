# JavaScript SEO

Google can render JavaScript, but not perfectly and not immediately. When your content depends on JavaScript to appear in the DOM, you're adding complexity to how search engines discover and index your pages. This matters for headless WordPress, React-based frontends, and any site that relies heavily on client-side rendering.

## How Google Renders JavaScript

Google's crawling and indexing pipeline has two phases:

```
Phase 1: Crawl
  Googlebot fetches HTML → Processes raw HTML → Extracts links
  (Immediate — happens during crawl)

Phase 2: Render
  Web Rendering Service (WRS) → Executes JavaScript → Processes rendered DOM
  (Delayed — can take seconds to weeks)
```

The gap between Phase 1 and Phase 2 is the problem. Content that only exists after JavaScript runs might not be indexed for days or weeks. Links that only appear after rendering might not be discovered during the initial crawl.

### What Google Can and Can't Do

| Capability | Status |
|-----------|--------|
| Execute modern JavaScript (ES6+) | Yes |
| Render React, Vue, Angular | Yes (with caveats) |
| Wait for async data fetching | Usually (timeout ~5 seconds) |
| Interact with the page (click, scroll) | No |
| Handle infinite scroll | No (needs pagination links) |
| Process lazy-loaded content below fold | Sometimes |
| Handle authenticated content | No |
| See content behind user interaction (tabs, accordions) | Only if in the DOM |

## WordPress and JavaScript SEO

### Standard WordPress: No Problem

Out of the box, WordPress is server-rendered PHP. HTML is complete before it reaches the browser. JavaScript SEO isn't a concern for standard WordPress sites — even with the block editor, all content is saved as HTML in the database.

### When JavaScript SEO Matters for WordPress

| Scenario | Risk Level |
|----------|-----------|
| Standard WordPress (classic or block themes) | None |
| WordPress with AJAX-loaded content (load more, infinite scroll) | Low-Medium |
| WordPress with heavy JavaScript-dependent features | Medium |
| Headless WordPress with React/Next.js frontend | High |
| WordPress as API-only backend | High |

## Headless WordPress SEO

Using WordPress as a headless CMS (REST API or WPGraphQL) with a JavaScript frontend introduces significant SEO challenges.

### Rendering Strategies

| Strategy | SEO Impact | Performance | Complexity |
|----------|-----------|-------------|-----------|
| **Server-Side Rendering (SSR)** | Best | Fast initial load | Medium |
| **Static Site Generation (SSG)** | Best | Fastest | Medium-High |
| **Client-Side Rendering (CSR)** | Poor | Slow initial, fast after | Low |
| **Incremental Static Regeneration (ISR)** | Best | Fast, fresh content | Medium |

### Next.js with WordPress (Recommended)

Next.js is the most common framework for headless WordPress because it supports all rendering strategies:

```
WordPress (CMS) → REST API / WPGraphQL → Next.js → HTML
```

Key SEO features Next.js provides:
- **SSR/SSG**: Content is HTML when Googlebot arrives
- **Head management**: `next/head` for meta tags, Open Graph
- **Automatic sitemap generation**: Via plugins like `next-sitemap`
- **Image optimization**: `next/image` for responsive images

### SEO Checklist for Headless WordPress

| Requirement | How to Handle |
|-------------|--------------|
| Meta tags (title, description) | Framework head management (Next.js `metadata`, Nuxt `useHead`) |
| Open Graph / Twitter cards | Same as above |
| Canonical URLs | Generate from WordPress permalink structure |
| XML sitemap | Generate from WordPress data, serve from frontend |
| robots.txt | Serve from frontend, point to sitemap |
| Hreflang | Generate per-page if multilingual |
| Structured data (JSON-LD) | Inject from WordPress custom fields or ACF |
| Internal linking | Use `<a>` tags with actual URLs, not JS navigation only |
| 301 redirects | Handle in framework or reverse proxy |
| 404 pages | Return actual 404 status codes, not soft 404s |

## AJAX Content Loading

WordPress sites often load content dynamically — "Load More" buttons, infinite scroll, filter/search without page reload.

### Load More / Infinite Scroll

The problem: Googlebot doesn't click buttons or scroll. Content loaded via AJAX isn't in the initial HTML.

**Solution: Paginated archive links**

```php
// Ensure pagination links exist in HTML (even if hidden by CSS/JS)
the_posts_pagination( array(
    'mid_size'  => 2,
    'prev_text' => '&laquo; Previous',
    'next_text' => 'Next &raquo;',
) );
```

Then enhance with JavaScript:

```javascript
// Progressively enhance pagination with AJAX load-more
document.querySelector('.load-more-button')?.addEventListener('click', function() {
    // Fetch next page via AJAX
    // Append to existing content
    // Update URL with history.pushState() for shareable URLs
});
```

The key: HTML pagination exists for bots. JavaScript enhances it for users.

### Filtered Content

Product filters, search results, and sorted listings that change content without page reload:

| Approach | SEO Friendly? |
|----------|--------------|
| URL updates with `pushState` | Yes — Google sees each filter state as a URL |
| No URL change | No — filtered content is invisible to Google |
| Hash-based URLs (`#filter=blue`) | No — Google ignores hash fragments |

```javascript
// Update URL when filters change
history.pushState(null, '', '?color=blue&size=m');
```

## Lazy Loading and SEO

### Images

WordPress adds `loading="lazy"` by default. This is fine — Google handles lazy-loaded images well. But the `src` or `srcset` attribute must contain the actual image URL (not a placeholder that gets swapped by JavaScript).

```html
<!-- Good: Native lazy loading -->
<img src="product.jpg" loading="lazy" alt="Product">

<!-- Bad: JavaScript-only image loading -->
<img data-src="product.jpg" src="placeholder.gif" alt="Product">
```

### Content

Content that loads when scrolled into view (intersection observer patterns):

| Pattern | Google Can See It? |
|---------|-------------------|
| Content in DOM but hidden with CSS | Yes |
| Content loaded via intersection observer | Sometimes (depends on viewport simulation) |
| Content loaded on click/interaction | No |
| Accordion/tab content in DOM | Yes (even if collapsed) |

**Best practice:** Always include content in the initial HTML. Use JavaScript to enhance the display (collapse, animate, lazy-render) but not to load the content itself.

## Testing JavaScript Rendering

### Google Search Console

```
URL Inspection → Test Live URL → View Tested Page → Screenshot
```

Compare "HTML" tab vs "Screenshot" tab. If content appears in the screenshot but not the HTML, it's JavaScript-rendered and at risk of delayed indexing.

### Tools

| Tool | What It Shows |
|------|-------------|
| **Google Rich Results Test** | Rendered page + detected structured data |
| **Google URL Inspection** | How Google sees your page |
| **Puppeteer / Playwright** | Headless browser rendering (simulate Googlebot) |
| **Chrome DevTools → Disable JavaScript** | What your page looks like without JS |

### Quick Test: Disable JavaScript

1. Open Chrome DevTools (F12)
2. Cmd+Shift+P → "Disable JavaScript"
3. Reload the page
4. If critical content disappears, you have a JavaScript SEO problem

## Dynamic Rendering

A middle-ground approach: serve pre-rendered HTML to bots, JavaScript to users.

```
User → JavaScript-rendered page
Googlebot → Pre-rendered HTML snapshot
```

### Implementation Options

| Service | How It Works |
|---------|-------------|
| **Prerender.io** | Cloud service, caches rendered pages |
| **Rendertron** | Google's open-source headless Chrome service |
| **Puppeteer** | Self-hosted rendering |

Google officially supports dynamic rendering as a workaround, but recommends SSR as the long-term solution.

### Nginx Configuration for Dynamic Rendering

```nginx
# Detect bots and proxy to pre-render service
map $http_user_agent $prerender {
    default       0;
    "~*googlebot" 1;
    "~*bingbot"   1;
    "~*yandex"    1;
}

location / {
    if ($prerender) {
        proxy_pass https://service.prerender.io;
    }
    try_files $uri $uri/ /index.html;
}
```

## Core Web Vitals and JavaScript

JavaScript directly impacts Core Web Vitals:

| Metric | JavaScript Impact |
|--------|------------------|
| **LCP** | Heavy JS delays rendering of largest content |
| **INP** | Long tasks block interaction responsiveness |
| **CLS** | JS that injects content causes layout shifts |

### Mitigation

- **Code split**: Load only the JavaScript needed for the current page
- **Defer non-critical JS**: Use `defer` or `async` attributes
- **Minimize main thread work**: Move heavy computation to Web Workers
- **Avoid DOM manipulation after load**: Causes CLS

## WordPress-Specific JavaScript Concerns

### Block Editor Output

Gutenberg blocks are saved as HTML, so block content is server-rendered. But some dynamic blocks fetch content via JavaScript:

| Block Type | Rendering | SEO Impact |
|-----------|-----------|-----------|
| Static blocks (paragraph, image, etc.) | Server HTML | None |
| Dynamic blocks (latest posts, query loop) | Server PHP → HTML | None |
| Interactive blocks (Interactivity API) | Server HTML + client enhancement | None (progressive enhancement) |
| Third-party blocks loading external data | Varies | Check if content is in initial HTML |

### Cart Fragments

WooCommerce's `wc-ajax=get_refreshed_fragments` adds JavaScript overhead. It's not an SEO issue (cart isn't indexed) but affects Core Web Vitals.

## Further Reading

- [Technical SEO Fundamentals](./01-technical-seo-fundamentals.md) — Core crawl/index concepts
- [Performance Optimization for SEO](./04-performance-optimization-for-seo.md) — Core Web Vitals
- [Frontend Asset Optimization](../04-performance/13-frontend-asset-optimization.md) — JavaScript optimization
- [Google's JavaScript SEO Guide](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) — Official documentation
