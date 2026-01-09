# Shipping Configuration

Shipping setup is one of the most confusing parts of WooCommerce. Here's how it all works, systematized.

## Shipping Architecture

```
Shipping Zones (geographic regions)
    └── Shipping Methods (delivery options)
            └── Shipping Rates (prices)
```

**Key principle:** Customers only see methods from the zone that matches their address.

## Shipping Zones

### How Zones Work

WooCommerce checks the customer's address and finds the **first** matching zone:

```
1. Checks specific postcodes
2. Checks regions/states
3. Checks countries
4. If nothing matches → "Locations not covered" zone
```

**Important:** Zone order matters. More specific zones should be first.

### Example Zone Structure

| Zone | Regions | Methods |
|------|---------|---------|
| Local Delivery | Postcodes 90001-90099 | Same Day, Standard |
| California | CA state | UPS, USPS |
| United States | US | UPS, USPS, FedEx |
| Canada | CA | UPS International |
| Rest of World | Locations not covered | Contact for quote |

### Postcode-based Zones

```
WooCommerce > Settings > Shipping > Add zone

Zone name: Downtown LA
Zone regions: United States
Limit to postcodes: 90001...90099
```

Use `...` for range or `,` for list:
- `90001...90099` = from 90001 to 90099
- `90001, 90024, 90210` = only these
- `90*` = all starting with 90

## Shipping Methods

### Built-in Methods

| Method | Usage |
|--------|-------|
| **Flat Rate** | Fixed price |
| **Free Shipping** | Free above certain amount |
| **Local Pickup** | Pickup from location |

### Flat Rate with Formulas

Flat rate supports formulas:

```
// Fixed price
10

// Price per product
5 * [qty]

// Percentage of cart
[cost] * 0.1

// Combination
5 + (2 * [qty])

// Min/max
[cost] * 0.05 min 5 max 20
```

**Placeholders:**
- `[qty]` - number of products
- `[cost]` - cart value
- `[fee]` - additional fee

### Shipping Classes

For different prices by product type:

```
WooCommerce > Settings > Shipping > Shipping classes

Classes:
- heavy-items (Heavy Products)
- fragile (Fragile Items)
- bulky (Oversized)
```

In Flat Rate settings:
```
Shipping class costs:
- heavy-items: 15
- fragile: 10
- bulky: 20
- No shipping class: 5
```

Calculation type:
- **Per class** - adds the price of each class
- **Per order** - takes the highest price

## Free Shipping

### Free Shipping Conditions

```
WooCommerce > Settings > Shipping > [Zone] > Free Shipping

Requires:
- N/A (always free)
- A minimum order amount (min amount)
- A minimum order amount OR a coupon (amount OR coupon)
- A minimum order amount AND a coupon (amount AND coupon)

Minimum order amount: 100
```

### Hide Paid Methods When Free Shipping Available

```php
// Hide other methods when free shipping is available
add_filter( 'woocommerce_package_rates', function( $rates ) {
    $dominated = false;

    foreach ( $rates as $rate ) {
        if ( strpos( $rate->method_id, 'free_shipping' ) !== false ) {
            $dominated = true;
            break;
        }
    }

    if ( $dominated ) {
        foreach ( $rates as $rate_key => $rate ) {
            if ( strpos( $rate->method_id, 'free_shipping' ) === false ) {
                unset( $rates[ $rate_key ] );
            }
        }
    }

    return $rates;
} );
```

## Custom Shipping Methods

### Integration with Carriers

Most major carriers have plugins:

```
UPS: "UPS Shipping Method" (official)
FedEx: "FedEx Shipping Method"
USPS: "USPS Shipping Method"
DHL: "DHL Express"
```

### Custom Shipping Method Class

```php
class WC_Shipping_Custom extends WC_Shipping_Method {

    public function __construct( $instance_id = 0 ) {
        $this->id                 = 'custom_shipping';
        $this->instance_id        = absint( $instance_id );
        $this->method_title       = 'Custom Shipping';
        $this->method_description = 'Custom shipping method';
        $this->supports           = array(
            'shipping-zones',
            'instance-settings',
        );

        $this->init();
    }

    public function init() {
        $this->init_form_fields();
        $this->init_settings();

        $this->title = $this->get_option( 'title' );

        add_action( 'woocommerce_update_options_shipping_' . $this->id,
            array( $this, 'process_admin_options' ) );
    }

    public function init_form_fields() {
        $this->instance_form_fields = array(
            'title' => array(
                'title'   => 'Title',
                'type'    => 'text',
                'default' => 'Custom Shipping',
            ),
            'base_cost' => array(
                'title'   => 'Base Cost',
                'type'    => 'price',
                'default' => '10',
            ),
        );
    }

    public function calculate_shipping( $package = array() ) {
        $cost = $this->get_option( 'base_cost' );

        // Custom logic
        $weight = 0;
        foreach ( $package['contents'] as $item ) {
            $product = $item['data'];
            $weight += $product->get_weight() * $item['quantity'];
        }

        if ( $weight > 5 ) {
            $cost += ( $weight - 5 ) * 2; // +$2 for each kg over 5
        }

        $this->add_rate( array(
            'id'    => $this->get_rate_id(),
            'label' => $this->title,
            'cost'  => $cost,
        ) );
    }
}

// Register
add_filter( 'woocommerce_shipping_methods', function( $methods ) {
    $methods['custom_shipping'] = 'WC_Shipping_Custom';
    return $methods;
} );
```

## Shipping Calculations

### Weight-based Shipping

```php
add_filter( 'woocommerce_package_rates', function( $rates, $package ) {
    // Calculate total weight
    $total_weight = 0;
    foreach ( $package['contents'] as $item ) {
        $product = $item['data'];
        if ( $product->get_weight() ) {
            $total_weight += floatval( $product->get_weight() ) * $item['quantity'];
        }
    }

    // Modify rates based on weight
    foreach ( $rates as $rate_key => $rate ) {
        if ( $rate->method_id === 'flat_rate' ) {
            if ( $total_weight > 10 ) {
                $rates[ $rate_key ]->cost += 20; // Additional fee
            }
        }
    }

    return $rates;
}, 10, 2 );
```

### Destination-based Logic

```php
add_filter( 'woocommerce_package_rates', function( $rates, $package ) {
    $destination = $package['destination'];

    // Different price for certain cities
    $downtown_postcodes = array( '90001', '90002', '90003' );

    if ( in_array( $destination['postcode'], $downtown_postcodes ) ) {
        foreach ( $rates as $rate_key => $rate ) {
            if ( $rate->method_id === 'flat_rate' ) {
                $rates[ $rate_key ]->cost = 5; // Lower price for downtown
            }
        }
    }

    return $rates;
}, 10, 2 );
```

## Shipping Labels & Tracking

### Adding Tracking Number

```php
// Meta box in order
add_action( 'woocommerce_admin_order_data_after_shipping_address', function( $order ) {
    $tracking = $order->get_meta( '_tracking_number' );
    ?>
    <p class="form-field">
        <label for="tracking_number">Tracking Number:</label>
        <input type="text" id="tracking_number" name="tracking_number"
               value="<?php echo esc_attr( $tracking ); ?>">
    </p>
    <?php
} );

// Save
add_action( 'woocommerce_process_shop_order_meta', function( $order_id ) {
    if ( isset( $_POST['tracking_number'] ) ) {
        $order = wc_get_order( $order_id );
        $order->update_meta_data( '_tracking_number', sanitize_text_field( $_POST['tracking_number'] ) );
        $order->save();
    }
} );

// Show to customer
add_action( 'woocommerce_order_details_after_order_table', function( $order ) {
    $tracking = $order->get_meta( '_tracking_number' );
    if ( $tracking ) {
        echo '<p><strong>Tracking:</strong> ' . esc_html( $tracking ) . '</p>';
    }
} );
```

## Local Pickup Locations

### Multiple Pickup Points

```php
add_filter( 'woocommerce_shipping_local_pickup_option', function( $options ) {
    return array(
        'title' => 'Select pickup location',
        'locations' => array(
            'downtown'  => 'Downtown Store - 123 Main St',
            'westside'  => 'Westside Location - 456 West Ave',
            'mall'      => 'Shopping Mall - Level 2',
        ),
    );
} );
```

## Troubleshooting

### "No shipping methods available"

1. Check address matches a zone
2. Check methods are enabled in the zone
3. Check products are not "virtual"
4. Check shipping class restrictions

```php
// Debug: See which zone is being matched
add_action( 'woocommerce_before_shipping_calculator', function() {
    $packages = WC()->shipping()->get_packages();
    foreach ( $packages as $package ) {
        $zone = WC_Shipping_Zones::get_zone_matching_package( $package );
        error_log( 'Matched zone: ' . $zone->get_zone_name() );
    }
} );
```

### Shipping Not Updating

```php
// Force recalculation
WC()->cart->calculate_shipping();

// Clear shipping cache
WC()->session->set( 'shipping_for_package_0', false );
```

### Cart Shows Wrong Shipping

```php
// On cart change, recalculate
add_action( 'woocommerce_cart_updated', function() {
    WC()->cart->calculate_shipping();
} );
```

## Performance Tips

### Cache Shipping Calculations

```php
// WooCommerce caches shipping per package hash
// If you have custom logic, internally cache API calls

add_filter( 'woocommerce_package_rates', function( $rates, $package ) {
    $cache_key = 'shipping_' . md5( serialize( $package['destination'] ) );
    $cached = get_transient( $cache_key );

    if ( $cached !== false ) {
        return $cached;
    }

    // ... calculate rates ...

    set_transient( $cache_key, $rates, HOUR_IN_SECONDS );
    return $rates;
}, 10, 2 );
```

## Further Reading

- [Checkout Customization](./04-checkout-customization.md) - Shipping in checkout context
- [WooCommerce Hooks](./02-woocommerce-hooks.md) - Shipping hooks
- [WooCommerce Shipping Docs](https://woocommerce.com/document/setting-up-shipping-zones/)
