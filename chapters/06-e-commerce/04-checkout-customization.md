# Checkout Customization

Checkout is the most critical page in your store. Every change here can either increase or destroy conversions.

## Checkout Architecture

WooCommerce checkout has two main parts:

```
┌─────────────────────────────────────────┐
│           Checkout Form                 │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │ Billing Info │  │ Shipping Info    │ │
│  └──────────────┘  └──────────────────┘ │
│  ┌──────────────────────────────────┐   │
│  │ Additional Fields / Notes        │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           Order Review                  │
│  ┌──────────────────────────────────┐   │
│  │ Cart Items / Totals              │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ Payment Methods                  │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ Place Order Button               │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Field Groups

WooCommerce organizes fields into groups:

| Group | Key | Description |
|-------|-----|-------------|
| Billing | `billing` | Billing address and contact |
| Shipping | `shipping` | Shipping address |
| Account | `account` | Username/password for registration |
| Order | `order` | Order notes and custom |

## Managing Checkout Fields

### Field Structure

```php
$fields['billing']['billing_phone'] = array(
    'type'        => 'tel',
    'label'       => 'Phone',
    'placeholder' => '+1 555 123 4567',
    'required'    => true,
    'class'       => array( 'form-row-wide' ),
    'priority'    => 100,
    'validate'    => array( 'phone' ),
    'autocomplete' => 'tel',
);
```

### Field Types

| Type | Visualization |
|------|---------------|
| `text` | Standard text input |
| `textarea` | Multi-line text |
| `select` | Dropdown |
| `radio` | Radio buttons |
| `checkbox` | Single checkbox |
| `password` | Password field |
| `email` | Email with validation |
| `tel` | Phone number |
| `number` | Numeric input |
| `country` | Country selector |
| `state` | State/region selector |

### Field Priority

Priority determines display order:

```php
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    // Move email to first place
    $fields['billing']['billing_email']['priority'] = 5;

    // Company after everything
    $fields['billing']['billing_company']['priority'] = 120;

    return $fields;
} );
```

Default priorities:
```
billing_first_name: 10
billing_last_name: 20
billing_company: 30
billing_country: 40
billing_address_1: 50
billing_address_2: 60
billing_city: 70
billing_state: 80
billing_postcode: 90
billing_phone: 100
billing_email: 110
```

## Common Customizations

### Removing Fields

```php
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    // Remove company
    unset( $fields['billing']['billing_company'] );

    // Remove address line 2
    unset( $fields['billing']['billing_address_2'] );
    unset( $fields['shipping']['shipping_address_2'] );

    // Remove order notes
    unset( $fields['order']['order_comments'] );

    return $fields;
} );
```

### Modifying Existing Fields

```php
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    // Change label
    $fields['billing']['billing_phone']['label'] = 'Mobile Phone';

    // Make optional
    $fields['billing']['billing_company']['required'] = false;

    // Add placeholder
    $fields['billing']['billing_email']['placeholder'] = 'you@example.com';

    // Change width (form-row-first, form-row-last, form-row-wide)
    $fields['billing']['billing_phone']['class'] = array( 'form-row-wide' );

    return $fields;
} );
```

### Adding New Fields

```php
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    // Text field
    $fields['billing']['billing_vat_number'] = array(
        'type'        => 'text',
        'label'       => 'VAT Number',
        'placeholder' => 'EU123456789',
        'required'    => false,
        'class'       => array( 'form-row-wide' ),
        'priority'    => 115,
    );

    // Select field
    $fields['order']['delivery_time'] = array(
        'type'     => 'select',
        'label'    => 'Preferred Delivery Time',
        'required' => true,
        'options'  => array(
            ''          => 'Select time slot',
            'morning'   => '9:00 - 12:00',
            'afternoon' => '12:00 - 17:00',
            'evening'   => '17:00 - 21:00',
        ),
        'priority' => 10,
    );

    // Checkbox
    $fields['order']['gift_wrap'] = array(
        'type'    => 'checkbox',
        'label'   => 'Gift wrap this order (+$5)',
        'default' => 0,
        'class'   => array( 'form-row-wide' ),
    );

    return $fields;
} );
```

## Saving Custom Fields

### Save to Order Meta

```php
// On checkout
add_action( 'woocommerce_checkout_update_order_meta', function( $order_id ) {
    $order = wc_get_order( $order_id );

    if ( ! empty( $_POST['billing_vat_number'] ) ) {
        $order->update_meta_data( '_billing_vat_number', sanitize_text_field( $_POST['billing_vat_number'] ) );
    }

    if ( ! empty( $_POST['delivery_time'] ) ) {
        $order->update_meta_data( '_delivery_time', sanitize_text_field( $_POST['delivery_time'] ) );
    }

    if ( isset( $_POST['gift_wrap'] ) ) {
        $order->update_meta_data( '_gift_wrap', 'yes' );
    }

    $order->save();
} );
```

### Display in Admin

```php
// In order details
add_action( 'woocommerce_admin_order_data_after_billing_address', function( $order ) {
    $vat = $order->get_meta( '_billing_vat_number' );
    if ( $vat ) {
        echo '<p><strong>VAT Number:</strong> ' . esc_html( $vat ) . '</p>';
    }
} );

// In order meta box
add_action( 'woocommerce_admin_order_data_after_order_details', function( $order ) {
    $time = $order->get_meta( '_delivery_time' );
    $gift = $order->get_meta( '_gift_wrap' );

    if ( $time ) {
        echo '<p><strong>Delivery Time:</strong> ' . esc_html( $time ) . '</p>';
    }
    if ( $gift === 'yes' ) {
        echo '<p><strong>Gift Wrap:</strong> Yes</p>';
    }
} );
```

### Display in Emails

```php
add_action( 'woocommerce_email_after_order_table', function( $order, $sent_to_admin ) {
    $time = $order->get_meta( '_delivery_time' );
    if ( $time ) {
        echo '<p><strong>Delivery Time:</strong> ' . esc_html( $time ) . '</p>';
    }
}, 10, 2 );
```

## Validation

### Built-in Validators

```php
$fields['billing']['billing_email'] = array(
    'validate' => array( 'email' ),
);

$fields['billing']['billing_phone'] = array(
    'validate' => array( 'phone' ),
);

$fields['billing']['billing_postcode'] = array(
    'validate' => array( 'postcode' ),
);
```

### Custom Validation

```php
add_action( 'woocommerce_checkout_process', function() {
    // VAT validation
    if ( ! empty( $_POST['billing_vat_number'] ) ) {
        $vat = sanitize_text_field( $_POST['billing_vat_number'] );

        // EU VAT format: 2 letters + 8-12 digits
        if ( ! preg_match( '/^[A-Z]{2}[0-9A-Z]{8,12}$/', strtoupper( $vat ) ) ) {
            wc_add_notice( 'Please enter a valid VAT number (e.g., EU123456789).', 'error' );
        }
    }

    // Required delivery time for local pickup
    $shipping_method = WC()->session->get( 'chosen_shipping_methods' );
    if ( strpos( $shipping_method[0], 'local_pickup' ) !== false ) {
        if ( empty( $_POST['delivery_time'] ) ) {
            wc_add_notice( 'Please select a delivery time for local pickup.', 'error' );
        }
    }
} );
```

## Conditional Fields

### Show/Hide Based on Selection

```php
// JavaScript for conditional logic
add_action( 'wp_footer', function() {
    if ( ! is_checkout() ) return;
    ?>
    <script>
    jQuery(function($) {
        // Show VAT field only for certain countries
        function toggleVatField() {
            var country = $('#billing_country').val();
            if (['DE', 'FR', 'IT', 'ES', 'NL'].includes(country)) {
                $('#billing_vat_number_field').show();
            } else {
                $('#billing_vat_number_field').hide();
            }
        }

        $('#billing_country').on('change', toggleVatField);
        toggleVatField(); // Initial state
    });
    </script>
    <?php
} );
```

### Show Based on Shipping Method

```php
add_action( 'wp_footer', function() {
    if ( ! is_checkout() ) return;
    ?>
    <script>
    jQuery(function($) {
        $(document.body).on('updated_checkout', function() {
            var method = $('input[name="shipping_method[0]"]:checked').val();
            if (method && method.indexOf('local_pickup') !== -1) {
                $('#delivery_time_field').show();
            } else {
                $('#delivery_time_field').hide();
            }
        });
    });
    </script>
    <?php
} );
```

## Layout Modifications

### CSS Classes

```css
/* form-row-first - left column */
/* form-row-last - right column */
/* form-row-wide - full width */

.woocommerce-checkout .form-row-first,
.woocommerce-checkout .form-row-last {
    width: 48%;
}

.woocommerce-checkout .form-row-wide {
    width: 100%;
}
```

### Layout Changes via Hooks

```php
// Remove shipping if same as billing
add_filter( 'woocommerce_ship_to_different_address_checked', '__return_false' );

// Hide shipping section for virtual products only cart
add_filter( 'woocommerce_cart_needs_shipping', function( $needs_shipping ) {
    $only_virtual = true;
    foreach ( WC()->cart->get_cart() as $item ) {
        if ( ! $item['data']->is_virtual() ) {
            $only_virtual = false;
            break;
        }
    }
    return ! $only_virtual;
} );
```

## Block Checkout (Gutenberg)

WooCommerce Blocks introduces a new checkout:

```php
// Check if block checkout is being used
if ( has_block( 'woocommerce/checkout' ) ) {
    // Block-based checkout
} else {
    // Classic checkout
}
```

**For block checkout customization:** Use `woocommerce_blocks_checkout_*` filters and JavaScript filters. Classic PHP hooks don't work.

## Common Pitfalls

### 1. Don't Forget Sanitization

```php
// Wrong
$order->update_meta_data( '_custom', $_POST['custom_field'] );

// Right
$order->update_meta_data( '_custom', sanitize_text_field( $_POST['custom_field'] ) );
```

### 2. Checkout Fragment Updates

Custom fields may not update on AJAX update:

```php
// Add field to fragments
add_filter( 'woocommerce_update_order_review_fragments', function( $fragments ) {
    ob_start();
    woocommerce_form_field( 'delivery_time', array(/* ... */), WC()->checkout->get_value( 'delivery_time' ) );
    $fragments['.delivery-time-field'] = ob_get_clean();
    return $fragments;
} );
```

### 3. Required Fields and Guests

```php
// Required field for guests only
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    if ( ! is_user_logged_in() ) {
        $fields['billing']['billing_phone']['required'] = true;
    }
    return $fields;
} );
```

## Testing Checklist

- [ ] All fields display correctly
- [ ] Required fields block submit when empty
- [ ] Custom validation works
- [ ] Data saves to order meta
- [ ] Data displays in admin
- [ ] Data is included in emails
- [ ] Works with guest checkout
- [ ] Works with logged-in users
- [ ] Responsive on mobile
- [ ] Works with different payment methods

## Further Reading

- [WooCommerce Hooks](./02-woocommerce-hooks.md) - All checkout hooks
- [WooCommerce Fundamentals](./01-woocommerce-fundamentals.md) - Data storage
- [Official Checkout Field Documentation](https://woocommerce.com/document/tutorial-customising-checkout-fields-using-actions-and-filters/)
