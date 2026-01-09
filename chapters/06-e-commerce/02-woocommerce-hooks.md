# WooCommerce Hooks

WooCommerce has hundreds of hooks. Here are the most commonly used ones for real customizations.

## Hook Philosophy

WooCommerce follows WordPress patterns:
- **Actions** - "do something at this moment"
- **Filters** - "modify this value"

But there's a critical difference: WooCommerce hooks fire in a specific order and many depend on each other.

## Product Hooks

### Modify Price Display

```php
// Change how the price is displayed (formatting)
add_filter( 'woocommerce_get_price_html', function( $price_html, $product ) {
    if ( $product->is_on_sale() ) {
        $price_html .= '<span class="sale-badge">SALE</span>';
    }
    return $price_html;
}, 10, 2 );
```

### Add Custom Tab on Product Page

```php
// Add a new tab
add_filter( 'woocommerce_product_tabs', function( $tabs ) {
    $tabs['specifications'] = array(
        'title'    => 'Specifications',
        'priority' => 20,
        'callback' => 'render_specifications_tab',
    );
    return $tabs;
} );

function render_specifications_tab() {
    global $product;
    echo get_post_meta( $product->get_id(), '_specifications', true );
}
```

### Product Page Actions (Visual Position)

```php
// These hooks control the single product page layout
// Order matters!

// Before product summary
woocommerce_before_single_product_summary
├── woocommerce_show_product_images (priority 20)
└── ...

// Inside product summary
woocommerce_single_product_summary
├── woocommerce_template_single_title (5)
├── woocommerce_template_single_rating (10)
├── woocommerce_template_single_price (10)
├── woocommerce_template_single_excerpt (20)
├── woocommerce_template_single_add_to_cart (30)
├── woocommerce_template_single_meta (40)
└── woocommerce_template_single_sharing (50)
```

**Example: Move price above rating:**
```php
remove_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_price', 10 );
add_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_price', 5 );
```

## Cart Hooks

### Add Message to Cart

```php
add_action( 'woocommerce_before_cart', function() {
    if ( WC()->cart->get_cart_contents_total() < 50 ) {
        wc_print_notice( 'Add another $' . (50 - WC()->cart->get_cart_contents_total()) . ' for free shipping!', 'notice' );
    }
} );
```

### Validate Add to Cart

```php
add_filter( 'woocommerce_add_to_cart_validation', function( $valid, $product_id, $quantity ) {
    $product = wc_get_product( $product_id );

    // Example: Maximum 5 units of one product
    if ( $quantity > 5 ) {
        wc_add_notice( 'Maximum 5 units of one product.', 'error' );
        return false;
    }

    return $valid;
}, 10, 3 );
```

### Modify Cart Item Data

```php
// Add custom data to cart item
add_filter( 'woocommerce_add_cart_item_data', function( $cart_item_data, $product_id ) {
    if ( isset( $_POST['gift_message'] ) ) {
        $cart_item_data['gift_message'] = sanitize_textarea_field( $_POST['gift_message'] );
    }
    return $cart_item_data;
}, 10, 2 );

// Display custom data in cart
add_filter( 'woocommerce_get_item_data', function( $item_data, $cart_item ) {
    if ( isset( $cart_item['gift_message'] ) ) {
        $item_data[] = array(
            'key'   => 'Gift Message',
            'value' => $cart_item['gift_message'],
        );
    }
    return $item_data;
}, 10, 2 );
```

## Checkout Hooks

### Checkout Fields Modification

```php
// Modify checkout fields
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    // Make company optional
    $fields['billing']['billing_company']['required'] = false;

    // Remove phone
    unset( $fields['billing']['billing_phone'] );

    // Add custom field
    $fields['billing']['billing_vat'] = array(
        'type'        => 'text',
        'label'       => 'VAT Number',
        'placeholder' => 'EU123456789',
        'required'    => false,
        'priority'    => 120,
    );

    return $fields;
} );
```

### Save Custom Checkout Field

```php
// Save to order meta
add_action( 'woocommerce_checkout_update_order_meta', function( $order_id ) {
    if ( ! empty( $_POST['billing_vat'] ) ) {
        $order = wc_get_order( $order_id );
        $order->update_meta_data( '_billing_vat', sanitize_text_field( $_POST['billing_vat'] ) );
        $order->save();
    }
} );

// Display in admin order details
add_action( 'woocommerce_admin_order_data_after_billing_address', function( $order ) {
    $vat = $order->get_meta( '_billing_vat' );
    if ( $vat ) {
        echo '<p><strong>VAT:</strong> ' . esc_html( $vat ) . '</p>';
    }
} );
```

### Checkout Validation

```php
add_action( 'woocommerce_checkout_process', function() {
    // Validate VAT format
    if ( ! empty( $_POST['billing_vat'] ) ) {
        $vat = sanitize_text_field( $_POST['billing_vat'] );
        if ( ! preg_match( '/^[A-Z]{2}[0-9]{9,12}$/', $vat ) ) {
            wc_add_notice( 'Invalid VAT number format.', 'error' );
        }
    }
} );
```

## Order Hooks

### On Order Status Change

```php
// On any status change
add_action( 'woocommerce_order_status_changed', function( $order_id, $old_status, $new_status ) {
    $order = wc_get_order( $order_id );

    // Example: Send to external API when completed
    if ( $new_status === 'completed' ) {
        send_to_fulfillment_api( $order );
    }
}, 10, 3 );

// Specific status transitions
add_action( 'woocommerce_order_status_pending_to_processing', function( $order_id ) {
    // Order is paid, ready for processing
} );

add_action( 'woocommerce_order_status_completed', function( $order_id ) {
    // Order is completed
} );
```

### On Order Creation

```php
// After order is created (checkout complete)
add_action( 'woocommerce_checkout_order_created', function( $order ) {
    // $order is WC_Order object
    $order->add_order_note( 'Order created via website.' );
} );

// IMPORTANT: woocommerce_new_order fires for manual orders from admin too
add_action( 'woocommerce_new_order', function( $order_id ) {
    // Careful - this is for all new orders
} );
```

## Email Hooks

### Add Content to Emails

```php
// Add after order details in customer emails
add_action( 'woocommerce_email_after_order_table', function( $order, $sent_to_admin, $plain_text, $email ) {
    if ( $email->id === 'customer_completed_order' ) {
        echo '<p>Thank you for your purchase! Use code RETURN10 for 10% off your next order.</p>';
    }
}, 10, 4 );
```

### Custom Email Triggers

```php
// Trigger email on custom event
$mailer = WC()->mailer();
$email = $mailer->get_emails()['WC_Email_Customer_Completed_Order'];
$email->trigger( $order_id );
```

## Payment Hooks

### Before/After Payment Form

```php
// Add message before payment methods
add_action( 'woocommerce_review_order_before_payment', function() {
    echo '<div class="payment-security-notice">';
    echo '<p>Your payment is secure and encrypted.</p>';
    echo '</div>';
} );
```

### On Successful Payment

```php
// After successful payment (redirect)
add_action( 'woocommerce_thankyou', function( $order_id ) {
    $order = wc_get_order( $order_id );

    // Track conversion
    echo '<script>trackConversion(' . $order->get_total() . ');</script>';
} );
```

## Ajax Hooks

WooCommerce AJAX endpoints:

```php
// Custom AJAX action
add_action( 'wp_ajax_my_custom_action', 'handle_my_action' );
add_action( 'wp_ajax_nopriv_my_custom_action', 'handle_my_action' );

function handle_my_action() {
    check_ajax_referer( 'my-nonce', 'security' );

    $product_id = intval( $_POST['product_id'] );
    $product = wc_get_product( $product_id );

    wp_send_json_success( array(
        'price' => $product->get_price(),
        'stock' => $product->get_stock_quantity(),
    ) );
}
```

## REST API Hooks

### Extend Product REST Response

```php
add_filter( 'woocommerce_rest_prepare_product_object', function( $response, $product ) {
    $response->data['custom_field'] = $product->get_meta( '_custom_field' );
    return $response;
}, 10, 2 );
```

## Hook Discovery Tips

### Find All Hooks on a Page

```php
// Temporarily add to functions.php
add_action( 'all', function( $tag ) {
    if ( strpos( $tag, 'woocommerce' ) !== false ) {
        error_log( 'Hook: ' . $tag );
    }
} );
```

### Query Monitor

Query Monitor plugin shows:
- All fired hooks in execution order
- Parameters passed to each hook
- Callbacks attached to hooks

## Common Pitfalls

### 1. Priority Matters

```php
// Wrong: Might not work if another plugin has lower priority
add_action( 'woocommerce_single_product_summary', 'my_function' ); // default 10

// Right: Be explicit with priority
add_action( 'woocommerce_single_product_summary', 'my_function', 15 );
```

### 2. Hook Timing

```php
// Wrong: WC() is not available at plugins_loaded
add_action( 'plugins_loaded', function() {
    WC()->cart->get_cart(); // Error!
} );

// Right: Wait for woocommerce_init or later
add_action( 'woocommerce_init', function() {
    // WC() is ready
} );
```

### 3. HPOS Compatibility

```php
// Wrong: Won't work with HPOS
$order_id = $wpdb->get_var( "SELECT ID FROM {$wpdb->posts} WHERE post_type = 'shop_order'..." );

// Right: Use WooCommerce API
$orders = wc_get_orders( array( 'limit' => 1 ) );
```

## Further Reading

- [WooCommerce Fundamentals](./01-woocommerce-fundamentals.md) - Architecture and data model
- [Checkout Customization](./04-checkout-customization.md) - Detailed checkout guide
- [WordPress Hooks System](../01-wordpress-plugin-architecture/02-hooks-system.md) - Hooks basics
- [WooCommerce Hook Reference](https://woocommerce.github.io/code-reference/hooks/hooks.html) - Official documentation
