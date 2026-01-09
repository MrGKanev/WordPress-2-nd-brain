# WooCommerce Performance

WooCommerce stores have specific performance challenges. Standard WordPress optimizations aren't enough.

## Why WooCommerce is Slower

| Reason | Impact |
|--------|--------|
| More database queries | Cart, session, prices - every page load |
| Complex product queries | Variable products, attributes, stock checks |
| Real-time calculations | Shipping, taxes, discounts |
| No page caching | Cart, checkout are dynamic |
| Heavy admin | WooCommerce admin is resource-intensive |

**Reality:** A typical WooCommerce page load makes 100-200+ database queries. A WordPress blog makes 20-30.

## Database Optimization

### Product Lookup Tables

WooCommerce 3.6+ has lookup tables for faster queries:

```php
// Enable lookup tables (if not already)
// WooCommerce > Status > Tools > Regenerate product lookup tables
```

These tables denormalize product data for fast searches.

### HPOS for Orders

High-Performance Order Storage significantly improves order queries:

```
WooCommerce > Settings > Advanced > Features
☑ Custom order tables (enable HPOS)
```

**Impact:** 5-10x faster order lists with 10,000+ orders.

### Autoload Cleanup

WooCommerce adds many autoloaded options:

```sql
-- Check how much autoloaded data you have
SELECT SUM(LENGTH(option_value)) as total_bytes
FROM wp_options
WHERE autoload = 'yes';
-- If over 1MB, you have a problem

-- Find the largest autoloaded options
SELECT option_name, LENGTH(option_value) as size
FROM wp_options
WHERE autoload = 'yes'
ORDER BY size DESC
LIMIT 20;
```

**Common culprits:**
- `_transient_*` - expired transients
- `wc_session_*` - old sessions
- Plugin settings with lots of data

### Index Optimization

Add indexes for common WooCommerce queries:

```sql
-- Stock queries
ALTER TABLE wp_postmeta ADD INDEX stock_lookup (meta_key, meta_value(10));

-- SKU lookups
ALTER TABLE wp_postmeta ADD INDEX sku_lookup (meta_key(20), meta_value(50));
```

## Caching Strategy

### What Can Be Cached

| Page | Full Page Cache | Fragment Cache |
|------|-----------------|----------------|
| Homepage | Yes (if no cart widget) | Yes |
| Category pages | Caution (sorting/filters) | Yes |
| Product pages | Caution (add to cart, stock) | Yes |
| Cart | No | Partial |
| Checkout | No | No |
| My Account | No | No |

### Page Cache Exclusions

In your caching plugin, exclude:

```
/cart/*
/checkout/*
/my-account/*
/wishlist/*

# Cookies to bypass cache
woocommerce_cart_hash
woocommerce_items_in_cart
wp_woocommerce_session_*
```

### Object Cache

Redis/Memcached is critical for WooCommerce:

```php
// In wp-config.php
define( 'WP_REDIS_HOST', '127.0.0.1' );
define( 'WP_REDIS_PORT', 6379 );
define( 'WP_REDIS_DATABASE', 0 );

// Selective group for WooCommerce
define( 'WP_REDIS_SELECTIVE_FLUSH', true );
```

**Important:** Object cache helps most with admin and logged-in users.

### Cart Fragments Ajax

Cart fragments is the most common performance problem:

```php
// What it does: Updates cart widget on every page load
// Problem: AJAX request on every page

// Option 1: Disable completely (if you don't have cart widget in header)
add_action( 'wp_enqueue_scripts', function() {
    wp_dequeue_script( 'wc-cart-fragments' );
}, 11 );

// Option 2: Lazy load - load only when needed
add_action( 'wp_enqueue_scripts', function() {
    if ( ! is_cart() && ! is_checkout() ) {
        wp_dequeue_script( 'wc-cart-fragments' );
    }
}, 11 );
```

## Query Optimization

### Problematic Queries

Find slow queries with Query Monitor:

```php
// Typical problem: get_posts without limit
$products = wc_get_products( array(
    'category' => 'clothing',
) ); // Returns ALL products!

// Correct
$products = wc_get_products( array(
    'category' => 'clothing',
    'limit'    => 12,
    'page'     => 1,
) );
```

### Avoid N+1 Queries

```php
// Wrong: N+1 problem
foreach ( $order->get_items() as $item ) {
    $product = $item->get_product();
    echo $product->get_name();
}

// Better: Prefetch products
$product_ids = array();
foreach ( $order->get_items() as $item ) {
    $product_ids[] = $item->get_product_id();
}
// Cache warmup
_prime_post_caches( $product_ids );

// Now the loop is fast
foreach ( $order->get_items() as $item ) {
    $product = $item->get_product();
    echo $product->get_name();
}
```

### Variable Products

Variable products are slow because each variation is a separate post:

```php
// Problem: Loading all variations
$product = wc_get_product( $id );
$variations = $product->get_available_variations(); // Slow!

// Better for frontend: Use variation data attribute
// WooCommerce does this automatically on product page
```

## Frontend Optimization

### Critical CSS

WooCommerce CSS is large. Load critical CSS inline:

```php
// Identify critical CSS for above-the-fold content
// Tools: Critical by Addy Osmani, or Perfmatters plugin
```

### JavaScript Loading

```php
// Don't load WooCommerce scripts on all pages
add_action( 'wp_enqueue_scripts', function() {
    // Remove on non-WooCommerce pages
    if ( ! is_woocommerce() && ! is_cart() && ! is_checkout() ) {
        wp_dequeue_style( 'woocommerce-general' );
        wp_dequeue_style( 'woocommerce-layout' );
        wp_dequeue_script( 'wc-cart-fragments' );
    }
}, 99 );
```

### Image Optimization

```php
// Optimal product image sizes
add_filter( 'woocommerce_get_image_size_single', function( $size ) {
    return array(
        'width'  => 600, // No more than needed
        'height' => 600,
        'crop'   => 1,
    );
} );

// Thumbnail size
add_filter( 'woocommerce_get_image_size_thumbnail', function( $size ) {
    return array(
        'width'  => 300,
        'height' => 300,
        'crop'   => 1,
    );
} );
```

## Admin Performance

### Slow Admin Panels

WooCommerce admin can be very slow:

```php
// Limit items per page in admin
add_filter( 'edit_posts_per_page', function( $per_page, $post_type ) {
    if ( $post_type === 'shop_order' ) {
        return 20; // Instead of default
    }
    if ( $post_type === 'product' ) {
        return 30;
    }
    return $per_page;
}, 10, 2 );
```

### Action Scheduler

WooCommerce uses Action Scheduler for background tasks:

```php
// Check pending actions
// WooCommerce > Status > Scheduled Actions

// If many pending, increase processing
add_filter( 'action_scheduler_queue_runner_batch_size', function() {
    return 50; // Default is 25
} );
```

### Analytics Disable

If you don't use WooCommerce Analytics:

```php
// Disable analytics tracking
add_filter( 'woocommerce_analytics_enabled', '__return_false' );

// Or only for specific reports
add_filter( 'woocommerce_admin_disabled', '__return_true' );
```

## Hosting Considerations

### Minimum Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| PHP Memory | 256MB | 512MB+ |
| PHP Workers | 4 | 8+ |
| MySQL | 5.7 | 8.0+ |
| Object Cache | Optional | Required |

### PHP-FPM Tuning

```ini
; For WooCommerce site
pm = dynamic
pm.max_children = 20
pm.start_servers = 5
pm.min_spare_servers = 3
pm.max_spare_servers = 10
pm.max_requests = 500
```

### Database Server

```ini
# MySQL tuning for WooCommerce
innodb_buffer_pool_size = 1G  ; 70% of RAM if dedicated
query_cache_type = 0          ; Disable, use object cache
tmp_table_size = 64M
max_heap_table_size = 64M
```

## Monitoring

### Key Metrics

Track these metrics:

```
- Time to First Byte (TTFB) < 200ms
- Largest Contentful Paint (LCP) < 2.5s
- Add to Cart response time < 500ms
- Checkout load time < 2s
- Order processing time < 1s
```

### Tools

| Tool | What It Measures |
|------|------------------|
| Query Monitor | Database queries, hooks |
| New Relic | Application performance |
| Blackfire | PHP profiling |
| GTmetrix/WebPageTest | Frontend performance |

## Quick Wins Checklist

- [ ] Enable HPOS for orders
- [ ] Disable cart fragments on non-WooCommerce pages
- [ ] Install Redis/Memcached object cache
- [ ] Configure page cache with proper exclusions
- [ ] Optimize product images
- [ ] Check for slow queries with Query Monitor
- [ ] Disable unused WooCommerce features
- [ ] Regenerate product lookup tables

## Further Reading

- [WooCommerce Fundamentals](./01-woocommerce-fundamentals.md) - Data storage architecture
- [Database Optimization](../03-wordpress-optimization/07-database-optimizations.md) - General DB tips
- [PHP-FPM Optimization](../03-wordpress-optimization/03-php-fpm-optimization.md) - Server tuning
- [Core Web Vitals](../03-wordpress-optimization/08-core-web-vitals-optimizations.md) - Frontend metrics
