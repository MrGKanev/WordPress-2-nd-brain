# Payment Gateways

Proper payment gateway setup is critical - mistakes here mean lost sales or security issues. This guide covers integration patterns, Stripe deep dive, webhooks, and handling edge cases like disputes and 3D Secure.

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
Webhook confirms payment (async)
        ↓
WooCommerce updates order status
```

**Important:** The synchronous response is not always reliable. Webhooks are the authoritative source of payment status.

## Types of Integrations

| Type | Security | UX | Example |
|------|----------|-----|---------|
| **Redirect** | High (off-site) | Worse (leaves site) | PayPal Standard |
| **Direct/On-site** | Requires PCI DSS | Best (seamless) | Custom integration |
| **Hosted Fields** | High (tokenized) | Good (looks native) | Stripe Elements |
| **Iframe** | High (sandboxed) | Medium | Braintree Drop-in |

**Recommendation:** Use **Hosted Fields** (Stripe Elements) - it looks native to your site, but card data never touches your server. This approach satisfies PCI SAQ A-EP requirements without the full PCI DSS audit burden.

## Popular Gateways Comparison

| Gateway | Base Fee | Per Transaction | Best For |
|---------|----------|-----------------|----------|
| **Stripe** | None | 2.9% + $0.30 | Most stores |
| **PayPal** | None | 2.9% + fixed | Buyer trust |
| **Square** | None | 2.9% + $0.30 | Omnichannel |
| **Authorize.net** | $25/month | 2.9% + $0.30 | Enterprise |
| **Braintree** | None | 2.9% + $0.30 | PayPal integration |

**Stripe** is generally recommended for:
- Best developer experience
- Excellent documentation
- Radar fraud protection included
- Easy subscription support
- Strong European SCA support

---

## Stripe Integration Deep Dive

### Installation Options

**Option 1: Official WooCommerce Stripe Plugin (Recommended)**

```bash
wp plugin install woocommerce-gateway-stripe --activate
```

**Option 2: Stripe for WooCommerce by WooCommerce**

Same plugin, maintained by Automattic.

### Basic Configuration

```
WooCommerce → Settings → Payments → Stripe

Settings to configure:
├── Enable Stripe: ✓
├── Title: Credit Card (Stripe)
├── Description: Pay securely with your credit card
├── Test mode: ✓ (during development)
├── Test Publishable key: pk_test_...
├── Test Secret key: sk_test_...
├── Webhook Secret: whsec_...
├── Inline Credit Card Form: ✓
├── Payment Request Buttons: ✓ (Apple Pay, Google Pay)
└── Saved cards: ✓
```

### API Keys Setup

1. Go to [Stripe Dashboard → Developers → API Keys](https://dashboard.stripe.com/apikeys)
2. Copy your **Publishable key** (pk_test_... or pk_live_...)
3. Copy your **Secret key** (sk_test_... or sk_live_...)
4. **Never expose your Secret key** in frontend code or version control

```php
// Add to wp-config.php for environment-based keys
define( 'STRIPE_SECRET_KEY', getenv('STRIPE_SECRET_KEY') ?: 'sk_test_xxx' );
define( 'STRIPE_PUBLISHABLE_KEY', getenv('STRIPE_PUBLISHABLE_KEY') ?: 'pk_test_xxx' );
```

---

## Webhook Configuration (Critical)

Webhooks are how Stripe tells WooCommerce about asynchronous events. Without webhooks, you'll miss:
- Successful payments (especially 3D Secure)
- Failed payments
- Refunds initiated from Stripe dashboard
- Disputes and chargebacks
- Subscription events

### Setting Up Webhooks

1. Go to [Stripe Dashboard → Developers → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Configure:

```
Endpoint URL: https://yoursite.com/?wc-api=wc_stripe
Description: WooCommerce Production

Events to send:
☑ payment_intent.succeeded
☑ payment_intent.payment_failed
☑ payment_intent.requires_action
☑ charge.refunded
☑ charge.dispute.created
☑ charge.dispute.closed
☑ checkout.session.completed
☑ customer.subscription.created
☑ customer.subscription.updated
☑ customer.subscription.deleted
☑ invoice.paid
☑ invoice.payment_failed
☑ review.opened
☑ review.closed
```

4. Copy the **Signing secret** (whsec_...) to WooCommerce settings

### Webhook Security

Always verify webhook signatures to prevent spoofing:

```php
// How the WooCommerce Stripe plugin handles this internally
function verify_webhook_signature() {
    $payload = file_get_contents( 'php://input' );
    $sig_header = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';
    $webhook_secret = get_option( 'woocommerce_stripe_webhook_secret' );

    try {
        $event = \Stripe\Webhook::constructEvent(
            $payload,
            $sig_header,
            $webhook_secret
        );
        return $event;
    } catch ( \Stripe\Exception\SignatureVerificationException $e ) {
        // Invalid signature
        http_response_code( 400 );
        error_log( 'Stripe webhook signature verification failed: ' . $e->getMessage() );
        exit();
    }
}
```

### Webhook Debugging

Check webhook delivery in Stripe Dashboard → Developers → Webhooks → Select endpoint → Recent deliveries.

Common issues:

| Status | Cause | Solution |
|--------|-------|----------|
| **400 Bad Request** | Signature mismatch | Check webhook secret matches |
| **404 Not Found** | Wrong URL | Verify endpoint URL |
| **500 Internal Error** | PHP error | Check WooCommerce logs |
| **Timeout** | Slow processing | Optimize webhook handler |

```php
// Log webhook events for debugging
add_action( 'woocommerce_api_wc_stripe', function() {
    $payload = file_get_contents( 'php://input' );
    $event = json_decode( $payload );

    error_log( 'Stripe webhook received: ' . $event->type );
    error_log( 'Event ID: ' . $event->id );
}, 5 );
```

---

## 3D Secure (SCA) Handling

**Strong Customer Authentication (SCA)** is required for European payments since September 2019. 3D Secure is the implementation.

### How 3D Secure Works

```
1. Customer enters card
        ↓
2. Stripe checks if 3DS required
        ↓
3. If yes: Customer redirected to bank authentication
        ↓
4. Customer confirms with password/SMS/biometrics
        ↓
5. Customer redirected back to your site
        ↓
6. Webhook confirms payment
```

### Payment Intents vs Charges

Old Stripe integration used **Charges API**. Modern integration uses **Payment Intents API** which handles 3D Secure automatically.

```php
// Modern approach - Payment Intents (used by WooCommerce plugin)
$intent = \Stripe\PaymentIntent::create([
    'amount' => 2000, // $20.00 in cents
    'currency' => 'usd',
    'payment_method' => $payment_method_id,
    'confirmation_method' => 'manual',
    'confirm' => true,
    'return_url' => wc_get_checkout_url(),
]);

// Handle different statuses
switch ( $intent->status ) {
    case 'succeeded':
        // Payment complete
        break;
    case 'requires_action':
        // 3D Secure required - redirect customer
        $redirect_url = $intent->next_action->redirect_to_url->url;
        break;
    case 'requires_payment_method':
        // Payment failed - ask for new card
        break;
}
```

### SCA Exemptions

Some payments can skip 3D Secure:

| Exemption | When Applied |
|-----------|--------------|
| **Low value** | Transactions under €30 |
| **Recurring** | Subsequent subscription payments |
| **Trusted merchant** | Customer whitelisted your business |
| **Low risk** | Stripe Radar assessment |
| **Corporate cards** | B2B payments |

```php
// Request exemption (Stripe decides if applicable)
add_filter( 'wc_stripe_payment_intent_args', function( $args ) {
    // Request merchant-initiated exemption for subscriptions
    if ( WC()->cart->needs_shipping() === false ) {
        $args['payment_method_options']['card']['request_three_d_secure'] = 'any';
    }
    return $args;
});
```

### Handling 3D Secure Failures

```php
// Hook into payment failures
add_action( 'woocommerce_order_status_failed', function( $order_id ) {
    $order = wc_get_order( $order_id );

    if ( $order->get_payment_method() !== 'stripe' ) {
        return;
    }

    $failure_reason = $order->get_meta( '_stripe_failure_reason' );

    // Log for analysis
    if ( strpos( $failure_reason, '3d_secure' ) !== false ) {
        error_log( "3D Secure failure for order $order_id: $failure_reason" );
    }

    // Optionally notify customer to retry
    $order->add_order_note( '3D Secure authentication failed. Customer may need to retry with different card.' );
});
```

---

## Stripe Subscriptions

For recurring payments with WooCommerce Subscriptions + Stripe.

### Subscription Webhooks

Additional events to enable:

```
☑ customer.subscription.created
☑ customer.subscription.updated
☑ customer.subscription.deleted
☑ customer.subscription.trial_will_end
☑ invoice.upcoming
☑ invoice.created
☑ invoice.paid
☑ invoice.payment_failed
☑ invoice.payment_action_required
```

### Handling Subscription Payment Failures

```php
// Retry failed subscription payments
add_action( 'woocommerce_subscription_payment_failed', function( $subscription, $order ) {
    // Stripe automatically retries - check settings in Dashboard

    // Log the failure
    $subscription->add_order_note(
        'Subscription payment failed. Stripe will retry per your retry schedule.'
    );

    // Optionally send custom notification
    do_action( 'custom_subscription_payment_failed_email', $subscription );
}, 10, 2 );

// When subscription is cancelled due to payment failures
add_action( 'woocommerce_subscription_status_cancelled', function( $subscription ) {
    if ( $subscription->get_payment_method() !== 'stripe' ) {
        return;
    }

    $last_order = $subscription->get_last_order( 'all' );
    if ( $last_order && $last_order->get_status() === 'failed' ) {
        // Cancelled due to payment failure
        // Send win-back email with link to update payment method
    }
});
```

### Saved Cards for Subscriptions

```php
// Check if customer has saved payment methods
$customer_id = get_current_user_id();
$stripe_customer_id = get_user_meta( $customer_id, '_stripe_customer_id', true );

if ( $stripe_customer_id ) {
    $stripe = new \Stripe\StripeClient( STRIPE_SECRET_KEY );
    $payment_methods = $stripe->paymentMethods->all([
        'customer' => $stripe_customer_id,
        'type' => 'card',
    ]);

    foreach ( $payment_methods->data as $pm ) {
        echo $pm->card->brand . ' ending in ' . $pm->card->last4;
    }
}
```

---

## Disputes and Chargebacks

Disputes cost money ($15 fee) and hurt your account standing. Handle them properly.

### Monitoring Disputes

```php
// Hook into dispute webhooks
add_action( 'woocommerce_api_wc_stripe', function() {
    $payload = file_get_contents( 'php://input' );
    $event = json_decode( $payload );

    if ( $event->type === 'charge.dispute.created' ) {
        $dispute = $event->data->object;

        // Find the order
        $charge_id = $dispute->charge;
        $orders = wc_get_orders([
            'meta_key' => '_stripe_charge_id',
            'meta_value' => $charge_id,
            'limit' => 1
        ]);

        if ( ! empty( $orders ) ) {
            $order = $orders[0];
            $order->update_status( 'on-hold', 'Dispute opened: ' . $dispute->reason );
            $order->add_order_note( sprintf(
                'Stripe dispute created. Reason: %s. Amount: %s. Evidence due by: %s',
                $dispute->reason,
                wc_price( $dispute->amount / 100 ),
                date( 'Y-m-d H:i', $dispute->evidence_details->due_by )
            ));

            // Alert admin
            wp_mail(
                get_option( 'admin_email' ),
                'Stripe Dispute Alert - Order #' . $order->get_id(),
                'A dispute was opened. Please submit evidence in Stripe Dashboard.'
            );
        }
    }
}, 20 );
```

### Preventing Disputes

Best practices to reduce chargebacks:

1. **Clear billing descriptor** - Set in Stripe Dashboard
2. **Order confirmation emails** - Immediate, with clear details
3. **Easy refund policy** - Refunds are cheaper than disputes
4. **Shipping tracking** - Proof of delivery
5. **Customer service** - Easy to contact before disputing

```php
// Add extra metadata to help with disputes
add_filter( 'wc_stripe_payment_metadata', function( $metadata, $order ) {
    $metadata['order_number'] = $order->get_order_number();
    $metadata['customer_email'] = $order->get_billing_email();
    $metadata['customer_ip'] = $order->get_customer_ip_address();
    $metadata['shipping_method'] = $order->get_shipping_method();

    // Add product names
    $items = [];
    foreach ( $order->get_items() as $item ) {
        $items[] = $item->get_name();
    }
    $metadata['products'] = implode( ', ', array_slice( $items, 0, 5 ) );

    return $metadata;
}, 10, 2 );
```

---

## Error Handling

### Common Stripe Errors

| Error Code | Meaning | User Message |
|------------|---------|--------------|
| `card_declined` | Generic decline | "Your card was declined. Please try another card." |
| `insufficient_funds` | Not enough money | "Insufficient funds. Please try another card." |
| `expired_card` | Card expired | "Your card has expired. Please use a different card." |
| `incorrect_cvc` | Wrong security code | "Incorrect security code. Please check and try again." |
| `processing_error` | Stripe issue | "Processing error. Please try again in a moment." |
| `rate_limit` | Too many requests | "Too many attempts. Please wait a moment." |

```php
// Customize error messages
add_filter( 'wc_stripe_error_messages', function( $messages ) {
    $messages['card_declined'] = 'Your payment was not authorized. Please contact your bank or try a different card.';
    $messages['insufficient_funds'] = 'Payment declined due to insufficient funds.';
    return $messages;
});

// Log errors for debugging
add_action( 'wc_stripe_process_payment_error', function( $exception, $order ) {
    $error_code = $exception->getStripeCode();
    $error_message = $exception->getMessage();

    error_log( sprintf(
        'Stripe payment error for order %d: [%s] %s',
        $order->get_id(),
        $error_code,
        $error_message
    ));
}, 10, 2 );
```

### Retry Logic

```php
// Implement retry for transient errors
function process_stripe_payment_with_retry( $order, $max_attempts = 3 ) {
    $attempts = 0;
    $last_error = null;

    while ( $attempts < $max_attempts ) {
        try {
            return process_stripe_payment( $order );
        } catch ( \Stripe\Exception\RateLimitException $e ) {
            $attempts++;
            $last_error = $e;
            sleep( pow( 2, $attempts ) ); // Exponential backoff
        } catch ( \Stripe\Exception\ApiConnectionException $e ) {
            $attempts++;
            $last_error = $e;
            sleep( 1 );
        } catch ( \Stripe\Exception\CardException $e ) {
            // Don't retry card errors
            throw $e;
        }
    }

    throw $last_error;
}
```

---

## PayPal Integration

### PayPal Checkout (Modern)

Use the official WooCommerce PayPal Payments plugin:

```bash
wp plugin install woocommerce-paypal-payments --activate
```

Features:
- PayPal Checkout buttons
- Pay Later / Pay in 4
- Venmo (US)
- Credit/Debit card processing

### IPN (Instant Payment Notification)

```
PayPal Dashboard → Account Settings → Notifications → IPN

IPN URL: https://yoursite.com/?wc-api=WC_Gateway_Paypal
```

### PayPal Webhooks (Preferred over IPN)

```
PayPal Developer → Dashboard → Webhooks

Webhook URL: https://yoursite.com/?wc-api=WC_Gateway_PPCP
Events:
☑ PAYMENT.CAPTURE.COMPLETED
☑ PAYMENT.CAPTURE.DENIED
☑ PAYMENT.CAPTURE.REFUNDED
☑ CHECKOUT.ORDER.APPROVED
```

---

## Custom Payment Gateway

### Basic Structure

```php
<?php
/**
 * Plugin Name: Custom Payment Gateway
 * Description: Example WooCommerce payment gateway
 */

if ( ! defined( 'ABSPATH' ) ) exit;

add_action( 'plugins_loaded', function() {
    if ( ! class_exists( 'WC_Payment_Gateway' ) ) {
        return;
    }

    class WC_Gateway_Custom extends WC_Payment_Gateway {

        public function __construct() {
            $this->id                 = 'custom_gateway';
            $this->icon               = ''; // URL to icon
            $this->has_fields         = true;
            $this->method_title       = 'Custom Gateway';
            $this->method_description = 'Accept payments via Custom Gateway';

            // Supports
            $this->supports = array(
                'products',
                'refunds',
                'subscriptions',
                'subscription_cancellation',
            );

            // Load settings
            $this->init_form_fields();
            $this->init_settings();

            $this->title       = $this->get_option( 'title' );
            $this->description = $this->get_option( 'description' );
            $this->enabled     = $this->get_option( 'enabled' );
            $this->testmode    = 'yes' === $this->get_option( 'testmode' );
            $this->api_key     = $this->testmode
                ? $this->get_option( 'test_api_key' )
                : $this->get_option( 'live_api_key' );

            // Save settings
            add_action( 'woocommerce_update_options_payment_gateways_' . $this->id,
                array( $this, 'process_admin_options' )
            );

            // Webhook handler
            add_action( 'woocommerce_api_' . strtolower( get_class( $this ) ),
                array( $this, 'webhook_handler' )
            );
        }

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
                    'description' => 'Payment method title shown on checkout',
                    'default'     => 'Custom Payment',
                ),
                'description' => array(
                    'title'       => 'Description',
                    'type'        => 'textarea',
                    'description' => 'Payment method description',
                    'default'     => 'Pay securely using Custom Gateway.',
                ),
                'testmode' => array(
                    'title'   => 'Test mode',
                    'type'    => 'checkbox',
                    'label'   => 'Enable test mode',
                    'default' => 'yes',
                ),
                'test_api_key' => array(
                    'title' => 'Test API Key',
                    'type'  => 'password',
                ),
                'live_api_key' => array(
                    'title' => 'Live API Key',
                    'type'  => 'password',
                ),
            );
        }

        public function payment_fields() {
            if ( $this->description ) {
                echo wpautop( wp_kses_post( $this->description ) );
            }

            if ( $this->testmode ) {
                echo '<p><strong>TEST MODE ENABLED</strong></p>';
            }

            // Add card fields or other inputs
            ?>
            <fieldset id="wc-<?php echo esc_attr( $this->id ); ?>-cc-form" class="wc-credit-card-form wc-payment-form">
                <?php do_action( 'woocommerce_credit_card_form_start', $this->id ); ?>
                <!-- Add your payment fields here -->
                <?php do_action( 'woocommerce_credit_card_form_end', $this->id ); ?>
                <div class="clear"></div>
            </fieldset>
            <?php
        }

        public function validate_fields() {
            // Validate payment fields
            return true;
        }

        public function process_payment( $order_id ) {
            $order = wc_get_order( $order_id );

            try {
                // Call your payment API
                $response = $this->call_api( array(
                    'amount'   => $order->get_total() * 100, // cents
                    'currency' => $order->get_currency(),
                    'email'    => $order->get_billing_email(),
                    // ... other parameters
                ));

                if ( $response['status'] === 'success' ) {
                    // Mark payment complete
                    $order->payment_complete( $response['transaction_id'] );

                    // Store transaction data
                    $order->update_meta_data( '_custom_transaction_id', $response['transaction_id'] );
                    $order->save();

                    // Empty cart
                    WC()->cart->empty_cart();

                    return array(
                        'result'   => 'success',
                        'redirect' => $this->get_return_url( $order ),
                    );
                } elseif ( $response['status'] === 'pending' ) {
                    // Payment requires action (like 3D Secure)
                    return array(
                        'result'   => 'success',
                        'redirect' => $response['redirect_url'],
                    );
                } else {
                    throw new Exception( $response['error_message'] );
                }

            } catch ( Exception $e ) {
                wc_add_notice( $e->getMessage(), 'error' );
                return array( 'result' => 'fail' );
            }
        }

        public function process_refund( $order_id, $amount = null, $reason = '' ) {
            $order = wc_get_order( $order_id );
            $transaction_id = $order->get_meta( '_custom_transaction_id' );

            if ( ! $transaction_id ) {
                return new WP_Error( 'error', 'No transaction ID found' );
            }

            try {
                $response = $this->call_api( array(
                    'action'         => 'refund',
                    'transaction_id' => $transaction_id,
                    'amount'         => $amount * 100,
                    'reason'         => $reason,
                ));

                if ( $response['status'] === 'success' ) {
                    $order->add_order_note( sprintf(
                        'Refund of %s processed. Refund ID: %s',
                        wc_price( $amount ),
                        $response['refund_id']
                    ));
                    return true;
                }

                return new WP_Error( 'error', $response['error_message'] );

            } catch ( Exception $e ) {
                return new WP_Error( 'error', $e->getMessage() );
            }
        }

        public function webhook_handler() {
            $payload = file_get_contents( 'php://input' );
            $event = json_decode( $payload, true );

            // Verify webhook signature
            if ( ! $this->verify_webhook( $payload ) ) {
                http_response_code( 400 );
                exit( 'Invalid signature' );
            }

            // Process webhook event
            switch ( $event['type'] ) {
                case 'payment.completed':
                    $this->handle_payment_completed( $event['data'] );
                    break;
                case 'payment.failed':
                    $this->handle_payment_failed( $event['data'] );
                    break;
                case 'refund.completed':
                    $this->handle_refund_completed( $event['data'] );
                    break;
            }

            http_response_code( 200 );
            exit( 'OK' );
        }

        private function call_api( $args ) {
            // Implement your API call
            $response = wp_remote_post( 'https://api.customgateway.com/v1/charge', array(
                'headers' => array(
                    'Authorization' => 'Bearer ' . $this->api_key,
                    'Content-Type'  => 'application/json',
                ),
                'body'    => wp_json_encode( $args ),
                'timeout' => 30,
            ));

            if ( is_wp_error( $response ) ) {
                throw new Exception( $response->get_error_message() );
            }

            return json_decode( wp_remote_retrieve_body( $response ), true );
        }

        private function verify_webhook( $payload ) {
            // Implement webhook signature verification
            return true;
        }
    }

    // Register gateway
    add_filter( 'woocommerce_payment_gateways', function( $gateways ) {
        $gateways[] = 'WC_Gateway_Custom';
        return $gateways;
    });
});
```

---

## Testing Payments

### Stripe Test Cards

| Card Number | Scenario |
|-------------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Generic decline |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0000 0000 9987` | Lost card |
| `4000 0000 0000 9979` | Stolen card |
| `4000 0027 6000 3184` | Requires 3D Secure |
| `4000 0000 0000 3220` | 3D Secure required, then decline |
| `4000 0000 0000 3063` | 3D Secure required, fails authentication |

Use any future expiry date and any 3-digit CVC.

### PayPal Sandbox

1. Create sandbox accounts at [developer.paypal.com](https://developer.paypal.com/)
2. Use sandbox credentials in WooCommerce
3. Login with sandbox buyer account during checkout

### Testing Checklist

- [ ] Successful payment → Order marked "Processing"
- [ ] Declined card → Clear error message shown
- [ ] 3D Secure flow → Redirect and return work
- [ ] 3D Secure failure → Appropriate error handling
- [ ] Refund from admin → Refund processed
- [ ] Refund from Stripe Dashboard → Order updated via webhook
- [ ] Dispute created → Admin notified
- [ ] Email notifications sent
- [ ] Order notes recorded
- [ ] Transaction IDs stored

---

## Security Best Practices

### 1. Never Log Sensitive Data

```php
// NEVER do this
error_log( 'Card: ' . $_POST['card_number'] );
error_log( print_r( $_POST, true ) ); // May contain card data

// Safe to log
error_log( 'Transaction ID: ' . $transaction_id );
error_log( 'Order ID: ' . $order_id );
```

### 2. Always Verify Webhooks

```php
// Always verify webhook signatures
$signature = $_SERVER['HTTP_STRIPE_SIGNATURE'];
$secret = get_option( 'stripe_webhook_secret' );

// Use constant-time comparison
if ( ! hash_equals( $expected_signature, $received_signature ) ) {
    http_response_code( 400 );
    exit();
}
```

### 3. Require HTTPS

```php
public function is_available() {
    // Require SSL in production
    if ( ! is_ssl() && ! $this->testmode ) {
        return false;
    }
    return parent::is_available();
}
```

### 4. Validate Order Amounts

```php
// In webhook handler - verify amount matches
$webhook_amount = $event['data']['amount'];
$order_amount = $order->get_total() * 100;

if ( abs( $webhook_amount - $order_amount ) > 1 ) {
    // Amount mismatch - potential fraud
    $order->add_order_note( 'Payment amount mismatch detected!' );
    return;
}
```

### 5. Use Idempotency Keys

```php
// Prevent duplicate charges on retries
$idempotency_key = 'order_' . $order_id . '_' . time();

$charge = \Stripe\Charge::create(
    [ /* charge params */ ],
    [ 'idempotency_key' => $idempotency_key ]
);
```

---

## Troubleshooting

### Payment Not Recording

1. Check webhook URL is accessible (not blocked by security plugin)
2. Verify webhook secret matches
3. Check WooCommerce → Status → Logs for errors
4. Verify SSL certificate is valid
5. Check Stripe Dashboard → Webhooks → Recent deliveries

### 3D Secure Not Working

```php
// Ensure return URL is correct
add_filter( 'wc_stripe_payment_intent_args', function( $args, $order ) {
    // Force correct return URL
    $args['return_url'] = add_query_arg(
        'wc-stripe-confirmation',
        '1',
        $order->get_checkout_order_received_url()
    );
    return $args;
}, 10, 2 );
```

### Orders Stuck on "Pending"

1. Webhook not received → Check endpoint URL
2. Webhook failing → Check server logs
3. Payment actually failed → Check Stripe Dashboard
4. JavaScript error → Check browser console

### Duplicate Orders

```php
// Check for existing order before creating
add_action( 'woocommerce_checkout_create_order', function( $order, $data ) {
    $payment_intent_id = WC()->session->get( 'stripe_payment_intent' );

    if ( $payment_intent_id ) {
        $existing = wc_get_orders([
            'meta_key' => '_stripe_intent_id',
            'meta_value' => $payment_intent_id,
            'limit' => 1
        ]);

        if ( ! empty( $existing ) ) {
            throw new Exception( 'Order already exists for this payment.' );
        }
    }
}, 10, 2 );
```

## Further Reading

- [WooCommerce Hooks](./02-woocommerce-hooks.md) — Payment-related hooks
- [Checkout Customization](./04-checkout-customization.md) — Checkout flow modifications
- [WooCommerce Performance](./03-woocommerce-performance.md) — Checkout speed optimization
- [Stripe Documentation](https://stripe.com/docs/payments/accept-a-payment)
- [PayPal Developer](https://developer.paypal.com/docs/checkout/)
- [PCI DSS Requirements](https://www.pcisecuritystandards.org/)
