# E-commerce SEO

E-commerce SEO is a different game from content SEO. You're optimizing hundreds or thousands of product pages that often share similar descriptions, competing with Amazon and established retailers, and dealing with faceted navigation that can create crawl nightmares. WooCommerce handles the basics, but winning in product search requires deliberate optimization.

## Product Schema Markup

Structured data tells Google exactly what your product is, its price, availability, and reviews. This earns rich snippets in search results — the price, rating stars, and availability badges that dramatically improve click-through rates.

### WooCommerce Default Schema

WooCommerce outputs basic `Product` schema automatically. But it's often incomplete. Check what's rendered:

```
Google Rich Results Test → Enter product URL → See what's detected
```

### Enhanced Product Schema

```php
// Add missing schema properties via filter
add_filter( 'woocommerce_structured_data_product', function( $markup, $product ) {
    // Add brand
    $markup['brand'] = array(
        '@type' => 'Brand',
        'name'  => $product->get_attribute( 'brand' ) ?: get_bloginfo( 'name' ),
    );

    // Add GTIN/EAN if stored in meta
    $gtin = $product->get_meta( '_gtin' );
    if ( $gtin ) {
        $markup['gtin13'] = $gtin;
    }

    // Add return policy
    $markup['hasMerchantReturnPolicy'] = array(
        '@type'                  => 'MerchantReturnPolicy',
        'applicableCountry'      => 'US',
        'returnPolicyCategory'   => 'https://schema.org/MerchantReturnFiniteReturnWindow',
        'merchantReturnDays'     => 30,
        'returnMethod'           => 'https://schema.org/ReturnByMail',
        'returnFees'             => 'https://schema.org/FreeReturn',
    );

    return $markup;
}, 10, 2 );
```

### Schema Properties That Matter

| Property | Impact | How to Add |
|----------|--------|-----------|
| `aggregateRating` | Stars in search results | WooCommerce reviews (enabled by default) |
| `brand` | Product Knowledge Panel | Custom field or attribute |
| `gtin` / `isbn` / `mpn` | Google Shopping eligibility | Product meta field |
| `offers.availability` | "In stock" badge | WooCommerce stock management |
| `offers.priceValidUntil` | Price snippet | Sale end date |
| `review` | Individual review snippets | WooCommerce reviews |
| `shippingDetails` | Shipping info in results | Structured shipping data |

### SEO Plugins and Schema

| Plugin | Schema Handling |
|--------|----------------|
| **Yoast WooCommerce SEO** | Enhanced product schema, breadcrumbs |
| **Rank Math** | Built-in WooCommerce schema, auto-detect |
| **Schema Pro** | Custom schema builder for any post type |

## Product Page Optimization

### Title Tag Formula

```
[Product Name] - [Key Feature/Benefit] | [Brand/Store]
```

Examples:
- "Ceramic Pour-Over Coffee Dripper - Handmade, Dishwasher Safe | CraftBrew"
- "Organic Cotton Baby Blanket - GOTS Certified, 100x140cm | Little Nest"

### Product Description Strategy

| Section | Purpose | SEO Impact |
|---------|---------|-----------|
| Short description | Above-fold summary, key selling points | Meta description source |
| Long description | Full details, use cases, specifications | Main keyword content |
| Specifications table | Technical details, dimensions, materials | Featured snippet potential |
| FAQ section | Common questions about the product | FAQ rich snippet, long-tail keywords |

### Image SEO for Products

| Optimization | How | Impact |
|-------------|-----|--------|
| Descriptive file names | `blue-wool-cardigan-front.jpg` not `IMG_4523.jpg` | Image search ranking |
| Alt text with product name | "Blue merino wool cardigan, front view" | Accessibility + image SEO |
| Multiple angles | Front, back, detail, in-use | Google Images carousel |
| WebP/AVIF format | Convert at upload | Faster loading, better Core Web Vitals |

## Category Page Optimization

Category pages are often more valuable for SEO than individual product pages — they target broader keywords and have more internal link authority.

### Category Page Content

```
Product category pages should include:

1. H1: Category name (optimized for search intent)
2. Intro paragraph (100-200 words, above products)
3. Product grid
4. Extended description below products (300-500 words)
5. FAQ section
6. Related categories
```

### WooCommerce Category Description

WooCommerce provides two description fields per category:

```
Products → Categories → Edit → Description (above products)
Products → Categories → Edit → Description below (requires theme support or plugin)
```

The below-products description is ideal for SEO content that doesn't interfere with shopping.

### Category URL Structure

| Structure | Example | SEO Value |
|-----------|---------|-----------|
| Flat | `/product-category/t-shirts/` | Simpler, less depth |
| Nested | `/product-category/clothing/t-shirts/` | Shows hierarchy |
| Product in category | `/clothing/t-shirts/blue-cotton-tee/` | Context in URL |

WooCommerce default: `/product-category/slug/`. If your store has logical hierarchy, nested categories help both users and search engines understand relationships.

```
WooCommerce → Settings → Permalinks → Product category base
```

## Faceted Navigation SEO

Faceted navigation (filter by color, size, price, brand) creates URL combinations that can explode your index. A store with 100 products, 5 colors, 8 sizes, and 10 brands generates thousands of filter URLs — most with near-duplicate content.

### The Problem

```
/t-shirts/                          ← Main category (index this)
/t-shirts/?color=blue               ← Filtered (maybe index)
/t-shirts/?color=blue&size=m        ← Filtered (don't index)
/t-shirts/?color=blue&size=m&brand=x ← Deep filter (definitely don't index)
```

### Solutions

| Approach | How | Tradeoff |
|----------|-----|----------|
| `noindex` on filtered pages | Meta robots tag | Prevents indexing but Google still crawls |
| Canonical to base category | `rel="canonical"` to unfiltered URL | Consolidates authority |
| Robots.txt block | Disallow filter parameters | Prevents crawling entirely |
| AJAX filtering | No URL change on filter | No indexation risk, but no filter URL sharing |
| Strategic indexing | Index valuable filters, noindex combinations | Complex but optimal |

### Implementation

```php
// Add noindex to filtered WooCommerce pages
add_action( 'wp_head', function() {
    if ( is_product_taxonomy() && ! empty( $_GET ) ) {
        // Any filtered view gets noindex
        echo '<meta name="robots" content="noindex, follow">';
    }
} );

// Or better: canonical to the base category
add_filter( 'woocommerce_product_query_tax_query', function( $tax_query ) {
    // WordPress/Yoast handles canonical automatically for standard taxonomy pages
    // But verify filtered pages point canonical to the unfiltered version
    return $tax_query;
} );
```

## Internal Linking for E-commerce

### Product-to-Product Links

| Link Type | Implementation | SEO Value |
|-----------|---------------|-----------|
| Related products | WooCommerce built-in (by category/tag) | Distributes authority |
| Upsells | Set per product | Guides to higher-value pages |
| Cross-sells | Shown on cart page | Connects product categories |
| "Frequently bought together" | Plugin (e.g., YITH, WPC) | Association signals |
| Recently viewed | WooCommerce widget | User engagement signals |

### Breadcrumbs

Breadcrumbs provide both UX navigation and structured data:

```
Home > Clothing > T-Shirts > Blue Cotton V-Neck
```

WooCommerce has built-in breadcrumbs. For enhanced control:

```php
// Use Yoast breadcrumbs (better schema markup)
if ( function_exists( 'yoast_breadcrumb' ) ) {
    yoast_breadcrumb( '<nav class="breadcrumb">', '</nav>' );
}
```

## Out-of-Stock Product Pages

Don't delete product pages — they may have rankings, backlinks, and traffic.

| Strategy | When to Use |
|----------|------------|
| Keep page, show "Out of Stock" | Product will return |
| Keep page, suggest alternatives | Product discontinued but category exists |
| 301 redirect to replacement | Direct replacement product exists |
| 301 redirect to category | No replacement, category is relevant |
| 410 Gone | Product permanently removed, no relevant alternative |

```php
// Show alternatives on out-of-stock products
add_action( 'woocommerce_single_product_summary', function() {
    global $product;
    if ( ! $product->is_in_stock() ) {
        echo '<div class="out-of-stock-alternatives">';
        echo '<h3>Similar products you might like:</h3>';
        // Display related products
        woocommerce_related_products( array( 'posts_per_page' => 4 ) );
        echo '</div>';
    }
}, 35 );
```

## Review SEO

Product reviews generate unique content, long-tail keywords, and rich snippets.

### Maximizing Review SEO Value

| Practice | Implementation |
|----------|---------------|
| Enable reviews | WooCommerce → Settings → Products → Enable reviews |
| Show aggregate rating | Default in WooCommerce schema |
| Allow photos in reviews | Plugin like JEREZ or WooCommerce Photo Reviews |
| Structured review Q&A | FAQ schema for common questions |

### Review Plugins

| Plugin | Features |
|--------|----------|
| **WooCommerce default** | Basic star ratings, verified buyer badge |
| **Judge.me** | Photo/video reviews, auto-request emails |
| **Yotpo** | Social proof, Q&A, visual marketing |
| **JEREZ** | Lightweight review enhancement |

## Google Merchant Center

For product visibility in Google Shopping:

### Requirements

| Requirement | How to Provide |
|-------------|---------------|
| Product feed | Plugin-generated XML/CSV |
| GTIN/MPN/Brand | Product meta fields |
| Correct pricing | Match website prices |
| Shipping info | Set in Merchant Center or feed |
| Return policy | Structured data or Merchant Center |

### Feed Plugins

| Plugin | Cost |
|--------|------|
| **Google Listings & Ads** (official) | Free |
| **Product Feed PRO for WooCommerce** | Free / $89+ |
| **CTX Feed** | Free / $119+ |
| **JEREZ Feed Manager** | Budget option |

## E-commerce SEO Checklist

- [ ] Product schema complete (brand, GTIN, reviews, availability)
- [ ] Unique product descriptions (not manufacturer copy-paste)
- [ ] Optimized product images with descriptive alt text
- [ ] Category pages have unique intro/description content
- [ ] Faceted navigation handled (noindex or canonical)
- [ ] Breadcrumbs with structured data
- [ ] Out-of-stock pages handled (not 404ing)
- [ ] Internal linking between related products
- [ ] Google Merchant Center feed submitted
- [ ] Review system active with aggregate ratings
- [ ] Product URLs are clean and descriptive

## Further Reading

- [Technical SEO Fundamentals](./01-technical-seo-fundamentals.md) — Core technical SEO
- [XML Sitemaps and Structured Data](./03-xml-sitemaps-and-structured-data.md) — Schema implementation
- [Performance Optimization for SEO](./04-performance-optimization-for-seo.md) — Core Web Vitals impact
- [WooCommerce Performance](../06-e-commerce/03-woocommerce-performance.md) — Store speed optimization
- [Checkout Customization](../06-e-commerce/04-checkout-customization.md) — Conversion optimization
