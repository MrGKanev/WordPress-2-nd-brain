# Lab: Design a Webhook Processor

This lab models the safe path for an external event. It does not connect to a live provider; use a provider's sandbox documentation for the exact signature format and event schema.

## Event Path

```text
Provider request
  → verify signature and timestamp
  → store event ID
  → return HTTP success quickly
  → process in a queue
  → record completion or safe failure
```

## Implementation Checklist

- [ ] Read the raw request body before modifying it.
- [ ] Compare the supplied signature with an HMAC using `hash_equals()`.
- [ ] Reject old timestamps to reduce replay risk.
- [ ] Use the provider event ID as an idempotency key.
- [ ] Persist receipt before replying successfully.
- [ ] Move network calls and expensive updates to Action Scheduler or another worker.

## Test Cases

| Request | Expected result |
|---------|-----------------|
| Valid signed event | Accepted once and queued |
| Same event ID twice | Second request succeeds without repeating work |
| Invalid signature | Rejected and recorded safely |
| Provider timeout after delivery | Reconciliation discovers the completed event |
| Worker failure | Event remains visible for controlled retry |

Do not use a browser redirect, a public query parameter or a generic WordPress nonce as webhook authentication. The sender is a server, so verification must use the provider's server-to-server scheme.

See [Integration Architecture](../10-platform-architecture-governance/07-integration-architecture.md) and [WooCommerce Operations & Integrations](../09-production-workflows/08-woocommerce-operations.md).
