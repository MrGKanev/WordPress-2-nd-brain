# Modern WooCommerce Architecture

> Last reviewed: 2026-07
> Tested with: current WooCommerce developer guidance; verify APIs and extension support against the target WooCommerce release.
> Risk: High — order storage and checkout changes can affect purchases, fulfillment and customer data.

Modern WooCommerce development needs to work with more than the classic
WordPress-post and shortcode checkout model. New stores can use
High-Performance Order Storage (HPOS), and Cart and Checkout blocks use a
client-side data flow backed by the Store API. Build against WooCommerce APIs,
not against assumptions about database tables or checkout markup.

This chapter explains the architectural choices. See [WooCommerce Fundamentals](./01-woocommerce-fundamentals.md) for products and order concepts, [Checkout Customization](./04-checkout-customization.md) for classic checkout hooks, and [WooCommerce REST API](./07-woocommerce-rest-api.md) for authenticated back-office integrations.

## The Compatibility Matrix

Before writing a feature, identify the environment it must support.

| Concern | Classic implementation | Modern implementation | Practical rule |
|---------|------------------------|-----------------------|----------------|
| Order storage | `shop_order` posts and post meta | HPOS custom order tables | Use WooCommerce CRUD, never query order posts directly |
| Cart/checkout UI | Shortcodes and PHP templates | Cart and Checkout blocks with JavaScript extensibility | Detect and support the checkout experience the store uses |
| Customer-facing API | Custom AJAX or ad hoc REST | Store API, session-aware | Use Store API patterns for cart/checkout behavior |
| Admin/integration API | WooCommerce REST API | WooCommerce REST API | Authenticate and authorize server-to-server access |

Support is not a badge in a plugin header. It means the feature works with the
selected storage and checkout architecture, with correct totals, validation,
payment behavior and order data.

## HPOS: High-Performance Order Storage

Historically, WooCommerce stored orders as WordPress posts plus `postmeta`. HPOS
uses dedicated order tables and indexes. WooCommerce 8.2 enabled HPOS by default
for new installs; existing stores can migrate after checking compatibility.

This improves scalability, but code that relies on `WP_Query` for `shop_order`,
calls `get_post_meta()` for order data, or directly queries `wp_posts`/
`wp_postmeta` may be incompatible. Products are still WordPress post types; this
warning is specifically about orders and order-related data.

### Use the WooCommerce CRUD API

Use the public WooCommerce objects and accessors. They delegate to the active
data store, so the same code can work with both legacy and HPOS storage.

```php
// Read an order without assuming a database table.
$order = wc_get_order( $order_id );

if ( ! $order ) {
    return;
}

$email  = $order->get_billing_email();
$total  = $order->get_total();
$source = $order->get_meta( '_my_plugin_source', true );

// Persist custom order metadata through the object, then save once.
$order->update_meta_data( '_my_plugin_source', 'campaign-a' );
$order->save();
```

For collections, use `wc_get_orders()` and its documented query arguments rather
than `WP_Query`. If a use case truly requires custom SQL, treat it as an HPOS
compatibility project: use the active data-store APIs where possible and test
both storage modes.

### Declare Compatibility for a Plugin

Only declare compatibility after testing. WooCommerce documents the declaration
through `FeaturesUtil`; run it early enough for WooCommerce to discover it.

```php
use Automattic\WooCommerce\Utilities\FeaturesUtil;

add_action( 'before_woocommerce_init', function() {
    if ( class_exists( FeaturesUtil::class ) ) {
        FeaturesUtil::declare_compatibility(
            'custom_order_tables',
            __FILE__,
            true
        );
    }
} );
```

Setting the final argument to `true` without a real test matrix creates risk for
store owners. If an extension is not compatible, declare `false` or omit the
declaration until it is fixed.

### Enable HPOS Safely on an Existing Store

1. Update WooCommerce, extensions and custom code on a production-like staging
   clone.
2. Check every extension's HPOS compatibility status in WooCommerce settings.
3. Take and verify a restorable backup.
4. Test key operations: order creation, payment callbacks, refunds, fulfillment,
   subscriptions, exports and custom admin screens.
5. Confirm synchronization has no pending orders before switching authoritative
   tables.
6. Schedule the production switch, monitor it and keep a reconciliation plan for
   transactions created during the window.

Do not edit HPOS tables manually. Use WooCommerce APIs, imports or documented
migration tools.

## Cart and Checkout Blocks

The Cart and Checkout blocks replace the legacy shortcode/template experience
with a block-based UI. Their JavaScript data stores manage UI state, while the
server remains the source of truth for cart items, totals, shipping, customer
data and orders.

This changes extension design:

- PHP filters that alter legacy checkout fields or template markup may not affect
  the block checkout.
- Client-side extensions should use the documented WooCommerce block APIs and
  data stores, not private React internals or DOM selectors.
- Information that must persist with an order needs a server-side path through
  the Store API/checkout flow, not only browser state.
- Payment gateways must explicitly support the block checkout experience.

### Choose the Right Extension Point

| Need | Preferred approach |
|------|--------------------|
| Display an extra component in Cart/Checkout | Documented Slot and Fill or an allowed inner block |
| Add a checkout field that must be saved | Additional Checkout Fields API or documented block extensibility |
| Add cart/checkout data for an extension | Extend the Store API schema and validate server-side |
| Change a label or presentation detail | Official checkout filters where available |
| Integrate a payment method | WooCommerce payment-method integration for blocks; test its full lifecycle |
| Change legacy shortcode checkout | Classic hooks/templates, with a separate blocks plan if required |

Do not use a visual DOM insertion as a checkout integration. A theme update,
translation, validation rerender or accessibility change can break it without a
PHP error.

## Store API vs WooCommerce REST API

These APIs solve different problems.

| API | Typical caller | Authentication | Appropriate data |
|-----|----------------|----------------|------------------|
| Store API (`wc/store/v1`) | Storefront browser/app | Session-aware; write endpoints require nonce or cart token | Current shopper's products, cart and checkout |
| WooCommerce REST API (`wc/v3`) | ERP, mobile backend, trusted integration | Authenticated | Back-office products, orders, customers and settings as authorized |

The Store API is intentionally not an unauthenticated way to query arbitrary
orders or customers. Use the authenticated REST API for server-to-server
integrations and enforce capabilities in any custom routes.

```bash
# Public product data for the current storefront context.
curl 'https://example.com/wp-json/wc/store/v1/products?per_page=12'

# The cart is specific to the current shopper session.
curl 'https://example.com/wp-json/wc/store/v1/cart'
```

For cart-changing or checkout requests, obtain and send the required nonce or
cart token through WooCommerce's documented flow. Do not invent an API key in
browser JavaScript or expose REST credentials to shoppers.

## Test the Whole Purchase Lifecycle

Use a staging store with sandbox payments and an order storage mode that matches
the scenario being tested. Test both guest and logged-in shoppers.

### HPOS Extension Checklist

- [ ] No direct order queries against `wp_posts` or `wp_postmeta`
- [ ] Order reads and writes use WooCommerce CRUD or documented query APIs
- [ ] Compatibility declaration matches real test results
- [ ] Order list/admin actions, exports, refunds and webhooks work
- [ ] Background jobs and custom reporting work with the selected data store

### Blocks and Store API Checklist

- [ ] Cart and Checkout blocks render without console errors
- [ ] Add/remove item, coupon, shipping and totals update correctly
- [ ] Required custom fields validate, persist and are visible where expected
- [ ] Payment methods appear, authorize and handle failure/success correctly
- [ ] Order confirmation, emails and webhooks contain expected data
- [ ] Guest/session behavior works after refresh and in a new browser
- [ ] Accessibility is tested with keyboard navigation and inline validation

### Rollback Considerations

Disable a new block integration or return to a prior release only after checking
the current checkout still processes orders. For HPOS, do not switch data-store
authority while synchronization is pending. A rollback that restores an older
database can lose new orders; use the recovery and reconciliation process in
[Backups & Disaster Recovery](../02-maintenance/09-backup-disaster-recovery.md).

## Common Mistakes

| Mistake | Better approach |
|---------|-----------------|
| Querying order posts directly | Use `wc_get_order()`, order objects and `wc_get_orders()` |
| Declaring HPOS compatible without testing | Test actual workflows, then declare honestly |
| Assuming classic checkout hooks work in blocks | Implement and test a block-compatible extension path |
| Exposing REST API credentials in frontend code | Use Store API session mechanisms or a protected backend |
| Treating browser state as order data | Validate and persist transaction-critical data server-side |
| Switching HPOS on a live store without a rehearsal | Test a production-like clone, backup and monitor migration |

## Further Reading

- [HPOS documentation](https://developer.woocommerce.com/docs/features/high-performance-order-storage/) — Storage model and migration behavior
- [HPOS extension recipe book](https://developer.woocommerce.com/docs/features/orders/high-performance-order-storage/recipe-book/) — Compatibility patterns
- [Store API](https://developer.woocommerce.com/docs/apis/store-api/) — Customer-facing API reference
- [Cart and Checkout extensibility](https://developer.woocommerce.com/docs/block-development/extensible-blocks/cart-and-checkout-blocks) — Official extension overview
- [Checkout Customization](./04-checkout-customization.md) — Existing classic checkout patterns
