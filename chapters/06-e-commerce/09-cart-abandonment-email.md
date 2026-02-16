# Cart Abandonment & Email Marketing

Around 70% of online shopping carts are abandoned. That's not a bug—it's how people shop online. They browse, compare, get distracted, come back later (or don't). The stores that recover even 5-10% of abandoned carts see significant revenue gains.

## Why Carts Get Abandoned

| Reason | Frequency | What You Can Fix |
|--------|-----------|-----------------|
| Just browsing / not ready | ~58% | Better retargeting, save cart |
| Unexpected shipping costs | ~49% | Show shipping earlier, free shipping threshold |
| Account creation required | ~24% | Guest checkout |
| Slow delivery | ~22% | Clear delivery estimates |
| Complicated checkout | ~18% | Fewer fields, progress indicator |
| Didn't trust site with payment | ~17% | Trust badges, SSL, known payment providers |
| Total cost too high | ~16% | Price transparency, discount incentives |

Source: Baymard Institute aggregate studies.

## Cart Abandonment Recovery

### How It Works

```
1. Customer adds items to cart
2. Customer provides email (checkout start, newsletter, account)
3. Customer leaves without completing purchase
4. Wait period (30 min - 1 hour)
5. Send first recovery email
6. If no conversion: send second email (24 hours)
7. If no conversion: send final email with incentive (48-72 hours)
```

The critical requirement: you need the customer's email. Without it, recovery emails are impossible. This is why many stores ask for email as the first checkout field.

### Plugin Options

| Plugin | Cost | Features |
|--------|------|----------|
| **AutomateWoo** | $149/year | Full automation suite, cart recovery, win-back, wishlists |
| **Retainful** | Free/paid | Cart recovery + next-order coupons |
| **CartFlows** | Free/paid | Funnel builder + cart abandonment |
| **WooCommerce Cart Abandonment Recovery** (CartFlows) | Free | Basic email recovery |
| **Metorik** | $20+/month | Analytics-first approach with email recovery |
| **Klaviyo** | Free to $20+/month | Full email marketing with WooCommerce integration |
| **Mailchimp for WooCommerce** | Free | Basic automation, large free tier |

### Recovery Email Sequence

**Email 1: Reminder (30-60 minutes after abandonment)**

Subject: "You left something in your cart"

Content:
- Show cart contents with images
- Direct link back to their cart (pre-populated)
- No discount yet—many customers just got distracted

**Email 2: Urgency (24 hours)**

Subject: "Your cart is about to expire"

Content:
- Cart contents reminder
- Stock availability warning (if applicable)
- Social proof (reviews, purchase count)
- Still no discount

**Email 3: Incentive (48-72 hours)**

Subject: "Here's 10% off to complete your order"

Content:
- Cart contents
- Discount code (auto-applied via link)
- Limited time on the offer
- Customer support contact

### Recovery Email Best Practices

| Practice | Why |
|----------|-----|
| Include product images | Visual reminder of what they wanted |
| Single CTA button | "Complete Your Order" — don't distract |
| Pre-populate the cart | Link should restore their exact cart |
| Mobile-optimized | 50%+ of emails opened on mobile |
| Plain text fallback | Some email clients block HTML |
| Unsubscribe option | Required by law (CAN-SPAM, GDPR) |

### Measuring Recovery Performance

| Metric | Good | Great |
|--------|------|-------|
| Recovery email open rate | 40%+ | 50%+ |
| Recovery email click rate | 10%+ | 15%+ |
| Cart recovery rate | 5%+ | 10%+ |
| Revenue recovered per email | Track this | Varies wildly |

## Email Marketing Integration

Beyond cart recovery, email drives repeat purchases.

### Key Email Flows for E-commerce

| Flow | Trigger | Purpose |
|------|---------|---------|
| **Welcome series** | Account creation | Introduce brand, first purchase incentive |
| **Post-purchase** | Order completed | Thank you, cross-sell, review request |
| **Cart abandonment** | Cart abandoned | Recover the sale |
| **Win-back** | No purchase in 60+ days | Re-engage inactive customers |
| **Browse abandonment** | Viewed products, didn't add to cart | Softer nudge than cart recovery |
| **Back-in-stock** | Product restocked | Notify interested customers |
| **Birthday/anniversary** | Customer's birthday | Personalized discount |

### Platform Comparison

| Platform | WooCommerce Integration | Automation | Free Tier |
|----------|------------------------|-----------|-----------|
| **Klaviyo** | Excellent (native plugin) | Advanced, visual builder | Up to 250 contacts |
| **Mailchimp** | Good (official plugin) | Basic-medium | Up to 500 contacts |
| **ActiveCampaign** | Good (via plugin) | Advanced, CRM included | No free tier |
| **Brevo** (ex-Sendinblue) | Good | Medium | 300 emails/day |
| **ConvertKit** | Basic | Creator-focused | Up to 1000 subscribers |
| **AutomateWoo** | Native (it IS WooCommerce) | WooCommerce-specific | No (paid plugin) |

**For most WooCommerce stores:** Start with Mailchimp (free, easy) or Klaviyo (better WooCommerce integration, more powerful automation).

### WooCommerce Data for Email Segmentation

WooCommerce provides rich data for email targeting:

| Segment | Criteria | Use |
|---------|----------|-----|
| High-value customers | Total spend > $500 | VIP offers, early access |
| New customers | First order in last 30 days | Onboarding series |
| At-risk customers | No order in 60+ days | Win-back campaign |
| Repeat buyers | 3+ orders | Loyalty rewards |
| Category buyers | Purchased from specific category | Related product recommendations |
| Average order value | AOV > $100 | Upsell opportunities |

### Transactional vs Marketing Email

| Type | Examples | Consent Needed? | Service |
|------|----------|-----------------|---------|
| **Transactional** | Order confirmation, shipping, password reset | No (required for service) | WordPress SMTP |
| **Marketing** | Newsletters, promotions, cart recovery | Yes (explicit opt-in) | Email platform |

Keep these separate. Transactional emails through your SMTP provider, marketing emails through your email platform. Mixing them risks deliverability—if your marketing emails get marked as spam, your order confirmations suffer too.

## Checkout Optimization for Recovery

### Capture Email Early

```php
// Move email field to the top of checkout
add_filter( 'woocommerce_checkout_fields', function( $fields ) {
    $fields['billing']['billing_email']['priority'] = 5; // First field
    return $fields;
} );
```

Once you have the email, cart recovery is possible even if the customer doesn't complete checkout.

### Exit-Intent Popups

Show a popup when the cursor moves toward the browser's close button:

| Plugin | Purpose |
|--------|---------|
| **OptinMonster** | Full exit-intent platform |
| **Elementor Popup Builder** | If already using Elementor |
| **Convert Pro** | Lightweight popup builder |

Use sparingly. A well-timed "Save 10% if you complete your order now" can work. An aggressive popup on every page annoys everyone.

### Persistent Cart

Save cart contents for logged-in users so they can return later:

WooCommerce does this by default for logged-in users via the `_woocommerce_persistent_cart_*` user meta. For guests, consider saving cart data in a cookie or session that persists for 30 days.

## Further Reading

- [Checkout Customization](./04-checkout-customization.md) — Optimizing checkout flow
- [WooCommerce Performance](./03-woocommerce-performance.md) — Cart fragments and caching
- [Email Deliverability](../02-maintenance/06-email-deliverability.md) — Ensuring emails arrive
- [Analytics](../02-maintenance/05-analytics.md) — Tracking conversion funnels
