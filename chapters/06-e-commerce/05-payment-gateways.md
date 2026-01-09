# Payment Gateways

Proper payment gateway setup is critical - mistakes here mean lost sales or security issues.

## How Payment Gateways Work

```
Customer clicks "Pay"
        ↓
WooCommerce collects payment data
        ↓
Gateway processes payment (redirect or on-site)
        ↓
Gateway returns result
        ↓
WooCommerce updates order status
```

## Types of Integrations

| Type | Description | Example |
|------|-------------|---------|
| **Redirect** | Customer goes to external page | PayPal Standard |
| **Direct/On-site** | Card entered on your site | Stripe |
| **Iframe** | Embedded form from gateway | Braintree |
| **Hosted Fields** | Gateway fields that look like yours | Stripe Elements |

**Security note:** Direct integration requires PCI DSS compliance. Hosted Fields is recommended - looks native, but data doesn't pass through your server.

## Popular Gateways

| Gateway | Fees | Notes |
|---------|------|-------|
| **Stripe** | 2.9% + $0.30 (US) | Easiest integration |
| **PayPal** | 2.9% + fixed fee | Familiar to customers |
| **Square** | 2.9% + $0.30 | Good for in-person too |
| **Authorize.net** | 2.9% + $0.30 | Established, reliable |
| **Braintree** | 2.9% + $0.30 | PayPal owned |

## Stripe Integration

### Basic Setup

```
WooCommerce > Settings > Payments > Stripe

☑ Enable Stripe
☑ Enable Payment Request Buttons (Apple/Google Pay)

Test mode: Use test keys for development
Live mode: Production keys
```

### Webhook Configuration

Webhooks are critical - without them WooCommerce doesn't know about successful payments:

```
Stripe Dashboard > Developers > Webhooks

Endpoint URL: https://yoursite.com/?wc-api=wc_stripe
Events to send:
- payment_intent.succeeded
- payment_intent.payment_failed
- charge.refunded
- charge.dispute.created
```

### Stripe Hooks

```php
// After successful Stripe payment
add_action( 'woocommerce_payment_complete', function( $order_id ) {
    $order = wc_get_order( $order_id );

    if ( $order->get_payment_method() === 'stripe' ) {
        // Stripe-specific logic
        $transaction_id = $order->get_transaction_id();
    }
} );

// Custom metadata to Stripe
add_filter( 'wc_stripe_payment_metadata', function( $metadata, $order ) {
    $metadata['customer_note'] = $order->get_customer_note();
    return $metadata;
}, 10, 2 );
```

## PayPal Integration

### PayPal Commerce Platform (Recommended)

The new PayPal plugin supports:
- PayPal Checkout
- Pay Later options
- Venmo (US)
- Card processing via PayPal

```
WooCommerce > Settings > Payments > PayPal

Connect your PayPal account (OAuth flow)
```

### IPN (Instant Payment Notification)

```
PayPal Dashboard > Account Settings > Notifications

IPN URL: https://yoursite.com/?wc-api=WC_Gateway_Paypal
```

## Custom Payment Gateway

Structure of a payment gateway class:

```php
class WC_Gateway_Custom extends WC_Payment_Gateway {

    public function __construct() {
        $this->id                 = 'custom_gateway';
        $this->method_title       = 'Custom Gateway';
        $this->method_description = 'Pay with Custom Gateway';
        $this->has_fields         = true; // Shows fields on checkout

        // Load settings
        $this->init_form_fields();
        $this->init_settings();

        $this->title       = $this->get_option( 'title' );
        $this->description = $this->get_option( 'description' );
        $this->enabled     = $this->get_option( 'enabled' );

        // Save settings
        add_action( 'woocommerce_update_options_payment_gateways_' . $this->id,
            array( $this, 'process_admin_options' ) );
    }

    // Admin settings fields
    public function init_form_fields() {
        $this->form_fields = array(
            'enabled' => array(
                'title'   => 'Enable/Disable',
                'type'    => 'checkbox',
                'label'   => 'Enable Custom Gateway',
                'default' => 'no',
            ),
            'title' => array(
                'title'       => 'Title',
                'type'        => 'text',
                'description' => 'Payment method title on checkout',
                'default'     => 'Custom Payment',
            ),
            'api_key' => array(
                'title' => 'API Key',
                'type'  => 'password',
            ),
        );
    }

    // Checkout payment fields
    public function payment_fields() {
        echo '<p>' . esc_html( $this->description ) . '</p>';
        // Add custom fields if needed
    }

    // Process payment
    public function process_payment( $order_id ) {
        $order = wc_get_order( $order_id );

        // Call external API
        $response = $this->call_payment_api( $order );

        if ( $response['success'] ) {
            // Mark as paid
            $order->payment_complete( $response['transaction_id'] );

            // Empty cart
            WC()->cart->empty_cart();

            // Return success
            return array(
                'result'   => 'success',
                'redirect' => $this->get_return_url( $order ),
            );
        } else {
            // Payment failed
            wc_add_notice( $response['error_message'], 'error' );
            return array( 'result' => 'fail' );
        }
    }

    private function call_payment_api( $order ) {
        // Implement API call
    }
}

// Register gateway
add_filter( 'woocommerce_payment_gateways', function( $gateways ) {
    $gateways[] = 'WC_Gateway_Custom';
    return $gateways;
} );
```

## Refunds

### Programmatic Refund

```php
// Full refund
$refund = wc_create_refund( array(
    'amount'   => $order->get_total(),
    'reason'   => 'Customer request',
    'order_id' => $order_id,
    'refund_payment' => true, // Trigger gateway refund
) );

// Partial refund
$refund = wc_create_refund( array(
    'amount'   => 25.00,
    'reason'   => 'Partial refund for damaged item',
    'order_id' => $order_id,
    'refund_payment' => true,
) );
```

### Refund Hooks

```php
// On refund creation
add_action( 'woocommerce_refund_created', function( $refund_id, $args ) {
    $refund = wc_get_order( $refund_id );
    $order = wc_get_order( $refund->get_parent_id() );

    // Notify external system
}, 10, 2 );

// After successful gateway refund
add_action( 'woocommerce_order_refunded', function( $order_id, $refund_id ) {
    // Refund processed by gateway
}, 10, 2 );
```

## Testing Payments

### Test Cards (Stripe)

| Card Number | Result |
|-------------|--------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Declined |
| 4000 0000 0000 9995 | Insufficient funds |
| 4000 0027 6000 3184 | Requires 3D Secure |

### Test Mode Checklist

- [ ] Enable test/sandbox mode
- [ ] Use test API keys
- [ ] Test successful payment
- [ ] Test declined card
- [ ] Test 3D Secure flow
- [ ] Test refund
- [ ] Verify webhook delivery
- [ ] Check order status updates
- [ ] Test email notifications

## Security Best Practices

### 1. Never Log Card Data

```php
// WRONG - never!
error_log( 'Card: ' . $_POST['card_number'] );

// Right - only log transaction IDs
error_log( 'Transaction ID: ' . $transaction_id );
```

### 2. Always Use HTTPS

```php
// Check in gateway
if ( ! is_ssl() && ! $this->testmode ) {
    wc_add_notice( 'This payment method requires SSL.', 'error' );
    return false;
}
```

### 3. Validate Webhook Signatures

```php
// Stripe webhook signature verification
$payload = file_get_contents( 'php://input' );
$sig_header = $_SERVER['HTTP_STRIPE_SIGNATURE'];

try {
    $event = \Stripe\Webhook::constructEvent(
        $payload,
        $sig_header,
        $webhook_secret
    );
} catch ( \Exception $e ) {
    http_response_code( 400 );
    exit();
}
```

## Troubleshooting

### Payment Not Recording

1. Check webhook URL is correct
2. Check webhook events are enabled
3. See WooCommerce > Status > Logs
4. Check SSL certificate

### 3D Secure Issues

```php
// For Stripe - ensure return URL is correct
add_filter( 'wc_stripe_payment_intent_args', function( $args ) {
    $args['return_url'] = wc_get_checkout_url();
    return $args;
} );
```

### Currency Mismatch

```php
// Check gateway supports currency
public function is_available() {
    if ( ! in_array( get_woocommerce_currency(), array( 'EUR', 'GBP', 'USD' ) ) ) {
        return false;
    }
    return parent::is_available();
}
```

## Further Reading

- [WooCommerce Hooks](./02-woocommerce-hooks.md) - Payment-related hooks
- [Checkout Customization](./04-checkout-customization.md) - Checkout flow
- [Stripe Documentation](https://stripe.com/docs/payments/accept-a-payment)
- [PayPal Developer](https://developer.paypal.com/docs/checkout/)
