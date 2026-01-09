# WooCommerce Performance

WooCommerce stores have specific performance challenges that standard WordPress optimizations don't address. Understanding why stores are slower leads to better solutions.

## Why WooCommerce is Slower

| Reason | What Happens | Impact |
|--------|--------------|--------|
| More database queries | Cart, session, prices - every page load | 100-200+ queries vs 20-30 for blogs |
| Complex product queries | Variable products, attributes, stock checks | JOINs across multiple tables |
| Real-time calculations | Shipping, taxes, discounts | Cannot cache, must compute |
| No page caching | Cart, checkout are dynamic | Full PHP execution every request |
| Heavy admin | Product lists, order management | Slow backend frustrates staff |

### The Query Reality

**A typical blog page:** 20-30 database queries
- Posts, meta, terms, options

**A typical WooCommerce shop page:** 100-200+ database queries
- Everything above PLUS:
- Product meta (price, stock, attributes)
- Variable product data (each variation)
- Session data (cart contents)
- Customer data (if logged in)
- Shipping zone matching
- Tax calculations

**A cart/checkout page:** 200-400+ queries
- All product data for cart items
- Stock verification
- Coupon validation
- Shipping rate calculations
- Payment gateway initialization
- Session read/write

**Why this matters:** You can't just "install a caching plugin" and expect good performance. WooCommerce requires strategic optimization at multiple levels.

## System Cron for WooCommerce

WooCommerce relies heavily on scheduled tasks. The default HTTP-triggered cron is problematic:

```php
// In wp-config.php - disable HTTP cron
define( 'DISABLE_WP_CRON', true );
```

**Set up system cron (every minute):**
```bash
* * * * * nice -n 15 wp cron event run --due-now --path=/PATH/TO/WP/ --quiet
```

**Why this matters for WooCommerce:**
- Prevents socket exhaustion on high-traffic stores
- Background tasks don't delay customer requests
- More reliable scheduled sale prices and stock updates

### Action Scheduler via CLI

WooCommerce's Action Scheduler handles background jobs. Run it via CLI instead of HTTP:

```bash
# Install the plugin to disable default queue runner
# https://github.com/developer developer/action-scheduler-disable-default-runner

# Add to system cron
* * * * * nice -n 15 wp action-scheduler run --path=/PATH/TO/WP/ --quiet
```

## Database Optimization

### Convert to InnoDB

Old installations may have MyISAM tables. InnoDB provides row-level locking (critical for concurrent checkouts):

```sql
-- Check for MyISAM tables
SELECT TABLE_NAME, ENGINE
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'your_database'
AND ENGINE = 'MyISAM';

-- Convert each table
ALTER TABLE wp_posts ENGINE=InnoDB;
```

Use [Servebolt Optimizer](https://wordpress.org/plugins/servebolt-optimizer/) for automated conversion.

### Product Lookup Tables

WooCommerce 3.6+ introduced lookup tables to speed up product queries:

```
Traditional query for "products under $50":
1. Query wp_posts for products
2. JOIN wp_postmeta for _price
3. Filter where meta_value < 50
4. Many rows, slow index usage

With lookup tables:
1. Query wp_wc_product_meta_lookup
2. WHERE min_price < 50
3. Direct column access, fast index
```

**Enable lookup tables:**
```
WooCommerce > Status > Tools > Regenerate product lookup tables
```

**Why it helps:** Instead of storing prices in the generic `wp_postmeta` table (which holds ALL metadata), WooCommerce copies critical product data to dedicated tables with proper indexes. The `wp_wc_product_meta_lookup` table has columns for `min_price`, `max_price`, `onsale`, `stock_status` - making filtering fast.

**When to regenerate:**
- After bulk price changes
- After importing products
- If product counts seem wrong in filters
- After WooCommerce major updates

### HPOS for Orders

High-Performance Order Storage moves orders from `wp_posts` to dedicated tables:

```
WooCommerce > Settings > Advanced > Features
☑ Custom order tables (enable HPOS)
```

### Why HPOS Dramatically Improves Performance

**The problem with post-based orders:**

Imagine a store with 50,000 orders. Each order has ~50 meta fields (billing address, shipping, items, payment details). That's 2.5 million rows in `wp_postmeta`:

```sql
-- This table serves EVERYTHING
wp_postmeta contains:
- Blog post meta
- Page meta
- Product meta
- Order meta  <- 2.5 million rows
- User meta
- Every plugin's data
```

When WordPress loads, it might autoload options. When you query orders, MySQL scans this massive shared table. Even with indexes, performance degrades.

**HPOS solution:**

```sql
-- Dedicated order tables
wp_wc_orders: Direct columns for status, total, customer
wp_wc_orders_meta: Only order-specific meta
wp_wc_order_addresses: Structured address data
```

**Measured improvements:**
- Order list admin page: 5-10x faster
- Order search: 3-5x faster
- Reports generation: Significantly faster
- Reduced database lock contention

### Autoload Cleanup

WordPress loads all `autoload='yes'` options into memory on EVERY page load. WooCommerce adds many options, and plugins add more:

```sql
-- Check your autoload situation
SELECT SUM(LENGTH(option_value)) / 1024 / 1024 as MB
FROM wp_options
WHERE autoload = 'yes';
-- If over 1MB, you have a problem. Over 2MB is critical.

-- Find the culprits
SELECT option_name, LENGTH(option_value) / 1024 as KB
FROM wp_options
WHERE autoload = 'yes'
ORDER BY LENGTH(option_value) DESC
LIMIT 20;
```

**Common problems:**
| Option Pattern | Cause | Solution |
|----------------|-------|----------|
| `_transient_*` | Expired transients not cleaned | Delete expired, check cron |
| `wc_session_*` | Shouldn't be autoloaded | Bug in older WC versions |
| Plugin analytics | Some plugins store huge data | Contact plugin author |
| Theme options | Themes with many settings | Consider theme switch |

**Safe cleanup:**
```sql
-- Delete expired transients (safe)
DELETE FROM wp_options
WHERE option_name LIKE '_transient_timeout_%'
AND option_value < UNIX_TIMESTAMP();

DELETE FROM wp_options
WHERE option_name LIKE '_transient_%'
AND option_name NOT LIKE '_transient_timeout_%'
AND option_name NOT IN (
    SELECT REPLACE(option_name, '_transient_timeout_', '_transient_')
    FROM wp_options
    WHERE option_name LIKE '_transient_timeout_%'
);
```

### Index Optimization

MySQL indexes make queries fast. WooCommerce's queries have specific patterns that benefit from custom indexes:

```sql
-- Stock status queries happen constantly (is product in stock?)
ALTER TABLE wp_postmeta
ADD INDEX stock_lookup (meta_key(20), meta_value(10));

-- SKU lookups (find product by SKU)
ALTER TABLE wp_postmeta
ADD INDEX sku_lookup (meta_key(20), meta_value(50));

-- Price range queries (filtering by price)
-- Note: Better handled by lookup tables if enabled
```

**Caution:** Adding indexes speeds up reads but slows writes slightly. On high-traffic stores, test in staging first.

## Caching Strategy

### What Can vs Cannot Be Cached

Understanding cacheability is crucial for WooCommerce:

| Page Type | Full Page Cache? | Why |
|-----------|------------------|-----|
| Homepage (no cart widget) | Yes | Static content |
| Category pages | Careful | Sorting, filters may vary |
| Product pages | Careful | Stock, prices change |
| Cart | **No** | User-specific |
| Checkout | **No** | User-specific, security |
| My Account | **No** | User-specific |

### Why Cart/Checkout Cannot Be Cached

When you cache a page, you serve the same HTML to everyone. The cart page shows:
- Your specific cart items
- Your calculated shipping
- Your available coupons
- Your customer discounts

Serving a cached cart would show someone else's cart. This is both wrong AND a security issue (exposing customer data).

**Even "smart" caching fails here:** Fragment caching (caching parts of a page) still requires PHP to run, just less of it. The performance gain is smaller than expected because cart calculations are the slow part.

### Page Cache Exclusions

In your caching plugin (WP Rocket, W3TC, etc.), exclude these URLs:

```
/cart/*
/checkout/*
/my-account/*
/wishlist/*

# Cookie-based bypass
woocommerce_cart_hash
woocommerce_items_in_cart
wp_woocommerce_session_*
```

**Why cookie-based bypass matters:** When a customer adds something to cart, they get a cookie. The caching plugin should see this cookie and bypass cache for that user. Without this:
1. User adds to cart
2. User visits homepage (cached, shows cart=0)
3. User confused - "where's my cart item?"

### Object Cache (Redis/Memcached)

Object cache stores database query results in memory. For WooCommerce, this is critical:

```php
// In wp-config.php
define( 'WP_REDIS_HOST', '127.0.0.1' );
define( 'WP_REDIS_PORT', 6379 );
define( 'WP_REDIS_DATABASE', 0 );

// Important for WooCommerce
define( 'WP_REDIS_SELECTIVE_FLUSH', true );
```

**How object cache helps WooCommerce:**

Without object cache:
```
User visits product page
→ Query product data (DB)
→ Query price meta (DB)
→ Query stock meta (DB)
→ Query categories (DB)
→ ... 50+ queries to database
```

With object cache:
```
First user visits product page
→ Query product data (DB) → store in Redis
→ Query price meta (DB) → store in Redis
→ ...

Second user visits same product
→ Get product data (Redis, microseconds)
→ Get price meta (Redis, microseconds)
→ ... No database queries!
```

**Impact is greatest on:**
- Category pages (same products queried repeatedly)
- Admin pages (staff viewing same data)
- Logged-in users (cannot use page cache)

### Cart Fragments: The Hidden Performance Killer

Cart fragments is WooCommerce's AJAX system for updating the mini-cart widget:

```
What it does:
1. User loads any page
2. JavaScript fires AJAX request to get current cart HTML
3. Updates mini-cart widget in header
4. Happens on EVERY page load

The problem:
- Extra HTTP request per page
- Runs PHP to render cart
- Cannot be cached
- Blocks page "complete" event
```

**Option 1: Disable completely** (if you don't use mini-cart widget)
```php
add_action( 'wp_enqueue_scripts', function() {
    wp_dequeue_script( 'wc-cart-fragments' );
}, 11 );
```

**Option 2: Conditional loading** (only where needed)
```php
add_action( 'wp_enqueue_scripts', function() {
    // Only load on pages where cart widget matters
    if ( ! is_cart() && ! is_checkout() && ! is_woocommerce() ) {
        wp_dequeue_script( 'wc-cart-fragments' );
    }
}, 11 );
```

**Option 3: Lazy load** (load only on user interaction)
```javascript
// Custom implementation: Load fragments when user hovers cart icon
$('.cart-icon').one('mouseenter', function() {
    $.ajax({
        url: wc_cart_fragments_params.ajax_url,
        type: 'POST',
        data: { action: 'get_refreshed_fragments' }
    });
});
```

## Query Optimization

### Find Slow Queries

Query Monitor plugin reveals WooCommerce database bottlenecks:

1. Install Query Monitor
2. Visit slow pages
3. Check "Queries by Component" → WooCommerce
4. Sort by time

**Common culprits:**
- `wc_get_products()` without limits
- Variable product loading all variations
- Order queries without date limits
- Stock status checks on many products

### The Limit Problem

```php
// DANGEROUS: Returns ALL products (could be thousands)
$products = wc_get_products( array(
    'category' => 'clothing',
) );

// SAFE: Returns manageable batch
$products = wc_get_products( array(
    'category' => 'clothing',
    'limit'    => 12,
    'page'     => 1,
) );
```

**Why this matters:** Without a limit, WooCommerce queries every product. Even if you only use 10, you've loaded 5,000 into memory, run their constructors, and populated caches.

### N+1 Query Problem

The N+1 problem is when you run 1 query to get a list, then N queries to get details:

```php
// BAD: N+1 problem - 1 query for order, N queries for products
$order = wc_get_order( $order_id );
foreach ( $order->get_items() as $item ) {
    $product = $item->get_product(); // Query for each item!
    echo $product->get_name();
}
// If order has 20 items = 21 database queries

// BETTER: Prefetch products in one query
$order = wc_get_order( $order_id );
$product_ids = array();
foreach ( $order->get_items() as $item ) {
    $product_ids[] = $item->get_product_id();
}

// Prime the cache with one query
_prime_post_caches( $product_ids );
// or: wc_get_products(['include' => $product_ids]);

// Now the loop doesn't hit database
foreach ( $order->get_items() as $item ) {
    $product = $item->get_product(); // From cache
    echo $product->get_name();
}
// If order has 20 items = 2 database queries total
```

### Variable Products Performance

Variable products are slow because each variation is a separate post:

```php
// SLOW: Loads ALL variations into memory
$product = wc_get_product( $variable_product_id );
$variations = $product->get_available_variations();
// If 100 variations = 100 post loads + all their meta

// FASTER: Get only what you need
$variation_ids = $product->get_children();
// Then load specific variations as needed
```

**Why variations are slow:**
- Each variation = separate database row
- Each has its own meta (price, stock, image, attributes)
- `get_available_variations()` loads ALL of them
- Then formats each for JavaScript

**WooCommerce's solution:** On product pages, variation data is loaded as JSON data attribute, not PHP. The JavaScript handles variation switching client-side. Don't reload variations in PHP unless necessary.

## Frontend Optimization

### HTML Validation

Invalid HTML parses and renders slower than valid HTML:

1. Check pages at [validator.w3.org](https://validator.w3.org/)
2. Fix structural errors
3. Check browser console for JavaScript errors (they consume processing time)

### Remove Unused CSS

WooCommerce loads CSS you may not need:

```php
// Remove specific stylesheets
add_action( 'wp_enqueue_scripts', function() {
    // Remove block styles if not using blocks
    wp_dequeue_style( 'wc-blocks-style' );

    // Remove on non-WooCommerce pages
    if ( ! is_woocommerce() && ! is_cart() && ! is_checkout() ) {
        wp_dequeue_style( 'woocommerce-general' );
    }
}, 20 );
```

**Find unused CSS:** Use [purifycss.online](https://purifycss.online/) to identify CSS bloat percentages.

### Critical CSS

WooCommerce adds substantial CSS. On a typical site:
- woocommerce.css: 50-100KB
- woocommerce-layout.css: 10-20KB
- woocommerce-smallscreen.css: 5-10KB
- Theme's WooCommerce styles: Variable

**The problem:** All this CSS blocks rendering. Browser waits for CSS before showing content.

**Solution: Critical CSS**
1. Extract CSS needed for above-the-fold content
2. Inline it in `<head>`
3. Load full CSS asynchronously

Tools:
- [Critical by Addy Osmani](https://github.com/addyosmani/critical)
- Perfmatters plugin
- WP Rocket's "Load CSS Asynchronously"

### Google Fonts Performance

Loading fonts from fonts.google.com adds ~1 second (render-blocking):

**Solution: Host fonts locally**

1. Download fonts from [google-webfonts-helper.herokuapp.com](https://google-webfonts-helper.herokuapp.com/)
2. Add to theme's `/fonts/` directory
3. Use `@font-face` in your CSS:

```css
@font-face {
    font-family: 'Open Sans';
    src: url('fonts/open-sans-v34-latin-regular.woff2') format('woff2');
    font-display: swap;
}
```

**Alternative:** Use Cloudflare/Accelerated Domains to proxy Google Fonts automatically.

### JavaScript Loading Strategies

| Method | Behavior | Use When |
|--------|----------|----------|
| In `<head>` | Blocks parsing and rendering | Never (legacy only) |
| End of `<body>` | Executes after HTML parsed | Better, but not ideal |
| `async` | Downloads parallel, executes immediately | Analytics, non-critical |
| `defer` | Downloads parallel, executes after parse | Most WooCommerce scripts |

```php
// Add defer to WooCommerce scripts
add_filter( 'script_loader_tag', function( $tag, $handle ) {
    $defer_scripts = array( 'woocommerce', 'wc-add-to-cart', 'wc-cart-fragments' );

    if ( in_array( $handle, $defer_scripts ) ) {
        return str_replace( ' src', ' defer src', $tag );
    }
    return $tag;
}, 10, 2 );
```

### Conditional Script Loading

WooCommerce loads several JavaScript files. Not all are needed everywhere:

```php
add_action( 'wp_enqueue_scripts', function() {
    // Don't load WooCommerce assets on non-WooCommerce pages
    if ( ! is_woocommerce() && ! is_cart() && ! is_checkout() && ! is_account_page() ) {
        // Styles
        wp_dequeue_style( 'woocommerce-general' );
        wp_dequeue_style( 'woocommerce-layout' );
        wp_dequeue_style( 'woocommerce-smallscreen' );
        wp_dequeue_style( 'wc-blocks-style' );

        // Scripts
        wp_dequeue_script( 'wc-cart-fragments' );
        wp_dequeue_script( 'woocommerce' );
        wp_dequeue_script( 'wc-add-to-cart' );
    }
}, 99 );
```

**Why priority 99?** WooCommerce enqueues its assets. Other plugins might enqueue theirs. By using high priority, you run after everyone else has enqueued, so you can dequeue effectively.

### Image Optimization

Product images are often the largest page weight. WooCommerce generates multiple sizes:

```php
// Control product image sizes
add_filter( 'woocommerce_get_image_size_single', function( $size ) {
    return array(
        'width'  => 600,  // Don't need 1200px for most layouts
        'height' => 600,
        'crop'   => 1,
    );
} );

add_filter( 'woocommerce_get_image_size_thumbnail', function( $size ) {
    return array(
        'width'  => 300,  // Thumbnails don't need to be huge
        'height' => 300,
        'crop'   => 1,
    );
} );

add_filter( 'woocommerce_get_image_size_gallery_thumbnail', function( $size ) {
    return array(
        'width'  => 100,
        'height' => 100,
        'crop'   => 1,
    );
} );
```

**After changing sizes:** Regenerate thumbnails (use WP-CLI or Regenerate Thumbnails plugin).

**Additional optimizations:**
- WebP conversion (ShortPixel, Imagify)
- Lazy loading (native or plugin)
- CDN for images (Cloudflare, BunnyCDN)

## Admin Performance

### Why WooCommerce Admin is Slow

The WooCommerce admin loads:
- Full product/order lists
- Analytics calculations
- Extension ads and notifications
- Block-based components (React)

**Common slowdowns:**
- Product list with 10,000+ products
- Order list with complex queries
- Analytics loading months of data
- Marketing hub loading external content

### Limit Items Per Page

```php
add_filter( 'edit_posts_per_page', function( $per_page, $post_type ) {
    if ( $post_type === 'shop_order' ) {
        return 20; // Default might be 20, but some installs have higher
    }
    if ( $post_type === 'product' ) {
        return 30; // Fewer products = faster page
    }
    return $per_page;
}, 10, 2 );
```

### Action Scheduler

WooCommerce uses Action Scheduler for background tasks (scheduled sales, data updates, etc.):

```
WooCommerce > Status > Scheduled Actions
```

**If pending actions pile up:**
```php
// Increase batch size (default 25)
add_filter( 'action_scheduler_queue_runner_batch_size', function() {
    return 50;
} );

// Increase concurrent batches (default 5)
add_filter( 'action_scheduler_queue_runner_concurrent_batches', function() {
    return 10;
} );
```

**When to worry:** Thousands of pending actions indicate either:
- Server cron not running properly
- Actions taking too long
- More actions created than can be processed

### Disable Unused Features

```php
// If you don't use WooCommerce Analytics
add_filter( 'woocommerce_analytics_enabled', '__return_false' );

// If you don't need the marketing hub
add_filter( 'woocommerce_admin_features', function( $features ) {
    return array_diff( $features, ['marketing'] );
} );

// Disable WooCommerce admin entirely (use classic admin)
add_filter( 'woocommerce_admin_disabled', '__return_true' );
```

## Hosting Considerations

### Minimum Requirements for WooCommerce

| Resource | Minimum | Recommended | Why |
|----------|---------|-------------|-----|
| PHP Memory | 256MB | 512MB+ | Variable products, cart calculations |
| PHP Workers | 4 | 8+ | Checkout can't wait, needs workers |
| MySQL | 5.7 | 8.0+ | Better JSON support, performance |
| Object Cache | Optional | Required | Essential for logged-in users |
| PHP Version | 7.4 | 8.1+ | Significant performance gains |

### PHP-FPM Tuning

```ini
; WooCommerce-appropriate PHP-FPM settings
pm = dynamic                ; Adapt to load
pm.max_children = 20        ; Based on RAM (each child ~50MB)
pm.start_servers = 5        ; Start with reasonable pool
pm.min_spare_servers = 3    ; Keep some ready
pm.max_spare_servers = 10   ; Don't waste RAM on idle workers
pm.max_requests = 500       ; Recycle workers to prevent memory leaks
```

**Calculation:** If server has 4GB RAM and 1GB for MySQL/OS, you have ~3GB for PHP. At 50MB per process, that's 60 workers max. But leave headroom: 20-30 is safer.

### MySQL Tuning

```ini
# MySQL tuning for WooCommerce
innodb_buffer_pool_size = 1G  ; 50-70% of RAM if dedicated DB server
query_cache_type = 0          ; Disable query cache (use object cache instead)
tmp_table_size = 64M          ; For complex JOINs
max_heap_table_size = 64M     ; Memory for temp tables
innodb_log_file_size = 256M   ; Larger logs = fewer flushes
```

**Why disable query cache?** MySQL query cache is invalidated whenever any row in a table changes. WooCommerce changes tables frequently (sessions, orders). The cache gets invalidated constantly, providing no benefit while consuming memory.

## Monitoring

### Key Metrics to Track

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Time to First Byte (TTFB) | < 200ms | Server response speed |
| Largest Contentful Paint (LCP) | < 2.5s | Perceived load time |
| Add to Cart response | < 500ms | Critical conversion action |
| Checkout load time | < 2s | Don't lose customers at checkout |
| Order processing | < 1s | Payment processing time |

### Monitoring Tools

| Tool | What It Measures | Best For |
|------|------------------|----------|
| Query Monitor | Database queries, hooks | Development, debugging |
| New Relic | Full application stack | Production monitoring |
| Blackfire | PHP profiling | Deep performance analysis |
| GTmetrix | Frontend performance | Core Web Vitals |
| UptimeRobot | Availability | Downtime alerts |

### Setting Up Alerts

Monitor these for problems:
- TTFB > 500ms (investigate immediately)
- Database connections > 80% max (scaling issue)
- PHP memory > 90% (increase limit or fix leak)
- Error rate > 1% (something broken)
- Cart abandonment spike (checkout problem?)

## Theme and Plugin Selection

### Theme Performance Impact

Theme choice dramatically affects WooCommerce performance:

**Avoid:**
- Multipurpose "Swiss army knife" themes with 100+ features
- Themes with built-in page builders loading on every page
- Themes loading 15+ JavaScript files

**Choose:**
- Lightweight themes built specifically for WooCommerce
- Themes with only features you actually use
- Themes from developers who document performance

**Testing themes:**
1. Test complete demo, not just homepage
2. Check product pages, category pages, cart
3. Test **uncached** with unique query strings: `?test=1`, `?test=2`
4. Use tools: Sitebulb, Screaming Frog, batchspeed.com

### Plugin Performance Audit

Test every plugin's impact individually:

```php
// Use WP Plugin Manager to disable plugins per-page
// Example: Disable review plugin on non-product pages
```

**Red flags in plugins:**
- License checks on every pageload
- XML-RPC connections to external servers
- Loading assets/code on wrong pages
- Heavy admin code affecting frontend

### Security Plugins Warning

Traditional security plugins (Wordfence, iThemes Security, Sucuri plugin) **hurt performance**:

- Run on every request (including cached)
- Work inside WordPress (too late to stop real threats)
- Consume PHP processing time

**Better approach:**
- Multi-factor authentication for wp-admin
- WAF/firewall at edge (Cloudflare, Accelerated Domains)
- Keep everything updated
- Remove unused plugins/themes

## Product Search Optimization

WooCommerce's built-in search struggles with filtered metadata queries on large catalogs.

### Algolia

Fast, hosted search with excellent relevance:

```bash
# Install via WebDevStudios plugin
wp plugin install wp-search-with-algolia --activate
```

**Best for:** Stores needing instant search, typo tolerance, faceted filtering.

### Elasticsearch

Self-hosted, highly customizable:

```bash
# Install 10up's plugin
wp plugin install elasticpress --activate
```

**Best for:** Stores needing full control, complex custom queries.

## Testing Methodology

### Test Uncached Performance

Cached performance is misleading. Test real server response:

```bash
# Each request bypasses cache with unique query string
curl -o /dev/null -s -w "%{time_total}\n" "https://store.com/product/?test=1"
curl -o /dev/null -s -w "%{time_total}\n" "https://store.com/product/?test=2"
curl -o /dev/null -s -w "%{time_total}\n" "https://store.com/product/?test=3"
```

### TTFB Benchmarks

| TTFB | Rating |
|------|--------|
| < 250ms | Good |
| < 500ms | OK |
| < 1000ms | Needs work |
| > 1000ms | Critical |

### Performance-First Development

Apply performance testing to ALL future changes:
- Theme switches
- Plugin installations/updates
- Development work
- Design modifications

Small slowdowns add up. Track cumulative impact.

## Common Misconceptions

**"Increase PHP memory limit for speed"**
- Memory limit affects capacity, not speed
- A 256MB limit runs the same speed as 512MB
- Only increase if hitting actual limits

**"Disable post revisions for performance"**
- With proper database indexes, revisions don't slow queries
- Zero performance benefit on well-configured databases

**"Cart Fragments always slows sites"**
- With proper caching configuration, impact is minimal
- Only disable if you truly don't use mini-cart widget

**"Redis dramatically speeds up frontend"**
- Redis helps backend/admin more than frontend
- Properly cached frontend rarely hits Redis
- Don't add complexity without measuring benefit

## Quick Wins Checklist

Before diving into complex optimization, check these:

- [ ] **Enable HPOS** for orders (5-10x faster order admin)
- [ ] **Disable cart fragments** on non-WooCommerce pages (fewer AJAX requests)
- [ ] **Install Redis/Memcached** object cache (dramatic improvement for logged-in users)
- [ ] **Configure page cache** with proper exclusions (cart/checkout/account)
- [ ] **Optimize product images** (WebP, proper sizes, lazy loading)
- [ ] **Check slow queries** with Query Monitor (find the bottleneck)
- [ ] **Disable unused features** (analytics, marketing hub if not used)
- [ ] **Regenerate lookup tables** (WooCommerce > Status > Tools)
- [ ] **Clean autoloaded options** (if over 1MB)
- [ ] **Update PHP version** (8.1 is 20-30% faster than 7.4)

## Further Reading

- [WooCommerce Fundamentals](./01-woocommerce-fundamentals.md) - Data storage architecture
- [Database Optimization](../04-performance/07-database-optimizations.md) - General DB tips
- [PHP-FPM Optimization](../04-performance/03-php-fpm-optimization.md) - Server tuning
- [Core Web Vitals](../04-performance/08-core-web-vitals-optimizations.md) - Frontend metrics
- [Servebolt WooCommerce Guide](https://servebolt.com/articles/how-to-speed-up-woocommerce/) - Comprehensive optimization article
