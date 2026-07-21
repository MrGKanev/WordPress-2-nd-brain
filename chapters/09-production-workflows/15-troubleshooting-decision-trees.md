# Troubleshooting Decision Trees

Decision trees prevent a stressful incident from becoming random configuration changes. Start with user impact, collect evidence, change one variable at a time and preserve a recovery path.

## Site Is Slow

```text
Is the page served from public cache?
  Yes → Check CDN/page-cache hit rate, cache TTL and asset delivery.
  No  → Is the delay PHP, database or external HTTP?
           PHP → Check PHP-FPM workers, slow log and heavy hooks.
           DB  → Check slow queries, locks, buffer/cache and table growth.
           HTTP→ Check timeout, dependency status and retry behavior.
```

Compare a public request with an authenticated or cart request. If only dynamic requests are slow, changing CDN settings will not solve the problem. If all requests are slow, inspect infrastructure saturation and recent deployments first.

## Checkout or Payment Fails

```text
Can the issue be reproduced with a sandbox payment?
  No  → Check provider dashboard, webhook delivery and real order evidence.
  Yes → Did WooCommerce create an order?
           No  → Inspect browser errors, validation, sessions and server logs.
           Yes → Check gateway response, order notes and webhook processing.
```

Do not retry a charge or refund until the provider record has been checked. A timeout does not prove that a payment failed; it may mean the response was lost after the provider completed the action.

## Deployment Caused Errors

```text
Did the error start with the latest deployment?
  Yes → Can the release be rolled back without reversing data?
           Yes → Roll back, verify recovery, then investigate on staging.
           No  → Disable the affected feature or use compatibility code.
  No  → Check dependency, infrastructure and traffic changes.
```

Collect the release identifier, timestamps, stack traces and affected URLs before cache purges or retries remove useful evidence. If a rollback succeeds, keep the failed artifact and notes for a blameless follow-up.

## Cron or Queue Is Backed Up

Check whether cron is scheduled externally, whether a worker is running, and whether failures are concentrated in one action group or integration. Retry only idempotent tasks. For non-idempotent jobs such as charging a payment or creating an external shipment, reconcile the external system before retrying.

See [WordPress Cron Management](../04-performance/04-cron-management.md), [Debugging & Profiling Tools](../04-performance/10-debugging-profiling.md) and [WooCommerce Operations & Integrations](./08-woocommerce-operations.md).
