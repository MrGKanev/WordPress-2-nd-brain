# Commerce Operations II: Returns, Fraud & Marketplaces

Payments and fulfilment are only part of store operations. Returns, chargebacks, fraud signals and marketplace feeds require clear policies and data ownership to avoid financial loss and poor customer support.

## Returns and Exchanges

Define what starts a return, who approves it, how inventory changes and when a refund is issued. A return request is not automatically a refunded payment; products may need inspection, restocking or exclusion under the store policy.

| Event | Record | Owner |
|-------|--------|-------|
| Return requested | Reason, items, customer contact | Support |
| Return authorized | Label/instructions, deadline | Operations |
| Item received | Condition and stock disposition | Warehouse |
| Refund issued | Provider refund ID and amount | Finance/support |

Keep customer-facing status messages aligned with internal states. An exchange should reserve replacement stock deliberately; otherwise a returned item can be processed while its replacement sells out.

## Fraud and Chargebacks

Use gateway risk tools and business rules as signals, not unquestioned verdicts. Log the decision and reason for manual review, minimize access to fraud-related personal data, and define who can cancel, capture or hold an order.

Prepare evidence for disputes: order record, payment event, delivery proof and customer communication. Never store prohibited payment-card data in WordPress order notes or custom fields.

## Marketplace and Product Feeds

Marketplace integrations need a field mapping, feed schedule and reconciliation process. Assign a source of truth for price, stock, titles and product identifiers. Monitor rejected feed items and rate limits; a feed that succeeds technically can still publish stale or non-compliant product data.

See [WooCommerce Operations & Integrations](../09-production-workflows/08-woocommerce-operations.md), [Shipping Configuration](../06-e-commerce/06-shipping-configuration.md) and [Payment Gateways](../06-e-commerce/05-payment-gateways.md).

## Operational Controls

Separate the ability to view an order from the ability to issue a refund, change stock or export customer data. Keep an audit trail for manual adjustments and require an order note that explains an exceptional refund, cancellation or stock correction.

Review a small operations dashboard every day during busy periods:

- orders pending payment beyond the normal window;
- fulfilment exceptions and delayed shipments;
- returns awaiting inspection or refund;
- negative or mismatched inventory;
- marketplace feed rejections and chargeback notices.

These controls are not bureaucracy. They make small discrepancies visible before they become a customer complaint, an oversell or a month-end accounting problem.
