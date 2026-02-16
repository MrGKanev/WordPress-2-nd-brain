# B2B E-commerce

B2B (business-to-business) selling in WooCommerce is fundamentally different from B2C. Your buyers are companies, not individuals. They expect negotiated pricing, bulk discounts, purchase orders, and credit terms. WooCommerce can handle B2B, but it needs extensions — the core is built for consumer retail.

## B2B vs. B2C Differences

| Aspect | B2C | B2B |
|--------|-----|-----|
| Buyer | Individual consumer | Company / purchasing department |
| Decision process | Quick, emotional | Committee, rational |
| Pricing | Fixed, displayed publicly | Negotiated, often hidden |
| Payment | Card at checkout | Net-30/60/90 invoicing |
| Order size | Small, frequent | Large, periodic |
| Product catalog | Open to all | May require login to view |
| Checkout | Simple, guest allowed | Complex, approval workflows |
| Reordering | Browse and add | "Reorder previous" button |
| Quotes | Rarely needed | Often required before purchase |

## Wholesale Pricing

### Plugin Options

| Plugin | Approach | Cost |
|--------|----------|------|
| **Wholesale Suite** (Wholesale Prices) | Role-based wholesale pricing | Free / $149+ |
| **B2BKing** | Full B2B suite | $139 (lifetime) |
| **WooCommerce B2B** | Comprehensive B2B features | $129/year |
| **YITH WooCommerce Role-Based Prices** | Price per role | $99/year |
| **Discount Rules for WooCommerce** | Flexible pricing rules | Free / $69+ |

### Wholesale Suite (Most Popular)

Wholesale Suite is the most common B2B solution for WooCommerce:

1. **Wholesale Prices** (free) — Add wholesale prices per product
2. **Wholesale Order Form** (premium) — Bulk order page
3. **Wholesale Lead Capture** (premium) — Registration and approval

```
How it works:
1. Create a "Wholesale Customer" role
2. Set wholesale prices on each product
3. Wholesale customers see their prices when logged in
4. Regular customers see retail prices
```

### Tiered Pricing

Pricing that changes based on quantity:

| Quantity | Price Per Unit |
|----------|---------------|
| 1-9 | $10.00 |
| 10-49 | $8.50 |
| 50-99 | $7.00 |
| 100+ | $5.50 |

```php
// Simple tiered pricing via filter
add_filter( 'woocommerce_product_get_price', function( $price, $product ) {
    if ( ! is_user_logged_in() || ! WC()->cart ) {
        return $price;
    }

    $cart_qty = 0;
    foreach ( WC()->cart->get_cart() as $cart_item ) {
        if ( $cart_item['product_id'] === $product->get_id() ) {
            $cart_qty = $cart_item['quantity'];
            break;
        }
    }

    // Apply tier pricing
    if ( $cart_qty >= 100 ) return $price * 0.55;
    if ( $cart_qty >= 50 ) return $price * 0.70;
    if ( $cart_qty >= 10 ) return $price * 0.85;

    return $price;
}, 10, 2 );
```

For production use, a dedicated plugin handles edge cases (cart recalculation, display, admin UI) far better than custom code.

## Quote / Request for Quote (RFQ)

Many B2B transactions start with a quote, not a cart:

| Plugin | Features | Cost |
|--------|----------|------|
| **YITH Request a Quote** | Replace "Add to Cart" with "Request Quote" | $99/year |
| **B2BKing** | Quote system built into B2B suite | $139 (lifetime) |
| **WooCommerce Request a Quote** (Addify) | Quote management, PDF quotes | $79 |

### Quote Workflow

```
1. Customer browses catalog → Adds items to quote list
2. Submits quote request
3. Admin receives notification
4. Admin reviews, adjusts pricing, sends quote
5. Customer reviews quote → Accepts or negotiates
6. Accepted quote converts to order
7. Customer pays via agreed terms (invoice, PO, etc.)
```

## Customer Groups and Roles

### WordPress Roles for B2B

```php
// Register custom B2B roles
add_action( 'init', function() {
    add_role( 'wholesale_bronze', 'Wholesale Bronze', array(
        'read' => true,
        'edit_posts' => false,
    ) );
    add_role( 'wholesale_silver', 'Wholesale Silver', array(
        'read' => true,
        'edit_posts' => false,
    ) );
    add_role( 'wholesale_gold', 'Wholesale Gold', array(
        'read' => true,
        'edit_posts' => false,
    ) );
} );
```

Each role can have different pricing, minimum order amounts, and payment terms.

### Customer Registration and Approval

B2B stores typically require approved registration:

```
Public registration form → Admin review → Approve/Reject → Role assignment
```

| Plugin | Approval Features |
|--------|------------------|
| **Wholesale Lead Capture** | Registration form, approval workflow |
| **B2BKing** | Custom registration fields, automatic/manual approval |
| **New User Approve** | Simple approval for any registration |
| **WooCommerce Registration** (Developer) | Custom fields on registration |

## Catalog Visibility

B2B stores often need to hide prices or products from non-logged-in visitors:

### Options

| Behavior | Plugin/Method |
|----------|-------------|
| Hide prices from guests | B2BKing, Catalog Visibility Options |
| Hide entire catalog from guests | B2BKing, WooCommerce Private Store |
| Show different catalogs per role | B2BKing, role-based category access |
| Replace "Add to Cart" with "Login to See Prices" | Custom or plugin |

### Simple Price Hiding

```php
// Hide prices for non-logged-in users
add_filter( 'woocommerce_get_price_html', function( $price, $product ) {
    if ( ! is_user_logged_in() ) {
        return '<a href="' . wp_login_url( get_permalink() ) . '">Login for pricing</a>';
    }
    return $price;
}, 10, 2 );

// Remove add-to-cart for guests
add_action( 'woocommerce_single_product_summary', function() {
    if ( ! is_user_logged_in() ) {
        remove_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_add_to_cart', 30 );
    }
}, 1 );
```

## Payment Terms

B2B buyers expect flexible payment options beyond credit cards:

### Invoice / Net Terms

| Plugin | Features |
|--------|----------|
| **WooCommerce PDF Invoices & Packing Slips** | Generate PDF invoices |
| **B2BKing** | Net 30/60/90 payment, credit limits |
| **WooCommerce Purchase Order Gateway** | Accept PO numbers |
| **YITH WooCommerce PDF Invoice** | Customizable invoice templates |

### Purchase Order (PO) Gateway

A simple payment gateway that accepts PO numbers:

```
Checkout → Customer enters PO number → Order placed as "On Hold"
→ Admin fulfills → Sends invoice → Customer pays on terms
```

B2BKing and several standalone plugins add PO number fields to checkout.

## Order Management for B2B

### Bulk Ordering

Standard WooCommerce product pages are slow for B2B buyers ordering 50+ SKUs. An order form is essential:

| Plugin | Type |
|--------|------|
| **Wholesale Order Form** (Wholesale Suite) | Spreadsheet-style ordering |
| **WooCommerce Product Table** | Tabular product list with quantities |
| **B2BKing** | Built-in order form |

### Reordering

B2B customers often repeat orders. Make it easy:

```php
// Add "Reorder" button to order history
add_filter( 'woocommerce_my_account_my_orders_actions', function( $actions, $order ) {
    $actions['reorder'] = array(
        'url'  => wp_nonce_url(
            add_query_arg( 'order_again', $order->get_id() ),
            'woocommerce-order_again'
        ),
        'name' => __( 'Reorder', 'textdomain' ),
    );
    return $actions;
}, 10, 2 );
```

WooCommerce has built-in "Order Again" functionality. Ensure it's enabled in settings.

### Minimum Order Requirements

```php
// Set minimum order for wholesale customers
add_action( 'woocommerce_check_cart_items', function() {
    if ( current_user_can( 'wholesale_customer' ) ) {
        $minimum = 100;
        if ( WC()->cart->get_subtotal() < $minimum ) {
            wc_add_notice(
                sprintf( 'Wholesale orders require a minimum of %s.', wc_price( $minimum ) ),
                'error'
            );
        }
    }
} );
```

## B2B-Specific Features Comparison

| Feature | Wholesale Suite | B2BKing | Custom Code |
|---------|----------------|---------|-------------|
| Role-based pricing | Yes | Yes | Possible |
| Tiered/quantity pricing | Premium | Yes | Complex |
| Quote system | No (separate plugin) | Yes | Very complex |
| Catalog visibility | No (separate plugin) | Yes | Possible |
| Registration approval | Premium | Yes | Possible |
| Invoice payment | No | Yes | Possible |
| Tax exemption by role | Premium | Yes | Possible |
| Bulk order form | Premium | Yes | Complex |
| Minimum order amounts | No | Yes | Simple |

## Tax for B2B

B2B transactions often have different tax treatment:

- **EU**: B2B sales with valid VAT number = 0% (reverse charge)
- **US**: Resale certificates exempt from sales tax
- **UK**: Reverse charge mechanism for some services

See [Tax Compliance](./10-tax-compliance.md) for implementation details.

## Further Reading

- [WooCommerce Hooks](./02-woocommerce-hooks.md) — Customizing store behavior
- [Checkout Customization](./04-checkout-customization.md) — B2B checkout modifications
- [Payment Gateways](./05-payment-gateways.md) — Payment integration
- [Tax Compliance](./10-tax-compliance.md) — B2B tax handling
- [Cart Abandonment & Email](./09-cart-abandonment-email.md) — B2B follow-up strategies
