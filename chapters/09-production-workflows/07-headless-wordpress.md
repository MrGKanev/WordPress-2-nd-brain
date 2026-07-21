# Headless WordPress

Headless WordPress uses WordPress as a content and commerce backend while a separate frontend renders the visitor experience. It can improve frontend flexibility, but it also moves familiar WordPress features—preview, caching, authentication and routing—into custom architecture.

## When It Fits

- Multiple channels consume the same structured content.
- The product needs a frontend framework or interaction model beyond a traditional theme.
- The team can own two deployable applications and their integration.

## Questions Before Adopting It

Define API authentication, draft previews, cache invalidation, SEO rendering, media handling and failure behavior when either application is unavailable. For many editorial sites, a block theme is simpler and delivers the same business outcome with less operational cost.

See [WordPress REST API](../08-plugin-development/06-rest-api.md) and [WooCommerce REST API](../06-e-commerce/07-woocommerce-rest-api.md).

## Architecture Boundaries

Write down which system owns each responsibility. WordPress usually owns editorial data, roles, media and commerce records. The frontend owns rendering, client-side interaction and often visitor-facing routing. A CDN or edge layer may own public-response caching.

The boundary is especially important for preview and authentication. Editors expect a draft preview to show unpublished content without making it public. Customers expect account pages and carts to remain private even if the rest of the site is aggressively cached.

| Capability | Traditional theme | Headless implementation must provide |
|------------|-------------------|--------------------------------------|
| Preview | Built in | Signed preview link and draft-data access |
| SEO HTML | PHP renders it | Server/edge rendering or static generation |
| Cache purge | Plugin integration | Webhook or API-driven revalidation |
| Authentication | WordPress cookies | Deliberate token or shared-session design |

## API Design

Expose only the fields the frontend needs. Version custom endpoints, validate every input and apply permission callbacks on the server. Do not use an administrator credential in browser code to make WordPress APIs convenient.

Choose a failure mode before launch. A stale public page may be acceptable while WordPress is temporarily unavailable; showing stale account or checkout data is not. Define timeouts, retries and error presentation for each API dependency.

## Decision Check

Headless is worthwhile when it solves a clear product requirement. It is not automatically a performance upgrade: it can add API round trips, cache-invalidation complexity and a second operational surface. Prototype the critical content, preview and commerce flows before committing to a migration.

## Delivery and Revalidation

Choose how public pages are delivered before building the frontend:

| Approach | Strength | Operational cost |
|----------|----------|------------------|
| Server-rendered frontend | Fresh content on every request | Requires frontend runtime capacity |
| Static generation | Fast, cheap public delivery | Needs reliable rebuild or revalidation |
| Incremental/edge rendering | Balanced freshness and speed | Provider-specific cache behavior |

For static or incremental sites, WordPress should notify the frontend after a published post, changed product, deleted page or taxonomy update. The notification must be authenticated, idempotent and observable. A failed revalidation should be retried from a queue; it should not depend on the editor clicking "Update" a second time.

## Contract Tests

The API response is a contract between two applications. A harmless-looking WordPress change—renaming a meta field, changing a block, disabling a plugin—can break a deployed frontend.

Keep representative API fixtures for important endpoints and test that required fields, types and permission behavior remain compatible. Also test the frontend against a staging WordPress instance during releases. This catches integration failures before an editor publishes content that the frontend cannot render.

## Editorial Experience

Do not accept a worse editing experience as the price of a modern frontend. Draft previews, scheduled publishing, redirects, responsive images and SEO metadata need an explicit owner. Pilot the workflow with real editors and a real content migration; technical success without editorial success usually becomes expensive custom support later.
