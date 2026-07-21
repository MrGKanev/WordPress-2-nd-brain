# WooCommerce Operations & Integrations

An online store continues working after a page response ends: payments update asynchronously, stock synchronizes with external systems and fulfilment services call webhooks. These workflows need the same care as checkout itself.

## Core Rules

- Treat webhook delivery as at-least-once: verify signatures and make handlers idempotent.
- Record external IDs and processing status so retries do not create duplicate orders, refunds or shipments.
- Define which system owns inventory, price and order status when an ERP, warehouse or marketplace is connected.
- Monitor failed actions and payment-status mismatches; do not rely on email alone.

Test delayed payment confirmation, duplicate webhooks, partial refunds, stock conflicts and an unavailable integration. The safe result is a recoverable queue and a clear operational procedure, not silent data loss.

See [Payment Gateways](../06-e-commerce/05-payment-gateways.md), [WooCommerce REST API](../06-e-commerce/07-woocommerce-rest-api.md) and [Background Processing](../08-plugin-development/10-background-processing.md).

## Webhook Handling Pattern

Never assume that a webhook arrives once, in order or immediately. A provider can retry it after a timeout, deliver a later status first or send the same event more than once.

```text
Receive request
  → verify provider signature and timestamp
  → store event ID durably
  → acknowledge quickly
  → process asynchronously
  → mark the event completed or retry safely
```

Use the provider's event ID as an idempotency key. If it has already completed, return a successful response without repeating the side effect. Keep failed events and their error details long enough for an operator to resolve them; do not discard them after a few blind retries.

## Source-of-Truth Matrix

Integrations fail when two systems can silently overwrite the same field. Before connecting an ERP, warehouse or marketplace, assign ownership.

| Data | Typical owner | Integration rule |
|------|---------------|------------------|
| Product copy and images | WordPress | Publish outward on approved changes |
| SKU and inventory | ERP/WMS | Import updates; prevent conflicting manual writes |
| Payment state and refund ID | Payment provider | Verify against signed provider events |
| Order fulfilment state | Warehouse/ERP | Map external states explicitly to WooCommerce states |

The actual owners may differ, but every field needs one. Include conflict behavior for a simultaneous update and an outage.

## Operational Runbook

Create a simple runbook for failed payments, inventory mismatch, stuck scheduled actions and a provider outage. It should identify the dashboard or log to check, the safe retry method, the person who can contact the provider and the customer-facing response. A recovery procedure is part of the integration—not an afterthought for the next incident.

## Payment-State Reconciliation

The payment provider is the authority for whether funds were captured or refunded. WooCommerce is the authority for the order record and customer communication. Reconcile the two regularly, especially after an outage or deployment.

| Situation | Safe response |
|-----------|---------------|
| Provider captured payment, order remains pending | Verify event history; update once through the gateway's supported flow |
| Order says paid, provider has no matching payment | Stop fulfilment and investigate the gateway record |
| Refund request timed out | Check provider before retrying; a retry can create a duplicate refund |
| Webhook verification fails | Preserve the event safely, alert the owner and do not trust its payload |

Never repair payment state by editing database rows directly. Use WooCommerce and gateway APIs so notes, stock changes, email and audit history remain coherent.

## Inventory Safeguards

Inventory synchronization needs a documented reservation policy. Decide when stock is reserved, how long an unpaid order holds it, and what returns it to sale. This becomes critical for limited stock, bank transfer payments and high-volume sale periods.

Monitor for negative stock, delayed imports, unprocessed queue actions and mismatches between the source system and WooCommerce. Define thresholds that create a human review rather than automatically overwriting stock after a conflicting update.

## Integration Test Matrix

At minimum, test a successful payment, declined payment, delayed confirmation, duplicate webhook, partial refund, out-of-stock product and provider timeout. Run this matrix on staging after gateway or integration updates and before major sales campaigns.
