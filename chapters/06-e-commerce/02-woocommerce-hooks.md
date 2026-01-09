# WooCommerce Hooks

WooCommerce has hundreds of hooks. Here are the most commonly used ones for real customizations, with explanations of why and when to use each.

## Hook Philosophy

WooCommerce follows WordPress patterns:
- **Actions** - "do something at this moment" (add content, trigger processes)
- **Filters** - "modify this value before it's used" (change prices, text, HTML)

### Why Hooks Matter More in WooCommerce

Unlike a simple blog where hooks are convenient, in WooCommerce hooks are **essential**:

1. **WooCommerce updates frequently** - Direct file modifications get overwritten
2. **Complex execution order** - Cart calculations, taxes, shipping all depend on each other
3. **Multiple systems interact** - Payment gateways, shipping providers, inventory management
4. **Theme independence** - Your customizations should work across themes

### The Hook Timing Problem

WooCommerce hooks fire in a specific order and many depend on each other. Understanding this prevents bugs:

```php
// WRONG: WC() is not fully loaded yet at plugins_loaded
add_action( 'plugins_loaded', function() {
    $cart_total = WC()->cart->get_cart_total(); // Fatal error!
} );

// RIGHT: Wait for WooCommerce to fully initialize
add_action( 'woocommerce_init', function() {
    // WC() is ready, cart exists, sessions are loaded
} );

// ALSO RIGHT: For frontend, wait even later
add_action( 'wp', function() {
    if ( is_cart() ) {
        // Cart page-specific logic
    }
} );
```

**Hook initialization order:**
1. `plugins_loaded` - WooCommerce plugin file is loaded
2. `woocommerce_loaded` - WooCommerce classes are available
3. `woocommerce_init` - WooCommerce is initialized
4. `wp_loaded` - WordPress is fully loaded
5. `template_redirect` - Right before template rendering

## Product Hooks

### Modify Price Display

The price you see on product pages goes through several filters. Understanding which filter to use depends on what you want to change:

```php
// woocommerce_get_price_html - modifies the DISPLAYED price HTML
// Use this when you want to ADD something visual (badge, text)
// The actual price calculation is unchanged
add_filter( 'woocommerce_get_price_html', function( $price_html, $product ) {
    if ( $product->is_on_sale() ) {
        // Add a visual badge next to the price
        $price_html .= '<span class="sale-badge">SALE</span>';
    }
    return $price_html;
}, 10, 2 );

// woocommerce_product_get_price - modifies the ACTUAL price value
// Use this when you want to CHANGE the price (discounts, surcharges)
// Affects calculations, not just display
add_filter( 'woocommerce_product_get_price', function( $price, $product ) {
    // 10% discount for logged-in users
    if ( is_user_logged_in() ) {
        $price = $price * 0.9;
    }
    return $price;
}, 10, 2 );
```

**Why two different hooks?** Separating display from calculation allows:
- Display changes that don't affect cart totals
- Calculation changes that propagate correctly through taxes, shipping, etc.

### Add Custom Tab on Product Page

Product tabs let you add information sections without modifying templates:

```php
// Add a new tab - the filter controls WHICH tabs appear
add_filter( 'woocommerce_product_tabs', function( $tabs ) {

    // Each tab needs: title, priority, callback
    $tabs['specifications'] = array(
        'title'    => 'Specifications',  // What users see
        'priority' => 20,                 // Order: lower = earlier (Description is 10)
        'callback' => 'render_specifications_tab', // Function to output content
    );

    // You can also remove default tabs
    unset( $tabs['reviews'] );           // Remove reviews
    unset( $tabs['additional_information'] ); // Remove attributes table

    // Or reorder them
    $tabs['description']['priority'] = 5; // Move description first

    return $tabs;
} );

// The callback renders the tab content
function render_specifications_tab() {
    global $product;

    // Get custom field data
    $specs = get_post_meta( $product->get_id(), '_specifications', true );

    if ( $specs ) {
        echo '<h2>Technical Specifications</h2>';
        echo wp_kses_post( $specs ); // Safe HTML output
    }
}
```

**Why use tabs instead of template overrides?** Tabs are:
- Theme-independent (work with any theme)
- Easier to maintain (no file merging on updates)
- Conditional (can show/hide based on product type, category, etc.)

### Product Page Actions (Visual Positions)

WooCommerce fires actions at specific positions on product pages. These hooks let you inject content without modifying templates:

```php
// Visual representation of single product page hooks
// (Each hook is a point where you can add content)

// BEFORE product content
woocommerce_before_single_product         // Very top, before everything
woocommerce_before_single_product_summary // Before the summary column

// INSIDE product summary (right side, next to image)
woocommerce_single_product_summary
├── woocommerce_template_single_title     (priority 5)  // Product name
├── woocommerce_template_single_rating    (priority 10) // Stars
├── woocommerce_template_single_price     (priority 10) // Price
├── woocommerce_template_single_excerpt   (priority 20) // Short description
├── woocommerce_template_single_add_to_cart (priority 30) // Add to cart button
├── woocommerce_template_single_meta      (priority 40) // SKU, categories, tags
└── woocommerce_template_single_sharing   (priority 50) // Share buttons

// AFTER summary
woocommerce_after_single_product_summary  // After summary, before tabs
woocommerce_after_single_product          // Very bottom
```

**Example: Move price above rating:**
```php
// Step 1: Remove from current position
remove_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_price', 10 );

// Step 2: Add back at new position (before rating, which is at 10)
add_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_price', 5 );
```

**Example: Add custom content after price:**
```php
add_action( 'woocommerce_single_product_summary', function() {
    global $product;

    // Show estimated delivery date
    $delivery_days = get_post_meta( $product->get_id(), '_delivery_days', true ) ?: 3;
    $delivery_date = date( 'M j', strtotime( "+{$delivery_days} weekdays" ) );

    echo '<p class="delivery-estimate">Estimated delivery: ' . esc_html( $delivery_date ) . '</p>';
}, 15 ); // After price (10), before excerpt (20)
```

## Cart Hooks

### Add Message to Cart

Cart messages guide customers toward desired behaviors (free shipping thresholds, upsells):

```php
add_action( 'woocommerce_before_cart', function() {
    $cart_total = WC()->cart->get_cart_contents_total(); // Subtotal without shipping/tax
    $free_shipping_min = 50;

    if ( $cart_total < $free_shipping_min ) {
        $remaining = $free_shipping_min - $cart_total;

        // wc_print_notice() is the proper way to show WooCommerce-styled messages
        // Types: 'success', 'notice', 'error'
        wc_print_notice(
            sprintf( 'Add %s more for free shipping!', wc_price( $remaining ) ),
            'notice'
        );
    }
} );
```

**Why `wc_print_notice()` instead of `echo`?**
- Consistent styling with WooCommerce
- Proper HTML structure with dismiss buttons
- Accessible (screen reader friendly)
- Theme-independent appearance

### Validate Add to Cart

This filter runs BEFORE an item is added to cart. Return `false` to prevent the addition:

```php
add_filter( 'woocommerce_add_to_cart_validation', function( $valid, $product_id, $quantity ) {
    // $valid starts as true - previous filters may have set it false

    // Example: Maximum 5 units per product
    if ( $quantity > 5 ) {
        wc_add_notice( 'Maximum 5 units per product allowed.', 'error' );
        return false; // Prevents add to cart
    }

    // Example: B2B only products (check user role)
    $product = wc_get_product( $product_id );
    $b2b_only = $product->get_meta( '_b2b_only' );

    if ( $b2b_only === 'yes' && ! current_user_can( 'wholesale_customer' ) ) {
        wc_add_notice( 'This product is only available to wholesale customers.', 'error' );
        return false;
    }

    // Example: Check combined cart quantity
    $cart_quantity = 0;
    foreach ( WC()->cart->get_cart() as $cart_item ) {
        if ( $cart_item['product_id'] === $product_id ) {
            $cart_quantity += $cart_item['quantity'];
        }
    }

    if ( $cart_quantity + $quantity > 10 ) {
        wc_add_notice( 'Maximum 10 units of this product per order.', 'error' );
        return false;
    }

    return $valid; // Return original $valid to respect previous filters
}, 10, 3 );
```

**Why use this instead of stock limits?** Stock limits are global. This hook enables:
- Per-customer limits
- Role-based restrictions
- Complex conditional logic
- Custom error messages

### Modify Cart Item Data

Add custom data to cart items that persists through the checkout process:

```php
// STEP 1: Add custom data when item is added to cart
add_filter( 'woocommerce_add_cart_item_data', function( $cart_item_data, $product_id ) {
    // Check if custom field was submitted (from product page form)
    if ( isset( $_POST['gift_message'] ) && ! empty( $_POST['gift_message'] ) ) {
        // Sanitize and store the data
        $cart_item_data['gift_message'] = sanitize_textarea_field( $_POST['gift_message'] );

        // IMPORTANT: Generate unique key to prevent cart item merging
        // Without this, two items with different gift messages would merge
        $cart_item_data['unique_key'] = md5( microtime() . rand() );
    }
    return $cart_item_data;
}, 10, 2 );

// STEP 2: Display custom data in cart
add_filter( 'woocommerce_get_item_data', function( $item_data, $cart_item ) {
    if ( isset( $cart_item['gift_message'] ) ) {
        // This adds a row below the product name in cart
        $item_data[] = array(
            'key'   => 'Gift Message',              // Label
            'value' => $cart_item['gift_message'],  // Value
        );
    }
    return $item_data;
}, 10, 2 );

// STEP 3: Save custom data to order (so it persists after purchase)
add_action( 'woocommerce_checkout_create_order_line_item', function( $item, $cart_item_key, $values, $order ) {
    if ( isset( $values['gift_message'] ) ) {
        // This saves to order item meta, visible in admin
        $item->add_meta_data( 'Gift Message', $values['gift_message'], true );
    }
}, 10, 4 );
```

**The three-step pattern is essential:**
1. **Add to cart** - Data enters the system
2. **Display in cart** - Customer can see their selection
3. **Save to order** - Data persists after checkout

Without step 3, the data disappears when the cart is cleared.

## Checkout Hooks

### Checkout Fields Modification

WooCommerce checkout fields are highly customizable. Understanding the structure is key:

```php
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    // $fields is organized by section:
    // - $fields['billing'] - Billing address fields
    // - $fields['shipping'] - Shipping address fields
    // - $fields['account'] - Account creation fields (username, password)
    // - $fields['order'] - Order notes

    // Make company field optional (it's required by default in some setups)
    $fields['billing']['billing_company']['required'] = false;

    // Remove phone field entirely
    unset( $fields['billing']['billing_phone'] );

    // Add custom field
    $fields['billing']['billing_vat'] = array(
        'type'        => 'text',           // 'text', 'textarea', 'select', 'radio', etc.
        'label'       => 'VAT Number',     // Field label
        'placeholder' => 'EU123456789',    // Placeholder text
        'required'    => false,            // Is it mandatory?
        'class'       => array('form-row-wide'), // CSS classes for layout
        'priority'    => 120,              // Order: lower = earlier
        'validate'    => array('postcode'), // Built-in validation rules
    );

    // Reorder fields (priority controls position)
    $fields['billing']['billing_email']['priority'] = 5; // Move email to top

    return $fields;
} );
```

**Field configuration options:**
| Property | Purpose | Example |
|----------|---------|---------|
| `type` | Field type | 'text', 'email', 'tel', 'select', 'textarea', 'checkbox', 'radio' |
| `label` | Label text | 'VAT Number' |
| `required` | Is mandatory? | true/false |
| `class` | CSS classes | array('form-row-first'), array('form-row-last'), array('form-row-wide') |
| `priority` | Display order | 10, 20, 30 (lower = earlier) |
| `options` | For select/radio | array('opt1' => 'Option 1', 'opt2' => 'Option 2') |
| `default` | Default value | 'US' |

### Save Custom Checkout Field

Adding a field is only half the work. You must also save and display it:

```php
// SAVE: Store the field value when order is created
add_action( 'woocommerce_checkout_update_order_meta', function( $order_id ) {
    if ( ! empty( $_POST['billing_vat'] ) ) {
        $order = wc_get_order( $order_id );

        // ALWAYS sanitize user input
        $vat = sanitize_text_field( $_POST['billing_vat'] );

        // Save to order meta
        $order->update_meta_data( '_billing_vat', $vat );
        $order->save(); // Don't forget to save!
    }
} );

// DISPLAY IN ADMIN: Show the field in order details
add_action( 'woocommerce_admin_order_data_after_billing_address', function( $order ) {
    $vat = $order->get_meta( '_billing_vat' );

    if ( $vat ) {
        echo '<p><strong>VAT Number:</strong> ' . esc_html( $vat ) . '</p>';
    }
} );

// DISPLAY IN EMAILS: Include in order confirmation
add_action( 'woocommerce_email_after_order_table', function( $order, $sent_to_admin, $plain_text ) {
    $vat = $order->get_meta( '_billing_vat' );

    if ( $vat ) {
        if ( $plain_text ) {
            echo "VAT Number: " . $vat . "\n";
        } else {
            echo '<p><strong>VAT Number:</strong> ' . esc_html( $vat ) . '</p>';
        }
    }
}, 10, 3 );
```

**Why the underscore prefix (`_billing_vat`)?**
The underscore makes the meta key "hidden" from WordPress's custom fields box. Use it for programmatically-managed fields. Without underscore, the field appears in the custom fields meta box (useful for admin-editable fields).

### Checkout Validation

Validation happens when the customer clicks "Place Order". Stop the order if something is wrong:

```php
add_action( 'woocommerce_checkout_process', function() {
    // This runs BEFORE payment, after form submission

    // Validate VAT format (European VAT numbers)
    if ( ! empty( $_POST['billing_vat'] ) ) {
        $vat = sanitize_text_field( $_POST['billing_vat'] );

        // EU VAT format: 2 letters + 8-12 digits
        if ( ! preg_match( '/^[A-Z]{2}[0-9]{8,12}$/', strtoupper( $vat ) ) ) {
            // wc_add_notice with 'error' type STOPS checkout
            wc_add_notice(
                'Please enter a valid VAT number (e.g., DE123456789).',
                'error'
            );
        }
    }

    // Validate minimum order amount
    $minimum = 25;
    if ( WC()->cart->get_cart_contents_total() < $minimum ) {
        wc_add_notice(
            sprintf( 'Minimum order amount is %s.', wc_price( $minimum ) ),
            'error'
        );
    }

    // Business hours validation
    $hour = current_time( 'G' ); // 0-23
    if ( $hour < 8 || $hour > 20 ) {
        wc_add_notice( 'Orders can only be placed between 8 AM and 8 PM.', 'error' );
    }
} );
```

**Important:** Each `wc_add_notice( ..., 'error' )` call prevents checkout from completing. The customer stays on the checkout page and sees all error messages.

## Order Hooks

### On Order Status Change

Order status changes trigger business processes (fulfillment, notifications, integrations):

```php
// GENERAL: Fires on ANY status change
add_action( 'woocommerce_order_status_changed', function( $order_id, $old_status, $new_status ) {
    $order = wc_get_order( $order_id );

    // Log the change
    $order->add_order_note(
        sprintf( 'Status changed from %s to %s', $old_status, $new_status )
    );

    // Example: Send to fulfillment API when completed
    if ( $new_status === 'completed' ) {
        send_to_fulfillment_api( $order );
    }

    // Example: Alert on high-value orders going on-hold
    if ( $new_status === 'on-hold' && $order->get_total() > 500 ) {
        wp_mail(
            'manager@yourstore.com',
            'High-value order on hold',
            'Order #' . $order_id . ' ($' . $order->get_total() . ') is on hold.'
        );
    }
}, 10, 3 );

// SPECIFIC: Fires only for specific transitions
// Pattern: woocommerce_order_status_{from}_to_{to}
add_action( 'woocommerce_order_status_pending_to_processing', function( $order_id ) {
    // Payment received! Order ready for fulfillment
    $order = wc_get_order( $order_id );

    // Reduce stock (usually handled automatically, but can customize)
    // Trigger warehouse notification
    // Update CRM
} );

add_action( 'woocommerce_order_status_completed', function( $order_id ) {
    // Order fully complete (shipped and done)
    // Perfect for: loyalty points, review request emails, etc.
} );
```

**When to use which:**
- `woocommerce_order_status_changed` - Need to compare old vs new status
- `woocommerce_order_status_{status}` - React to entering a specific status
- `woocommerce_order_status_{from}_to_{to}` - React to specific transition

### On Order Creation

```php
// woocommerce_checkout_order_created - Customer placed order via checkout
// This is the most common hook for "order just created"
add_action( 'woocommerce_checkout_order_created', function( $order ) {
    // $order is already a WC_Order object

    // Add internal note
    $order->add_order_note( 'Order created via website checkout.' );

    // Set custom meta
    $order->update_meta_data( '_source', 'website' );
    $order->save();
} );

// woocommerce_new_order - Fires for ALL new orders (including API, admin, imports)
// Use carefully - this runs for manual orders too
add_action( 'woocommerce_new_order', function( $order_id ) {
    // This fires even for admin-created orders
    // Don't send customer notifications here!
} );
```

**The difference matters:** If you're integrating with an external system, use `woocommerce_checkout_order_created` for website orders only. Use `woocommerce_new_order` if you truly need to catch ALL order creation.

## Email Hooks

### Add Content to Emails

WooCommerce sends many transactional emails. Customize them with hooks:

```php
// Add content AFTER the order table in emails
add_action( 'woocommerce_email_after_order_table', function( $order, $sent_to_admin, $plain_text, $email ) {
    // $email->id tells you which email this is:
    // - 'customer_completed_order' - Order complete notification
    // - 'customer_processing_order' - Order received notification
    // - 'customer_on_hold_order' - Order on hold
    // - 'new_order' - Admin notification

    // Only add to specific email types
    if ( $email->id === 'customer_completed_order' ) {
        if ( $plain_text ) {
            echo "\nThank you for your purchase!\n";
            echo "Use code RETURN10 for 10% off your next order.\n";
        } else {
            echo '<div style="margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 5px;">';
            echo '<p>Thank you for your purchase! Use code <strong>RETURN10</strong> for 10% off your next order.</p>';
            echo '</div>';
        }
    }
}, 10, 4 );

// Add content at the very top of all customer emails
add_action( 'woocommerce_email_header', function( $email_heading, $email ) {
    if ( strpos( $email->id, 'customer_' ) === 0 ) {
        // Only for customer-facing emails
        echo '<p style="text-align: center;">Questions? Call us at 1-800-STORE</p>';
    }
}, 10, 2 );
```

**Available email hooks (in order):**
1. `woocommerce_email_header` - After header image
2. `woocommerce_email_order_details` - Order details section
3. `woocommerce_email_order_meta` - After order meta
4. `woocommerce_email_after_order_table` - After line items table
5. `woocommerce_email_customer_details` - Customer address section
6. `woocommerce_email_footer` - Footer area

### Custom Email Triggers

Programmatically send WooCommerce emails:

```php
// Manually trigger an existing email
function send_order_complete_email( $order_id ) {
    // Get the WooCommerce mailer
    $mailer = WC()->mailer();

    // Get the specific email class
    $email = $mailer->get_emails()['WC_Email_Customer_Completed_Order'];

    // Trigger it
    $email->trigger( $order_id );
}

// Available email classes:
// WC_Email_New_Order - Admin new order notification
// WC_Email_Customer_Processing_Order - Customer payment received
// WC_Email_Customer_Completed_Order - Customer order shipped/complete
// WC_Email_Customer_Refunded_Order - Customer refund notification
// WC_Email_Customer_Invoice - Manual invoice email
```

## Payment Hooks

### Before/After Payment Form

Add content around the payment methods section:

```php
// Before payment methods are displayed
add_action( 'woocommerce_review_order_before_payment', function() {
    echo '<div class="payment-security-notice">';
    echo '<span class="dashicons dashicons-lock"></span>';
    echo '<p>Your payment information is encrypted and secure.</p>';
    echo '</div>';
} );

// After payment methods, before Place Order button
add_action( 'woocommerce_review_order_after_payment', function() {
    echo '<p class="terms-reminder">By placing your order, you agree to our Terms & Conditions.</p>';
} );
```

### On Successful Payment

The thank you page is your conversion moment:

```php
// Runs on thank you page - order is confirmed and paid
add_action( 'woocommerce_thankyou', function( $order_id ) {
    // Guard: runs once even for direct page visits
    if ( ! $order_id ) {
        return;
    }

    $order = wc_get_order( $order_id );

    // Prevent duplicate tracking (important for page refreshes)
    if ( $order->get_meta( '_thankyou_tracked' ) ) {
        return;
    }

    // Track conversion
    ?>
    <script>
        // Google Analytics 4 purchase event
        gtag('event', 'purchase', {
            transaction_id: '<?php echo esc_js( $order->get_order_number() ); ?>',
            value: <?php echo esc_js( $order->get_total() ); ?>,
            currency: '<?php echo esc_js( $order->get_currency() ); ?>',
            items: [
                <?php foreach ( $order->get_items() as $item ) : ?>
                {
                    item_id: '<?php echo esc_js( $item->get_product_id() ); ?>',
                    item_name: '<?php echo esc_js( $item->get_name() ); ?>',
                    quantity: <?php echo esc_js( $item->get_quantity() ); ?>,
                    price: <?php echo esc_js( $order->get_item_total( $item ) ); ?>
                },
                <?php endforeach; ?>
            ]
        });
    </script>
    <?php

    // Mark as tracked
    $order->update_meta_data( '_thankyou_tracked', true );
    $order->save();
}, 10 );
```

## Ajax Hooks

WooCommerce operations often need to happen without page reload:

```php
// Register custom AJAX action
// wp_ajax_{action} - For logged-in users
// wp_ajax_nopriv_{action} - For guests (important for non-logged-in shoppers!)
add_action( 'wp_ajax_check_product_stock', 'handle_stock_check' );
add_action( 'wp_ajax_nopriv_check_product_stock', 'handle_stock_check' );

function handle_stock_check() {
    // ALWAYS verify nonce for security
    check_ajax_referer( 'wc-stock-check-nonce', 'security' );

    // Get and validate input
    $product_id = isset( $_POST['product_id'] ) ? absint( $_POST['product_id'] ) : 0;

    if ( ! $product_id ) {
        wp_send_json_error( array( 'message' => 'Invalid product' ) );
    }

    $product = wc_get_product( $product_id );

    if ( ! $product ) {
        wp_send_json_error( array( 'message' => 'Product not found' ) );
    }

    // Return data
    wp_send_json_success( array(
        'in_stock'       => $product->is_in_stock(),
        'stock_quantity' => $product->get_stock_quantity(),
        'stock_status'   => $product->get_stock_status(),
    ) );
}
```

**Frontend JavaScript:**
```javascript
jQuery(function($) {
    $('.check-stock-btn').on('click', function() {
        $.ajax({
            url: wc_add_to_cart_params.ajax_url, // WooCommerce provides this
            type: 'POST',
            data: {
                action: 'check_product_stock',
                security: wc_stock_check.nonce, // Localized from PHP
                product_id: $(this).data('product-id')
            },
            success: function(response) {
                if (response.success) {
                    alert('Stock: ' + response.data.stock_quantity);
                }
            }
        });
    });
});
```

## REST API Hooks

### Extend Product REST Response

Add custom data to API responses:

```php
// Add custom field to product API response
add_filter( 'woocommerce_rest_prepare_product_object', function( $response, $product, $request ) {
    // Add custom meta
    $response->data['warehouse_location'] = $product->get_meta( '_warehouse_location' );

    // Add computed data
    $response->data['profit_margin'] = calculate_margin( $product );

    // Add related data
    $response->data['total_sold'] = get_post_meta( $product->get_id(), 'total_sales', true );

    return $response;
}, 10, 3 );
```

## Hook Discovery Tips

### Find All Hooks on a Page

When you need to discover what hooks are available:

```php
// Add temporarily to functions.php - shows all WooCommerce hooks in debug.log
add_action( 'all', function( $tag ) {
    if ( strpos( $tag, 'woocommerce' ) !== false ) {
        error_log( 'Hook: ' . $tag );
    }
} );
```

**Better option: Query Monitor plugin**
- Shows all hooks in execution order
- Shows parameters passed to each hook
- Shows all callbacks attached
- No code modification needed

### Common Debugging Approach

```php
// When a hook isn't working, verify it fires
add_action( 'your_suspected_hook', function() {
    error_log( 'Hook fired at: ' . current_time( 'mysql' ) );
    error_log( 'Args: ' . print_r( func_get_args(), true ) );
}, 0 ); // Priority 0 = runs first
```

## Common Pitfalls

### 1. Priority Matters

```php
// Wrong: Default priority (10) might not work if others already ran
add_action( 'woocommerce_single_product_summary', 'my_function' );

// Right: Be explicit - check what priority the element you want to affect uses
add_action( 'woocommerce_single_product_summary', 'my_function', 15 );

// To run BEFORE everything else
add_action( 'woocommerce_single_product_summary', 'my_function', 1 );

// To run AFTER everything else
add_action( 'woocommerce_single_product_summary', 'my_function', 99 );
```

### 2. Hook Timing

```php
// Wrong: WC() singleton doesn't exist yet
add_action( 'plugins_loaded', function() {
    WC()->cart->get_cart(); // Fatal error!
} );

// Wrong: Session might not be loaded
add_action( 'init', function() {
    WC()->session->get( 'something' ); // Might fail
} );

// Right: Wait for WooCommerce to fully load
add_action( 'woocommerce_init', function() {
    // Safe to use WC() here
} );

// Right for frontend operations
add_action( 'wp', function() {
    // Template conditionals work here (is_shop(), is_product(), etc.)
} );
```

### 3. HPOS Compatibility

```php
// Wrong: Direct database queries break with HPOS
global $wpdb;
$orders = $wpdb->get_results(
    "SELECT ID FROM {$wpdb->posts} WHERE post_type = 'shop_order'"
);

// Right: Use WooCommerce API (works with any storage)
$orders = wc_get_orders( array(
    'limit'  => 100,
    'status' => 'processing',
) );

// Wrong: Using get_post() for orders
$order_post = get_post( $order_id );

// Right: Using wc_get_order()
$order = wc_get_order( $order_id );
```

## Further Reading

- [WooCommerce Fundamentals](./01-woocommerce-fundamentals.md) - Architecture and data model
- [Checkout Customization](./04-checkout-customization.md) - Detailed checkout guide
- [WordPress Hooks System](../01-wordpress-plugin-architecture/02-hooks-system.md) - Hooks basics
- [WooCommerce Hook Reference](https://woocommerce.github.io/code-reference/hooks/hooks.html) - Official documentation
