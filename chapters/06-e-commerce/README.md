# E-commerce with WordPress

A practical guide to building and optimizing online stores with WordPress and WooCommerce.

## Why WooCommerce?

WooCommerce powers over 25% of all online stores on the internet. Not because it's perfect, but because:

- **Free and open-source** - no monthly platform fees
- **Flexible** - from 10 products to 100,000+
- **Ecosystem** - thousands of extensions and integrations
- **WordPress foundation** - leverage familiar concepts

## When WooCommerce is NOT the Right Choice

Be honest with yourself:

| Scenario | Better Alternative |
|----------|-------------------|
| SaaS product with recurring billing | Stripe Billing + custom |
| Marketplace with many sellers | Sharetribe, specialized platform |
| Digital products only | Gumroad, Lemon Squeezy |
| Enterprise with millions of orders | Magento, Shopify Plus |
| Simple checkout for 1-2 products | Stripe Payment Links |

WooCommerce shines when you have physical products, need customization, and want to control your data.

## What You'll Find Here

### [WooCommerce Fundamentals](01-woocommerce-fundamentals.md)
The architecture of WooCommerce - how it stores data, key concepts, and where to look when debugging.

### [WooCommerce Hooks](02-woocommerce-hooks.md)
The most commonly used hooks for customization - from modifying checkout fields to custom product tabs.

### [WooCommerce Performance](03-woocommerce-performance.md)
Store-specific optimizations - why standard WordPress advice isn't enough.

### [Checkout Customization](04-checkout-customization.md)
How to modify the checkout process without breaking payments.

### [Payment Gateways](05-payment-gateways.md)
Integrating Stripe, PayPal and other payment providers. How to create a custom gateway.

### [Shipping Configuration](06-shipping-configuration.md)
Shipping zones, methods, shipping classes. Custom shipping calculations and courier integrations.

### [WooCommerce REST API](07-woocommerce-rest-api.md)
External access to your store - for mobile apps, ERP integrations, headless frontend.

## Important Principles

### 1. Never Modify WooCommerce Directly
Always use hooks. WooCommerce updates frequently and your changes will disappear.

### 2. Test Payments in Sandbox
Stripe, PayPal and others have test modes. Never test with real cards.

### 3. Performance is Critical for Conversions
Every second of delay = 7% fewer conversions. A store with 3+ seconds load time loses customers.

### 4. Security is Doubly Important
The store processes personal data and payments. One breach and the business is at risk.

## Prerequisites

Before continuing, make sure you understand:

- [WordPress Hooks System](../01-plugin-development/02-hooks-system.md)
- [Database Operations](../01-plugin-development/03-database-operations.md)
- Basics of PHP and WordPress development
