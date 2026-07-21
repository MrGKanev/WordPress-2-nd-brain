# Lab: Validate a Cache Change

This lab verifies correctness before treating a cache change as a performance win. Use a staging URL and two separate browser profiles.

## Test Matrix

| Visitor | Page | Expected behavior |
|---------|------|-------------------|
| Anonymous | Public product page | Cacheable response with correct public content |
| Shopper with cart | Homepage/product | Bypasses shared cache; cart count stays correct |
| Logged-in customer | Account page | Never receives shared cached HTML |
| Editor after update | Changed page | Updated content appears after intended invalidation |

## Commands

```bash
# Inspect response headers for a public page.
curl -I https://staging.example.com/products/example-product/

# Record headers before and after a content change.
curl -s -D - -o /dev/null https://staging.example.com/products/example-product/
```

Compare cache-status, `Cache-Control` and `Vary` headers with the expected rules for the CDN or web server. Do not assume that a `HIT` is correct: it may be a hit for the wrong visitor variant.

## Rollback

Keep the previous cache rule or configuration revision available. If a shopper sees stale cart, price or private data, disable the affected cache rule first, purge the relevant entries, then investigate with the recorded cookies and headers.

See [Cache Architecture & Invalidation](../09-production-workflows/10-cache-architecture.md).
