# Subscriptions & Digital Products

Physical products are straightforward—ship a box, done. Subscriptions and digital products have different rules: recurring billing, license management, download delivery, access control. WooCommerce handles these through extensions, each with their own patterns and gotchas.

## Subscriptions

### When You Need Subscriptions

- SaaS with monthly/yearly plans
- Membership sites with recurring access
- Subscription boxes (physical products on a schedule)
- Maintenance contracts or retainers
- Magazine/newspaper digital access

### WooCommerce Subscriptions

The official extension from Woo. It's expensive ($239/year) but mature and well-integrated.

**What it provides:**
- Recurring payment processing via Stripe, PayPal, and others
- Subscription management in My Account
- Proration for plan changes
- Suspension, cancellation, and reactivation
- Renewal emails and retry logic for failed payments

**Key concepts:**

| Concept | What It Means |
|---------|--------------|
| **Trial period** | Free access before first billing |
| **Sign-up fee** | One-time fee on first payment |
| **Synchronized renewals** | All subscriptions renew on the same date |
| **Proration** | Adjusting charges when plan changes mid-cycle |
| **Failed payment retry** | Automatic retry schedule for declined cards |

### Alternatives to WooCommerce Subscriptions

| Plugin | Cost | Best For |
|--------|------|----------|
| **YITH WooCommerce Subscription** | $149/year | Simpler subscription needs |
| **Subscriptions for WooCommerce** (WebToffee) | $99/year | Budget-conscious stores |
| **SUMO Subscriptions** | $49 (lifetime) | One-time purchase preference |
| **Stripe Billing** (direct) | Free + Stripe fees | SaaS with custom frontend |

### Subscription Performance Impact

Subscriptions add complexity to WooCommerce:

- Renewal processing runs via Action Scheduler (background)
- Each subscription is a separate post type (`shop_subscription`)
- Status checks on every My Account page load
- Failed payment retry logic runs on cron

**Mitigations:**
- Enable HPOS for subscription order storage
- Run Action Scheduler via system cron, not HTTP
- Keep subscriptions table indexed (WooCommerce Subscriptions handles this)

### Payment Gateway Requirements

Not all gateways support subscriptions:

| Gateway | Recurring Support | Token Storage |
|---------|------------------|---------------|
| **Stripe** | Full | Yes (on Stripe's servers) |
| **PayPal** | Full (Reference Transactions) | Yes |
| **Square** | Limited | Yes |
| **Mollie** | Full | Yes |
| **Bank transfer** | No (manual renewals only) | N/A |

The gateway must support **tokenization**—storing card details so future charges can be made without the customer re-entering their card.

### Failed Payment Handling

Cards expire, get replaced, or have insufficient funds. Your retry strategy determines whether you lose the customer or recover:

```
Day 0: Payment fails
Day 1: First retry + email to customer
Day 3: Second retry + urgent email
Day 5: Third retry + final warning
Day 7: Subscription suspended
Day 14: Subscription cancelled (optional)
```

WooCommerce Subscriptions handles this automatically. Configure in:
```
WooCommerce → Settings → Subscriptions → Failed Payment Retry Rules
```

## Digital Products

### Types of Digital Products

| Type | Delivery Method | Access Control |
|------|----------------|---------------|
| **Downloadable files** | Direct download link | Time-limited or count-limited URLs |
| **Software licenses** | License key + download | Key validation against server |
| **Online courses** | Access to content | Role-based or membership gating |
| **Digital services** | API access | API key provisioning |

### WooCommerce Downloadable Products

Built into WooCommerce core—no extension needed for basic file delivery.

**Setting up a downloadable product:**

1. Create a product
2. Under Product Data, check "Virtual" (no shipping) and "Downloadable"
3. Add files with name and URL
4. Set download limit and expiry

**Security settings:**

```
WooCommerce → Settings → Products → Downloadable products
```

| Setting | Recommendation | Why |
|---------|---------------|-----|
| File download method | Force downloads | Prevents hotlinking |
| Access restriction | Grant after payment | Don't deliver before money clears |
| Download limit | 3-5 per file | Prevents abuse while allowing re-downloads |
| Download expiry | 30-365 days | Balance convenience with protection |

### Protecting Download URLs

WooCommerce generates unique download URLs per order, but additional protection helps:

```php
// Prevent directory browsing of uploads
// Add to wp-content/uploads/woocommerce_uploads/.htaccess
deny from all
```

```php
// wp-config.php — use a non-public directory for downloads
define( 'WOOCOMMERCE_UPLOADS_DIR', '/path/outside/webroot/woo-downloads' );
```

### Software Licensing

For selling software (WordPress plugins, desktop apps, SaaS access):

| Plugin | Purpose | Best For |
|--------|---------|----------|
| **Software License Manager** | License key generation and validation | WordPress plugin developers |
| **WooCommerce API Manager** | Full API licensing with versions | Software products with updates |
| **Easy Digital Downloads** | Complete digital store | If you don't need physical products |
| **Freemius** | Full platform (licensing, deployment, analytics) | WordPress plugin/theme businesses |

### Easy Digital Downloads vs WooCommerce

If you only sell digital products, consider EDD instead of WooCommerce:

| Feature | WooCommerce | Easy Digital Downloads |
|---------|-------------|----------------------|
| Physical products | Yes | No (add-on only) |
| Digital focus | Add-on | Core feature |
| Performance | Heavier | Lighter for digital-only |
| Licensing system | Extension needed | Built-in (with extension) |
| Software updates | Extension needed | Built-in (with extension) |
| Ecosystem | Massive | Smaller but focused |

**Use WooCommerce when:** You sell both physical and digital, or already have a WooCommerce store.

**Use EDD when:** Digital-only products, especially software.

## Membership Sites

When access itself is the product (rather than a downloadable file):

### Plugin Options

| Plugin | Approach | Best For |
|--------|----------|----------|
| **MemberPress** | All-in-one membership | Course creators, content sites |
| **Restrict Content Pro** | Lightweight access control | Simple membership tiers |
| **WooCommerce Memberships** | WooCommerce-integrated | Stores adding member-only content |
| **Paid Memberships Pro** | Flexible, free core | Budget-conscious sites |
| **LearnDash** | LMS-focused | Online courses with quizzes/certificates |

### Access Control Patterns

```php
// Check if user has active membership
if ( wc_memberships_is_user_active_member( get_current_user_id(), 'premium' ) ) {
    // Show premium content
} else {
    // Show upgrade prompt
}
```

For non-WooCommerce solutions:

```php
// Role-based content restriction (works with any membership plugin)
if ( current_user_can( 'access_premium_content' ) ) {
    the_content();
} else {
    echo '<p>This content is for premium members. <a href="/pricing">Upgrade now</a>.</p>';
}
```

## Tax Implications for Digital Products

Digital products have specific tax rules, especially in the EU:

| Region | Rule |
|--------|------|
| **EU** | VAT charged at customer's country rate (not seller's) |
| **US** | Sales tax varies by state; many states now tax digital goods |
| **UK** | 20% VAT on digital products |
| **Australia** | 10% GST on digital products sold to AU consumers |

See [Tax Compliance](./10-tax-compliance.md) for implementation details.

## Further Reading

- [Payment Gateways](./05-payment-gateways.md) — Gateway setup and tokenization
- [Checkout Customization](./04-checkout-customization.md) — Modifying subscription checkout
- [WooCommerce Performance](./03-woocommerce-performance.md) — Handling subscription cron load
- [Tax Compliance](./10-tax-compliance.md) — Digital product taxation
