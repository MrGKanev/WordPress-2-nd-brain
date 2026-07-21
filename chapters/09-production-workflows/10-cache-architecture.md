# Cache Architecture & Invalidation

Caching is an architecture decision across browser, CDN, page, object and database layers. The hard part is defining who may receive a cached response and exactly when it becomes invalid.

## Cache Design Questions

- Which pages are public, which are personalized and which must never be cached?
- Which inputs vary a response: login state, cart, currency, locale, device or geolocation?
- What content change invalidates which URLs, API responses and edge entries?
- How will a deployment, price change or incident safely purge stale data?

Use cache keys and bypass rules that reflect these answers. Test with separate guest and logged-in sessions, and add a cache-status header during debugging. A high hit ratio is not a success if it can show the wrong price, cart or private content.

See [Object Caching](../04-performance/14-object-caching.md), [CDN Strategy](../04-performance/19-cdn-strategy.md) and [WooCommerce Performance](../06-e-commerce/03-woocommerce-performance.md).

## Layers and Responsibilities

Each layer should have a clear job:

| Layer | Good candidates | Do not store here carelessly |
|-------|-----------------|------------------------------|
| Browser | Versioned assets, public pages | Personalized account data |
| CDN/edge | Public HTML, images, scripts | Cart, checkout and private API responses |
| Page cache | Anonymous pages with stable variants | Logged-in or cookie-personalized pages |
| Object cache | Reusable WordPress objects and query results | Durable business records without a persistence plan |
| Application cache | Expensive computed results with explicit expiry | Values whose invalidation is unknown |

More layers do not automatically mean a faster site. Add a cache only when its key, expiry, invalidation and failure behavior are understood.

## Invalidation Design

List the events that change visitor-visible data: post publish, product price change, stock update, translation update, deployment and permission change. For each event, define the precise cache entries that should be purged or revalidated.

```text
Product price changes
  → product page
  → relevant category/archive pages
  → product API response
  → search or feed index, if it stores the price
```

Prefer targeted invalidation over purging the whole cache. A global purge makes the next burst of visitors rebuild every page through PHP and can create an avoidable capacity incident.

## Test for Correctness

During cache testing, use separate browser profiles for an anonymous visitor, a shopper with a cart and a logged-in customer. Check response headers, currency and language variants, prices, stock, permissions and cache purge behavior after an edit. Treat a personalization leak as a security bug even if the site scores well in a speed test.

## A Cache Test Script

Use repeatable requests when changing cache rules. Response headers reveal whether a page is being served, bypassed or refreshed as expected:

```bash
# Inspect a public page and its cache-related headers.
curl -I https://example.com/products/example-product/

# Repeat after changing the underlying content to confirm invalidation.
curl -I -H 'Cache-Control: no-cache' \
  https://example.com/products/example-product/
```

The exact headers depend on the CDN and web server. Configure a non-sensitive diagnostic header such as `X-Cache-Status` in a protected testing environment; remove it or limit it when it exposes infrastructure details you do not want to publish.

## Deployments and Cache

Code deployments can change templates, asset names and response behavior without changing WordPress content. Include cache invalidation in the release procedure:

1. Publish versioned static assets so browsers can safely cache them for a long time.
2. Revalidate pages whose markup or data shape changed.
3. Avoid a global purge unless a targeted purge cannot restore correctness.
4. Monitor origin load and error rate after the deployment.

If a full purge is necessary, consider warming the most important public URLs at a controlled rate. Cache warming is a capacity tool, not a replacement for correct invalidation rules.
