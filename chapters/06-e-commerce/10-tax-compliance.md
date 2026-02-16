# Tax Compliance

Tax is the part of e-commerce nobody enjoys but everybody needs. Get it wrong and you're either overcharging customers (lost sales) or undercharging them (you owe the difference). The complexity multiplies when you sell across borders—different rates, different rules, different reporting requirements.

## Tax Fundamentals for WooCommerce

### How WooCommerce Calculates Tax

WooCommerce uses tax classes and tax rates:

```
Product has a Tax Class (Standard, Reduced, Zero)
    ↓
Customer's location is determined (billing or shipping address)
    ↓
Tax rate matched: Class + Location = Rate
    ↓
Tax calculated and displayed
```

### Basic Tax Configuration

```
WooCommerce → Settings → Tax
```

| Setting | Options | Recommendation |
|---------|---------|---------------|
| Prices entered with tax | Including / Excluding | **Excluding** for B2B, **Including** for B2C in EU |
| Calculate tax based on | Customer shipping/billing address, Shop base | **Customer shipping address** for physical goods |
| Display prices in shop | Including / Excluding tax | Match your region's convention |
| Display prices during cart/checkout | Including / Excluding tax | Match shop display |
| Tax rounding | At subtotal / Per line | **At subtotal** (fewer rounding issues) |

### Tax Classes

| Class | Default Rate | Use For |
|-------|-------------|---------|
| **Standard** | Country default (e.g., 20% UK, 19% DE) | Most products |
| **Reduced rate** | Lower rate (e.g., 5% UK) | Food, children's clothing (varies by country) |
| **Zero rate** | 0% | Exports, B2B with valid VAT number |

You can create custom tax classes for specific product categories.

## US Sales Tax

US sales tax is complicated because it's governed at state (and sometimes city/county) level, with over 12,000 tax jurisdictions.

### Nexus

You only need to collect sales tax in states where you have "nexus"—a significant presence:

| Nexus Type | Examples |
|-----------|---------|
| **Physical** | Office, warehouse, employees in the state |
| **Economic** | $100K+ in sales or 200+ transactions in the state (varies) |
| **Marketplace** | Selling on Amazon/eBay (marketplace handles tax) |

After the 2018 Supreme Court ruling (*South Dakota v. Wayfair*), most states can require collection based on economic nexus alone.

### Automation Options

Manual tax rates for the US are impractical. Use an automated service:

| Service | Cost | Integration |
|---------|------|------------|
| **WooCommerce Tax** (powered by Jetpack) | Free | Built into WooCommerce |
| **TaxJar** | From $19/month | WooCommerce plugin, auto-filing |
| **Avalara AvaTax** | Custom pricing | Enterprise, auto-calculation and filing |
| **TaxCloud** | Free (for basic) | API-based, supports exemptions |

**WooCommerce Tax** is free and handles rate calculation automatically via Jetpack's tax API. It's sufficient for most small-medium US stores. TaxJar adds automated filing and reporting.

## EU VAT

### How EU VAT Works

| Scenario | Rule |
|----------|------|
| **Sell physical goods within your country** | Charge your country's VAT rate |
| **Sell physical goods to EU consumers** | Charge your country's rate (under €10,000 threshold) |
| **Sell physical goods above threshold** | Register for OSS, charge customer's country rate |
| **Sell digital products to EU consumers** | Always charge customer's country rate (no threshold) |
| **Sell to EU businesses with valid VAT number** | 0% (reverse charge mechanism) |

### One-Stop Shop (OSS)

Since July 2021, the EU OSS scheme simplifies VAT for cross-border sellers:

- Register in one EU country
- Report all EU sales through that country
- Pay all VAT through a single return

Without OSS, you'd need to register in every EU country where you have customers.

### VAT Rate Table (Common Rates)

| Country | Standard | Reduced | Super-Reduced |
|---------|----------|---------|---------------|
| Germany | 19% | 7% | — |
| France | 20% | 5.5% / 10% | 2.1% |
| Netherlands | 21% | 9% | — |
| Spain | 21% | 10% | 4% |
| Italy | 22% | 5% / 10% | 4% |
| Poland | 23% | 5% / 8% | — |
| Ireland | 23% | 9% / 13.5% | 4.8% |

These rates change. Don't hardcode them—use an automated solution.

### VAT Number Validation

For B2B sales, validate the customer's VAT number against the EU VIES database:

| Plugin | What It Does |
|--------|-------------|
| **WooCommerce EU VAT Number** | Official extension, VIES validation, auto-exemption |
| **EU/UK VAT Manager** | VIES + HMRC validation |
| **Germanized for WooCommerce** | Full German compliance including VAT |
| [EU VAT for WP](https://openwpclub.com/plugins/eu-vat-wp/) | Lightweight VAT validation |

### Digital Products and MOSS/OSS

Digital products (downloads, SaaS, streaming) have stricter rules:

- **No threshold** — You must charge the customer's country VAT rate from the first sale
- **Two pieces of evidence** — You need two non-contradictory pieces of evidence for the customer's location (IP address + billing address, for example)
- **Keep records** — Retain location evidence for 10 years

## UK VAT (Post-Brexit)

Since Brexit, UK VAT is separate from EU:

| Scenario | Rule |
|----------|------|
| UK business → UK customer | Charge 20% VAT |
| UK business → EU customer (physical, under threshold) | No UK VAT, customer pays import VAT |
| EU business → UK consumer (physical, under £135) | Register for UK VAT, charge at point of sale |
| Digital products → UK consumer | Charge 20% UK VAT |

## WooCommerce Tax Configuration

### Manual Rate Setup

For simple stores with few tax jurisdictions:

```
WooCommerce → Settings → Tax → Standard rates → Insert row
```

| Field | Example |
|-------|---------|
| Country code | DE |
| State code | * (all states) |
| Postcode | * |
| City | * |
| Rate % | 19 |
| Tax name | VAT |
| Priority | 1 |
| Compound | No |
| Shipping | Yes |

### Tax Exemptions

```php
// Exempt specific customer roles from tax
add_filter( 'woocommerce_customer_is_vat_exempt', function( $exempt ) {
    if ( current_user_can( 'wholesale_customer' ) ) {
        return true;
    }
    return $exempt;
} );
```

### Tax Display Customization

```php
// Show tax-inclusive prices in shop, exclusive in cart
add_filter( 'woocommerce_get_price_suffix', function( $suffix, $product ) {
    if ( wc_tax_enabled() ) {
        $suffix = ' <small class="tax-note">' . __( 'incl. VAT', 'textdomain' ) . '</small>';
    }
    return $suffix;
}, 10, 2 );
```

## Tax Reporting

### Built-in WooCommerce Reports

```
WooCommerce → Reports → Taxes → Taxes by date / Taxes by code
```

Shows total tax collected per rate. Useful for basic filing.

### For Automated Filing

| Service | Filing Support | Regions |
|---------|---------------|---------|
| **TaxJar** | AutoFile for US states | US |
| **Avalara** | Managed returns | US, EU, global |
| **Taxdoo** | EU OSS filing | EU |
| **SimplyVAT** | EU VAT registration and filing | EU |

## Tax Compliance Checklist

- [ ] Tax enabled in WooCommerce settings
- [ ] Tax rates configured (automated or manual)
- [ ] Correct tax class assigned to each product
- [ ] Tax display matches regional convention (incl/excl)
- [ ] Invoices show tax breakdown (required in EU)
- [ ] VAT number validation for B2B (if selling in EU)
- [ ] Digital product tax rules applied (if selling digital)
- [ ] Tax reporting exported for accountant/filing
- [ ] Nexus obligations reviewed quarterly (US)
- [ ] Tax rates updated when regulations change

## Further Reading

- [Payment Gateways](./05-payment-gateways.md) — Payment processing and tax interaction
- [Subscriptions & Digital Products](./08-subscriptions-digital.md) — Digital product tax implications
- [GDPR Implementation](../03-security/04-gdpr-implementation.md) — Data requirements for tax records
- [EU One-Stop Shop](https://ec.europa.eu/taxation_customs/business/vat/oss_en) — Official EU OSS information
