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

### Why This Architecture Matters

WooCommerce's decision to build on WordPress primitives has profound implications:

**The Good:**
- Standard WordPress functions like `get_posts()`, `WP_Query`, and `get_terms()` work with WooCommerce data
- WordPress plugins for SEO, caching, and security automatically apply to products
- Familiar patterns for WordPress developers - no new concepts to learn
- Built-in REST API support through WordPress

**The Trade-offs:**
- Post meta storage is flexible but slow at scale (addressed by HPOS for orders)
- Products share the `wp_posts` table with blog posts, pages, and everything else
- Complex queries require joining multiple tables
- The `wp_postmeta` table becomes enormous on large stores

**Practical Impact:** When you understand that a product is just a post with extra metadata, debugging becomes intuitive. Price not showing? Check `_price` meta. Product not appearing? Check `post_status`. Variable product broken? Look at child posts.

## Data Storage Model

### Products and Post Meta

Product data is split between two locations, each serving a specific purpose:

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

### Why This Split Exists

**The `wp_posts` table** stores data that WordPress core needs for standard operations:
- Search functionality uses `post_title` and `post_content`
- Permalinks are generated from `post_name`
- Publishing workflow uses `post_status`
- Archive pages rely on `post_date`

**The `wp_postmeta` table** stores everything WooCommerce-specific:
- Flexible key-value storage allows unlimited custom fields
- No schema changes needed when adding new product data
- Third-party plugins can add their own meta without conflicts

**The Performance Reality:** This flexibility comes at a cost. Each meta value is a separate row. A single product with 50 meta fields means 50 rows in `wp_postmeta`. Querying "all products under $50" requires joining tables and is inherently slower than a dedicated `products` table would be.

### Understanding Meta Key Prefixes

WooCommerce uses underscores strategically:

```php
// Single underscore = "hidden" from custom fields UI
_price          // Won't show in admin custom fields box
_sku            // Managed by WooCommerce, not manual entry

// No underscore = visible in custom fields
my_custom_field // Shows in admin UI for manual editing
```

**Why this matters:** When adding custom product data, prefix with underscore if you're managing it programmatically. Leave without underscore if store admins need to see/edit it in the standard WordPress custom fields box.

### HPOS: High-Performance Order Storage

From WooCommerce 8.2, orders can be stored in **custom tables** instead of post meta:

```
wp_wc_orders (core order data)
├── id, status, currency, total
├── customer_id, billing_email
└── date_created, date_modified

wp_wc_orders_meta (order meta)
├── order_id, meta_key, meta_value
└── (same pattern but separate table)

wp_wc_order_addresses (billing/shipping)
├── order_id, address_type
├── first_name, last_name, company
└── address_1, city, postcode, country

wp_wc_order_items (line items)
├── order_id, order_item_type
└── order_item_name
```

### Why HPOS Exists and Why It Matters

The post meta system works fine for hundreds of orders. But as stores scale:

**The Problem at Scale:**
- 10,000 orders × 50 meta fields = 500,000 rows in `wp_postmeta`
- This table is also used by pages, posts, products, and everything else
- Queries become slow because MySQL must scan more data
- Index efficiency degrades as the table grows

**HPOS Solution:**
- Orders get their own dedicated tables
- Common order data (status, totals) is in columns, not meta
- SQL queries can filter directly without JOINs
- The `wp_postmeta` table stays manageable

**Performance Impact:**
- 5-10x faster order queries with many orders
- Order list page in admin loads significantly faster
- Reports and analytics run without timing out
- Better scalability for high-volume stores

**Check if HPOS is active:**
```php
// Modern approach - check if orders use custom tables
$hpos_enabled = wc_get_container()
    ->get( \Automattic\WooCommerce\Internal\DataStores\Orders\CustomOrdersTableController::class )
    ->custom_orders_table_usage_is_enabled();

if ( $hpos_enabled ) {
    // Orders are in custom tables
    // NEVER use get_post() for orders
}
```

**Practical Tip:** Always use `wc_get_order()` instead of `get_post()` for orders. This function automatically works with both storage modes. Code using `get_post()` will break silently when HPOS is enabled - orders will appear as "not found" because they're no longer in `wp_posts`.

## Key Objects and Functions

WooCommerce wraps database complexity in object-oriented classes. Understanding these objects is essential for effective development.

### WC_Product - The Product Object

```php
// Get a product - this is the ONLY correct way
$product = wc_get_product( $product_id );

// Why wc_get_product() instead of new WC_Product()?
// - Handles product type detection automatically
// - Returns correct class (WC_Product_Simple, WC_Product_Variable, etc.)
// - Integrates with object cache
// - Returns false if product doesn't exist (safe to check)

// Core methods - what they actually return
$product->get_name();           // Post title
$product->get_price();          // Current effective price (after sales)
$product->get_regular_price();  // Base price before any discounts
$product->get_sale_price();     // Discounted price (empty if not on sale)
$product->get_sku();            // Stock Keeping Unit - your internal ID
$product->get_stock_quantity(); // Integer count (null if not managing stock)
$product->is_in_stock();        // Boolean - considers stock status AND quantity
$product->is_on_sale();         // Boolean - has active sale price
$product->get_type();           // 'simple', 'variable', 'grouped', 'external'
```

### Why get_price() vs get_regular_price()?

This trips up many developers:

- `get_regular_price()` - The base price you set. Never changes automatically.
- `get_sale_price()` - The discounted price, if any sale is active.
- `get_price()` - The **current** price customers will pay.

```php
// Example: Product is $100, on sale for $80
$product->get_regular_price(); // "100"
$product->get_sale_price();    // "80"
$product->get_price();         // "80" (active sale price)

// If sale ends
$product->get_price();         // "100" (back to regular)
```

**Use `get_price()` for display and calculations.** Use `get_regular_price()` only when you specifically need the "was" price.

### WC_Order - The Order Object

```php
// Get an order - ALWAYS use this function
$order = wc_get_order( $order_id );

// Why wc_get_order()?
// - Works with both post meta storage AND HPOS
// - Returns correct order type (WC_Order, WC_Order_Refund, etc.)
// - Handles caching appropriately
// - Returns false if order doesn't exist

// Core methods
$order->get_status();           // 'pending', 'processing', 'completed', etc.
$order->get_total();            // Final amount charged (string, formatted)
$order->get_billing_email();    // Customer email for communications
$order->get_items();            // Array of WC_Order_Item objects
$order->get_payment_method();   // Gateway ID like 'stripe', 'paypal'
$order->get_date_created();     // WC_DateTime object (not timestamp!)
```

### Understanding Order Statuses

Order status flow is critical for store operations:

```
Customer places order
        ↓
    [pending] ──────→ Payment fails → stays pending
        ↓
    Payment succeeds
        ↓
    [processing] ────→ Awaiting fulfillment
        ↓
    Order shipped
        ↓
    [completed] ─────→ Final state

Special statuses:
    [on-hold]     → Manual review required (fraud check, verification)
    [cancelled]   → Customer or admin cancelled
    [refunded]    → Full refund processed
    [failed]      → Payment definitively failed
```

### WC_Cart - The Shopping Cart

```php
// Cart is a singleton - there's only one cart per session
// Access it through WC() global function

WC()->cart->get_cart();         // Array of cart items
WC()->cart->get_cart_total();   // Formatted string with currency
WC()->cart->get_cart_contents_count(); // Total items (considers quantities)
WC()->cart->add_to_cart( $product_id, $quantity );
WC()->cart->remove_cart_item( $cart_item_key );
```

### Why Cart is Different

Unlike products and orders, the cart:

- **Is not stored in the database** (except as session data)
- **Only exists for the current user's session**
- **Is recalculated on every page load** (totals, shipping, taxes)
- **Uses cart item keys**, not IDs, to identify items

```php
// Cart item structure
$cart_item = [
    'key'          => 'abc123...', // Unique hash, not product ID
    'product_id'   => 42,
    'variation_id' => 0,           // If variable product
    'quantity'     => 2,
    'data'         => WC_Product,  // Full product object
    'line_total'   => 50.00,
    // ... plus any custom data you add
];
```

**Common Mistake:** Trying to use product ID to remove items. You need the cart item key:

```php
// WRONG - product ID doesn't work
WC()->cart->remove_cart_item( $product_id );

// RIGHT - use the cart item key
foreach ( WC()->cart->get_cart() as $cart_item_key => $cart_item ) {
    if ( $cart_item['product_id'] === $product_id ) {
        WC()->cart->remove_cart_item( $cart_item_key );
    }
}
```

## Product Types

WooCommerce comes with 4 core product types, each designed for specific use cases:

| Type | Usage | Has Variations? | Use When... |
|------|-------|-----------------|-------------|
| Simple | Single product, one price | No | T-shirt in one size, book, service |
| Variable | Product with options | Yes | T-shirt with size/color options |
| Grouped | Collection of products | No | Camera + lens + bag as "kit" |
| External/Affiliate | Link to another site | No | Amazon affiliate products |

### Variable Products: The Complex One

Variable products are the most powerful but also most confusing type:

```
Variable Product (parent) - ID: 100
├── Attribute: Color (Red, Blue, Green)
├── Attribute: Size (S, M, L)
└── Variations (children)
    ├── Variation 101: Red + S, SKU: SHIRT-R-S, $20
    ├── Variation 102: Red + M, SKU: SHIRT-R-M, $22
    ├── Variation 103: Blue + S, SKU: SHIRT-B-S, $20
    └── ... (one for each combination)
```

### How Variable Products Work Internally

Each variation is actually a **separate post** of type `product_variation`:

```sql
-- Parent product
wp_posts: ID=100, post_type='product', post_title='T-Shirt'

-- Variations (children)
wp_posts: ID=101, post_type='product_variation', post_parent=100
wp_posts: ID=102, post_type='product_variation', post_parent=100
```

**Why this matters:**
- Each variation has its own price, SKU, stock, and image
- Querying variations means querying posts
- Product with 50 variations = 51 database entries
- Performance degrades with many variations

**Attribute Storage:**
```php
// Variation 101 meta
_sku: 'SHIRT-R-S'
_price: '20'
attribute_pa_color: 'red'    // pa_ prefix = product attribute
attribute_pa_size: 's'
```

## Session and Cart Storage

Understanding where cart data lives explains many confusing behaviors:

| User Type | Storage Location | Persistence |
|-----------|------------------|-------------|
| Logged-in | `wp_usermeta` table | Permanent (until cleared) |
| Guest | `wp_woocommerce_sessions` table | Until session expires |

### How Guest Sessions Work

1. First visit: WooCommerce generates a unique session ID
2. Stores it in cookie: `wp_woocommerce_session_[hash]`
3. Cart data saved to `wp_woocommerce_sessions` table
4. Session expires after X days (default: 48 hours with items, 2 hours empty)

**Why Carts Disappear:**
- Session expired
- User cleared cookies
- Different browser/device
- Cache plugin served stale page

### The Session Table Problem

```sql
-- This table can grow HUGE on busy sites
SELECT COUNT(*) FROM wp_woocommerce_sessions;
-- Thousands of abandoned sessions

-- Cleanup (WooCommerce does this via Action Scheduler)
DELETE FROM wp_woocommerce_sessions
WHERE session_expiry < UNIX_TIMESTAMP();
```

**If sessions aren't being cleaned:** Check that Action Scheduler is running (`WooCommerce > Status > Scheduled Actions`).

## Database Tables

WooCommerce adds these tables to WordPress:

| Table | Purpose | Notes |
|-------|---------|-------|
| `wp_woocommerce_sessions` | Guest cart/session data | Can grow large, auto-cleaned |
| `wp_woocommerce_api_keys` | REST API authentication keys | For external integrations |
| `wp_woocommerce_attribute_taxonomies` | Custom product attributes | Color, Size, Material, etc. |
| `wp_woocommerce_downloadable_product_permissions` | Digital download access | Tracks who can download what |
| `wp_woocommerce_order_items` | Order line items, shipping, fees | Separate from order meta |
| `wp_woocommerce_order_itemmeta` | Metadata for order items | Product options, custom data |
| `wp_woocommerce_tax_rates` | Tax rate definitions | By country/state/postcode |
| `wp_woocommerce_tax_rate_locations` | Tax rate location rules | Detailed location matching |
| `wp_wc_*` | HPOS tables (if enabled) | Modern order storage |

## Caching Considerations

WooCommerce has its own caching layer that works alongside WordPress:

```php
// Product data is cached in memory during request
$product = wc_get_product( 123 ); // First call - database query
$product = wc_get_product( 123 ); // Second call - from cache (no query)

// Invalidate cache when you modify products directly
clean_post_cache( $product_id );           // Clear WordPress cache
wc_delete_product_transients( $product_id ); // Clear WooCommerce transients
```

### Why Caching is Complicated for WooCommerce

**What CAN be cached:**
- Product pages (carefully - stock status, prices change)
- Category/archive pages (with variation awareness)
- Static pages without WooCommerce elements

**What CANNOT be cached:**
- Cart page (user-specific)
- Checkout page (user-specific, security sensitive)
- My Account pages (user-specific)
- Any page with cart widget showing count

**Object Cache (Redis/Memcached):**
WooCommerce benefits enormously from object cache because it makes many repeated database queries. The first product query hits the database; subsequent queries hit Redis. This is especially impactful for:
- Category pages listing many products
- Cart calculations
- Admin product lists

## Debugging Tips

### WooCommerce Logger

```php
// WooCommerce has a built-in logger - USE IT
$logger = wc_get_logger();

// Available levels (in order of severity)
$logger->debug( 'Detailed debugging info', array( 'source' => 'my-plugin' ) );
$logger->info( 'General information', array( 'source' => 'my-plugin' ) );
$logger->notice( 'Normal but significant events', array( 'source' => 'my-plugin' ) );
$logger->warning( 'Something might be wrong', array( 'source' => 'my-plugin' ) );
$logger->error( 'Something IS wrong', array( 'source' => 'my-plugin' ) );
$logger->critical( 'System is unusable', array( 'source' => 'my-plugin' ) );

// View logs at: WooCommerce > Status > Logs
// Files stored in: wp-content/uploads/wc-logs/
```

**Why use WooCommerce logger instead of `error_log()`?**
- Logs are viewable in WooCommerce admin (no server access needed)
- Organized by source (your plugin name)
- Automatic log rotation
- Can be configured per environment

### Debug Mode

In `wp-config.php`:
```php
// Standard WordPress debugging
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', false ); // Don't show on frontend

// WooCommerce specific - file-based logging
define( 'WC_LOG_HANDLER', 'WC_Log_Handler_File' );
```

### Query Monitor Plugin

Query Monitor is invaluable for WooCommerce development:

- **Hooks panel:** Shows all WooCommerce hooks and when they fire
- **Queries panel:** Database queries from WooCommerce (often the bottleneck)
- **Template panel:** Which WooCommerce template files are being used
- **Conditionals:** `is_shop()`, `is_product()`, etc. - which are true

## Template System

WooCommerce uses a template hierarchy similar to WordPress themes:

```
1. theme/woocommerce/[template-file].php
2. theme/[template-file].php
3. woocommerce/templates/[template-file].php (plugin default)
```

### How Template Overrides Work

To customize any WooCommerce template:

```
1. Find the template in: plugins/woocommerce/templates/
2. Copy it to: theme/woocommerce/[same-path]
3. Modify your copy
```

**Example:** Override the single product template:
```
Source: plugins/woocommerce/templates/single-product.php
Copy to: theme/woocommerce/single-product.php
```

### Why Not Just Copy Everything?

**Maintenance nightmare:** When WooCommerce updates, templates change. If you've copied 50 templates, you need to check all 50 for changes and merge your customizations.

**Best Practice:**
- Only copy files you actually modify
- Use hooks instead of template overrides when possible
- After WooCommerce updates, check `WooCommerce > Status > Templates` for outdated overrides
- Keep a changelog of what you changed and why

### Template vs. Hooks: When to Use Which

| Use Templates When... | Use Hooks When... |
|-----------------------|-------------------|
| Completely restructuring layout | Adding/removing elements |
| Complex HTML changes | Changing text/values |
| Need full control | Small modifications |
| One-off customization | Reusable across themes |

## Further Reading

- [WooCommerce Hooks](./02-woocommerce-hooks.md) - Practical hooks for customization
- [WooCommerce Performance](./03-woocommerce-performance.md) - Store optimizations
- [WordPress Database Operations](../08-plugin-development/03-database-operations.md) - Database basics
- [Official WooCommerce Developer Docs](https://developer.woocommerce.com/)
