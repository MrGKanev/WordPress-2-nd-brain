# WooCommerce Fundamentals

Understanding WooCommerce architecture will save you hours of debugging. Here's the knowledge that's usually learned the hard way.

## Architectural Philosophy

WooCommerce is built on top of WordPress, maximizing use of existing systems:

| WooCommerce Concept | WordPress Equivalent |
|--------------------|---------------------|
| Products | Custom Post Type (`product`) |
| Orders | Custom Post Type (`shop_order`) |
| Coupons | Custom Post Type (`shop_coupon`) |
| Product Categories | Custom Taxonomy (`product_cat`) |
| Product Tags | Custom Taxonomy (`product_tag`) |
| Product Attributes | Custom Taxonomy (dynamic) |

**Why this matters:** You can use standard WordPress functions like `get_posts()`, `WP_Query`, `get_terms()` to work with WooCommerce data.

## Data Storage Model

### Products and Post Meta

Product data is stored in two places:

```
wp_posts (core data)
├── post_title = Product name
├── post_content = Full description
├── post_excerpt = Short description
└── post_status = publish/draft/etc

wp_postmeta (everything else)
├── _price = Current price
├── _regular_price = Regular price
├── _sale_price = Sale price
├── _sku = SKU
├── _stock = Stock quantity
├── _stock_status = instock/outofstock
└── ... hundreds of other meta keys
```

### HPOS: High-Performance Order Storage

From WooCommerce 8.2, orders can be stored in **custom tables** instead of post meta:

```
wp_wc_orders (core order data)
wp_wc_orders_meta (order meta)
wp_wc_order_addresses (billing/shipping)
wp_wc_order_items (line items)
```

**Why HPOS matters:**
- 5-10x faster order queries with many orders
- Cleaner database structure
- Better scalability

**Check if HPOS is active:**
```php
// Don't use get_post() for orders if HPOS is active
if ( wc_get_container()->get( \Automattic\WooCommerce\Internal\DataStores\Orders\CustomOrdersTableController::class )->custom_orders_table_usage_is_enabled() ) {
    // Always use wc_get_order()
}
```

**Practical tip:** Always use `wc_get_order()` instead of `get_post()` for orders. It works with both storage modes.

## Key Objects and Functions

### WC_Product

```php
// Get a product
$product = wc_get_product( $product_id );

// Core methods
$product->get_name();           // Product name
$product->get_price();          // Current price (after discounts)
$product->get_regular_price();  // Regular price
$product->get_sale_price();     // Sale price
$product->get_sku();            // SKU
$product->get_stock_quantity(); // Stock count
$product->is_in_stock();        // Boolean
$product->is_on_sale();         // Boolean
$product->get_type();           // simple, variable, grouped, external
```

### WC_Order

```php
// Get an order
$order = wc_get_order( $order_id );

// Core methods
$order->get_status();           // pending, processing, completed, etc
$order->get_total();            // Order total
$order->get_billing_email();    // Customer email
$order->get_items();            // Array of order items
$order->get_payment_method();   // Payment gateway ID
$order->get_date_created();     // WC_DateTime object
```

### WC_Cart

```php
// Cart is a singleton, accessible via WC()
WC()->cart->get_cart();         // Array of cart items
WC()->cart->get_cart_total();   // Formatted total
WC()->cart->get_cart_contents_count(); // Item count
WC()->cart->add_to_cart( $product_id, $quantity );
WC()->cart->remove_cart_item( $cart_item_key );
```

## Product Types

WooCommerce comes with 4 core product types:

| Type | Usage | Has Variations? |
|------|-------|-----------------|
| Simple | Single product, one price | No |
| Variable | Product with options (size, color) | Yes |
| Grouped | Collection of simple products | No |
| External/Affiliate | Link to another site | No |

### Variable Products Structure

```
Variable Product (parent)
├── Attribute: Color (Red, Blue, Green)
├── Attribute: Size (S, M, L)
└── Variations (children)
    ├── Variation 1: Red + S, $20
    ├── Variation 2: Red + M, $22
    ├── Variation 3: Blue + S, $20
    └── ...
```

Each variation is a separate post of type `product_variation` with parent = variable product ID.

## Session and Cart Storage

WooCommerce cart is stored differently for logged-in and guest users:

| User | Storage |
|------|---------|
| Logged-in | `wp_usermeta` (user's meta) |
| Guest | `wp_woocommerce_sessions` table |

**Session ID for guests:** Based on cookie `wp_woocommerce_session_*`

**Important:** Cart data is temporary. When the session expires, the cart is lost. This is by design.

## Database Tables

WooCommerce adds these tables:

| Table | Contents |
|-------|----------|
| `wp_woocommerce_sessions` | Guest cart/session data |
| `wp_woocommerce_api_keys` | REST API keys |
| `wp_woocommerce_attribute_taxonomies` | Custom product attributes |
| `wp_woocommerce_downloadable_product_permissions` | Download permissions |
| `wp_woocommerce_order_items` | Order line items |
| `wp_woocommerce_order_itemmeta` | Order item metadata |
| `wp_woocommerce_tax_rates` | Tax rates |
| `wp_woocommerce_tax_rate_locations` | Tax rate locations |
| `wp_wc_*` | HPOS tables (if enabled) |

## Caching Considerations

WooCommerce has its own caching layer:

```php
// Product data is cached
$product = wc_get_product( 123 ); // First call - DB query
$product = wc_get_product( 123 ); // Second call - from cache

// Invalidate when needed
clean_post_cache( $product_id );
wc_delete_product_transients( $product_id );
```

**Object Cache Compatibility:**
WooCommerce works well with Redis/Memcached, but some transients are important for performance. Don't disable all transients.

## Debugging Tips

### Logging

```php
// WooCommerce has a built-in logger
$logger = wc_get_logger();
$logger->debug( 'Debug message', array( 'source' => 'my-plugin' ) );
$logger->error( 'Error message', array( 'source' => 'my-plugin' ) );

// Logs are in: WooCommerce > Status > Logs
```

### Debug Mode

In `wp-config.php`:
```php
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );

// WooCommerce specific
define( 'WC_LOG_HANDLER', 'WC_Log_Handler_File' );
```

### Query Monitor

Query Monitor plugin shows:
- WooCommerce hooks and when they fire
- Database queries from WooCommerce
- Template files being used

## Template System

WooCommerce uses template hierarchy:

```
1. theme/woocommerce/[template-file].php
2. theme/[template-file].php
3. woocommerce/templates/[template-file].php (plugin default)
```

**Example:** To override single product template:
```
Copy: plugins/woocommerce/templates/single-product.php
To: theme/woocommerce/single-product.php
```

**Best Practice:** Only copy files you modify. On WooCommerce update, check for changes in original templates.

## Further Reading

- [WooCommerce Hooks](./02-woocommerce-hooks.md) - Practical hooks for customization
- [WooCommerce Performance](./03-woocommerce-performance.md) - Store optimizations
- [WordPress Database Operations](../01-wordpress-plugin-architecture/03-database-operations.md) - Database basics
- [Official WooCommerce Developer Docs](https://developer.woocommerce.com/)
