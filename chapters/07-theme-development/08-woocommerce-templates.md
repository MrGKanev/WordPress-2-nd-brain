# WooCommerce Template Overrides

WooCommerce generates its frontend through a template system separate from WordPress's standard template hierarchy. Understanding this system is essential for customizing store appearance without breaking functionality or losing changes on plugin updates.

## How WooCommerce Templates Work

WooCommerce ships its own template files in `wp-content/plugins/woocommerce/templates/`. When rendering a shop page, WooCommerce looks for templates in this order:

```
1. Your theme:    wp-content/themes/your-theme/woocommerce/
2. WooCommerce:   wp-content/plugins/woocommerce/templates/
```

To customize a template, copy it to your theme's `woocommerce/` directory with the same file path. WooCommerce automatically uses your version instead.

### Template Directory Structure

```
your-theme/
└── woocommerce/
    ├── archive-product.php          # Shop page / category pages
    ├── single-product.php           # Individual product page
    ├── content-product.php          # Product in loop (archive)
    ├── content-single-product.php   # Single product content
    ├── cart/
    │   ├── cart.php                 # Cart page
    │   ├── cart-empty.php           # Empty cart
    │   └── mini-cart.php            # Widget/header cart
    ├── checkout/
    │   ├── form-checkout.php        # Checkout form
    │   ├── form-billing.php         # Billing fields
    │   ├── form-shipping.php        # Shipping fields
    │   ├── review-order.php         # Order review table
    │   └── thankyou.php             # Thank you page
    ├── myaccount/
    │   ├── my-account.php           # Account dashboard
    │   ├── orders.php               # Order history
    │   └── form-login.php           # Login/register
    ├── loop/
    │   ├── orderby.php              # Sorting dropdown
    │   ├── pagination.php           # Shop pagination
    │   └── result-count.php         # "Showing 1-12 of 36"
    ├── single-product/
    │   ├── title.php                # Product title
    │   ├── price.php                # Product price
    │   ├── rating.php               # Star rating
    │   ├── add-to-cart/             # Add to cart buttons
    │   ├── tabs/                    # Product tabs
    │   └── related.php              # Related products
    └── emails/                      # Transactional emails
        ├── email-header.php
        ├── email-footer.php
        └── customer-completed-order.php
```

## Safe Template Override Process

### Step 1: Find the Original Template

```bash
# Find WooCommerce template files
find wp-content/plugins/woocommerce/templates/ -name "*.php" | sort
```

Or check WooCommerce → Status → Templates for active overrides and outdated templates.

### Step 2: Copy to Your Theme

```bash
# Example: Override the single product page
mkdir -p wp-content/themes/your-theme/woocommerce/
cp wp-content/plugins/woocommerce/templates/content-single-product.php \
   wp-content/themes/your-theme/woocommerce/content-single-product.php
```

### Step 3: Modify Your Copy

Each WooCommerce template has a version header:

```php
/**
 * The template for displaying product content in the single-product.php template
 *
 * @version 3.6.0
 */
```

Keep this header. WooCommerce uses it to warn you when your override is outdated (the plugin's version has changed).

### Step 4: Check for Outdated Templates

```
WooCommerce → Status → System Status → Templates
```

This page shows which templates you've overridden and whether any are outdated. When WooCommerce updates a template, you need to review and merge the changes into your override.

## Hooks vs. Template Overrides

Before copying a template file, check if you can achieve the same result with hooks. Hooks survive WooCommerce updates; template overrides can break.

### When to Use Hooks

| Task | Method |
|------|--------|
| Add content before/after product title | `woocommerce_single_product_summary` hook |
| Remove a product element | `remove_action()` on the relevant hook |
| Change element order | `remove_action()` + `add_action()` with different priority |
| Add a custom tab | `woocommerce_product_tabs` filter |
| Modify cart item data | `woocommerce_cart_item_name` filter |

### Example: Rearranging Product Page Elements

```php
// Default priority order on single product:
// 5: title, 10: rating, 10: price, 20: excerpt, 25: add-to-cart, 30: meta, 40: sharing

// Move price above rating
remove_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_price', 10 );
add_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_price', 4 );

// Add custom content after price
add_action( 'woocommerce_single_product_summary', function() {
    if ( get_post_meta( get_the_ID(), '_free_shipping', true ) ) {
        echo '<p class="free-shipping-badge">Free Shipping</p>';
    }
}, 11 );

// Remove product meta (categories, tags, SKU)
remove_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_meta', 40 );
```

### When Template Override Is Necessary

- Restructuring the HTML layout entirely
- Changing how loop items are wrapped
- Adding complex conditional logic to template structure
- Cart or checkout layout modifications that hooks can't reach

## Common Customizations

### Product Loop (Archive/Shop)

```php
// Change number of products per row
add_filter( 'loop_shop_columns', function() {
    return 3; // 3 products per row
} );

// Change products per page
add_filter( 'loop_shop_per_page', function() {
    return 24;
} );

// Add "New" badge to recent products
add_action( 'woocommerce_before_shop_loop_item_title', function() {
    global $product;
    $created = strtotime( $product->get_date_created() );
    if ( ( time() - $created ) < ( 30 * DAY_IN_SECONDS ) ) {
        echo '<span class="badge badge-new">New</span>';
    }
}, 5 );
```

### Single Product Tabs

```php
// Add custom tab
add_filter( 'woocommerce_product_tabs', function( $tabs ) {
    $tabs['shipping_info'] = array(
        'title'    => __( 'Shipping Info', 'theme-textdomain' ),
        'priority' => 25,
        'callback' => function() {
            echo '<h2>Shipping Information</h2>';
            echo '<p>Free shipping on orders over $50. Standard delivery 3-5 business days.</p>';
        },
    );
    return $tabs;
} );

// Remove reviews tab
add_filter( 'woocommerce_product_tabs', function( $tabs ) {
    unset( $tabs['reviews'] );
    return $tabs;
} );

// Rename description tab
add_filter( 'woocommerce_product_tabs', function( $tabs ) {
    if ( isset( $tabs['description'] ) ) {
        $tabs['description']['title'] = __( 'Details', 'theme-textdomain' );
    }
    return $tabs;
} );
```

### Cart Customization

```php
// Add a message above the cart table
add_action( 'woocommerce_before_cart', function() {
    $remaining = 50 - WC()->cart->get_subtotal();
    if ( $remaining > 0 ) {
        printf(
            '<div class="free-shipping-notice">Add %s more for free shipping!</div>',
            wc_price( $remaining )
        );
    }
} );

// Add custom field to cart items
add_filter( 'woocommerce_cart_item_name', function( $name, $cart_item ) {
    $product = $cart_item['data'];
    $brand = $product->get_attribute( 'brand' );
    if ( $brand ) {
        $name = '<span class="item-brand">' . esc_html( $brand ) . '</span><br>' . $name;
    }
    return $name;
}, 10, 2 );
```

## Email Template Customization

WooCommerce emails use the same override system:

```
your-theme/woocommerce/emails/customer-completed-order.php
```

### Email-Specific Considerations

| Consideration | Details |
|--------------|---------|
| Inline CSS only | Email clients don't support `<style>` blocks reliably |
| Table-based layout | Modern CSS layout doesn't work in most email clients |
| Test across clients | Outlook, Gmail, Apple Mail render differently |
| Include unsubscribe | Required for marketing emails (not transactional) |

### Customizing Email Appearance

```php
// Change email header background color
add_filter( 'woocommerce_email_styles', function( $css ) {
    $css .= '#header_wrapper { background-color: #1a1a2e !important; }';
    return $css;
} );

// Add content after order table in emails
add_action( 'woocommerce_email_after_order_table', function( $order, $sent_to_admin ) {
    if ( ! $sent_to_admin ) {
        echo '<p style="margin-top:16px;">Questions about your order? Reply to this email.</p>';
    }
}, 10, 2 );
```

## Template Versioning and Updates

### Handling WooCommerce Updates

When WooCommerce updates a template you've overridden:

1. Check `WooCommerce → Status → Templates` for outdated warnings
2. Compare your override with the new template (diff tools help)
3. Merge WooCommerce's changes into your override
4. Update the `@version` header to match
5. Test thoroughly

### Minimizing Override Risk

| Practice | Why |
|----------|-----|
| Override as few templates as possible | Fewer files to maintain |
| Keep changes minimal | Easier to merge updates |
| Use hooks when possible | Survive updates automatically |
| Comment your modifications | Know what you changed and why |
| Track overrides in version control | Diff against WooCommerce updates |

### Declaring WooCommerce Support

Your theme must declare WooCommerce support:

```php
add_action( 'after_setup_theme', function() {
    add_theme_support( 'woocommerce' );
    add_theme_support( 'wc-product-gallery-zoom' );
    add_theme_support( 'wc-product-gallery-lightbox' );
    add_theme_support( 'wc-product-gallery-slider' );
} );
```

Without this, WooCommerce wraps its output in default markup that may conflict with your theme's layout.

## Debugging Templates

### Which Template Is Active?

```php
// Add to functions.php temporarily
add_filter( 'wc_get_template', function( $template, $template_name ) {
    if ( current_user_can( 'manage_options' ) ) {
        error_log( 'WC Template: ' . $template_name . ' → ' . $template );
    }
    return $template;
}, 10, 2 );
```

### Query Monitor

The Query Monitor plugin shows which WooCommerce templates are loaded on each page — far easier than logging.

## Further Reading

- [WooCommerce Hooks](../06-e-commerce/02-woocommerce-hooks.md) — Available hooks for customization
- [Checkout Customization](../06-e-commerce/04-checkout-customization.md) — Checkout-specific modifications
- [Child Themes](./02-child-themes.md) — Safe override patterns
- [WooCommerce Template Documentation](https://woocommerce.com/document/template-structure/) — Official reference
