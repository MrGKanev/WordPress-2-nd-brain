# XML Sitemaps and Structured Data

XML sitemaps help search engines discover your content. Structured data helps them understand it. Together, they form the foundation of technical SEO communication with search engines.

## XML Sitemaps

### How WordPress Sitemaps Work

Since WordPress 5.5, core includes a native XML sitemap at `/wp-sitemap.xml`. This sitemap is actually a **sitemap index** that references multiple child sitemaps:

```
/wp-sitemap.xml              → Main index
├── /wp-sitemap-posts-post-1.xml    → Posts
├── /wp-sitemap-posts-page-1.xml    → Pages
├── /wp-sitemap-taxonomies-category-1.xml → Categories
├── /wp-sitemap-taxonomies-post_tag-1.xml → Tags
└── /wp-sitemap-users-1.xml         → Author archives
```

Each child sitemap contains up to 2,000 URLs by default.

### Default Sitemap Limitations

The native WordPress sitemap is basic. It lacks:

- **Priority and change frequency** — All URLs treated equally
- **Image sitemaps** — No image URL inclusion
- **Video sitemaps** — No video metadata
- **News sitemaps** — Required for Google News inclusion
- **Last modified dates** — Only shows current date, not actual modification
- **Exclusion controls** — No easy way to exclude specific posts/pages

For most sites, an SEO plugin provides better sitemap functionality.

### Customizing Native Sitemaps

If you prefer the native sitemap, you can customize it with filters:

```php
// Remove users from sitemap (security/privacy)
add_filter('wp_sitemaps_add_provider', function($provider, $name) {
    if ($name === 'users') {
        return false;
    }
    return $provider;
}, 10, 2);

// Exclude specific post types
add_filter('wp_sitemaps_post_types', function($post_types) {
    unset($post_types['attachment']);
    unset($post_types['custom_private_type']);
    return $post_types;
});

// Exclude specific taxonomies
add_filter('wp_sitemaps_taxonomies', function($taxonomies) {
    unset($post_types['post_format']);
    return $taxonomies;
});

// Add custom URLs to sitemap
add_filter('wp_sitemaps_posts_query_args', function($args, $post_type) {
    if ($post_type === 'post') {
        $args['post_status'] = 'publish';
        $args['orderby'] = 'modified';
    }
    return $args;
}, 10, 2);
```

### Disabling Native Sitemaps

When using an SEO plugin, disable the native sitemap to avoid duplicates:

```php
// Completely disable WordPress sitemaps
add_filter('wp_sitemaps_enabled', '__return_false');
```

Most SEO plugins (Yoast, Rank Math, SEOPress) do this automatically.

### SEO Plugin Sitemaps Comparison

| Feature | WordPress Core | Yoast SEO | Rank Math |
|---------|---------------|-----------|-----------|
| Image sitemap | ❌ | ✅ | ✅ |
| Video sitemap | ❌ | Premium | ✅ |
| News sitemap | ❌ | Premium | ✅ |
| Last modified | Basic | ✅ | ✅ |
| Exclude posts | Via code | ✅ UI | ✅ UI |
| Priority/frequency | ❌ | ❌ (deprecated) | ❌ (deprecated) |
| Styling (XSL) | ❌ | ✅ | ✅ |

**Note:** Google ignores priority and changefreq attributes, so their absence is not a concern.

### Sitemap Best Practices

1. **Submit to Search Console** — Don't just create it, submit it
2. **Keep URLs under 50,000** — Split into multiple sitemaps if needed
3. **Only include indexable URLs** — No noindex, redirects, or 404s
4. **Update regularly** — Trigger regeneration after content changes
5. **Monitor in Search Console** — Check for errors and coverage

### Image Sitemaps

Image sitemaps help Google discover images that might not be found through normal crawling:

```xml
<url>
  <loc>https://example.com/sample-page/</loc>
  <image:image>
    <image:loc>https://example.com/wp-content/uploads/photo.jpg</image:loc>
    <image:title>Descriptive image title</image:title>
    <image:caption>Image caption with context</image:caption>
  </image:image>
</url>
```

Most SEO plugins include images automatically. For custom implementation, use the `wp_sitemaps_posts_entry` filter.

---

## Structured Data (Schema.org)

Structured data uses a standardized vocabulary (Schema.org) to describe your content in a way search engines understand. This enables **rich results** — enhanced search listings with stars, prices, FAQs, and more.

### How Structured Data Works

Search engines parse structured data from your HTML to understand:

- **What type of content** this is (Article, Product, Recipe, etc.)
- **Key attributes** (author, price, rating, date, etc.)
- **Relationships** between entities (author wrote article, business has location)

### Implementation Formats

Three formats exist for adding structured data:

| Format | Pros | Cons | Recommended |
|--------|------|------|-------------|
| **JSON-LD** | Clean, separate from HTML, easy to manage | Requires script tag | ✅ Yes |
| **Microdata** | Inline with HTML | Messy, hard to maintain | ❌ No |
| **RDFa** | Flexible | Complex syntax | ❌ No |

**Google recommends JSON-LD.** It's cleaner and doesn't mix with your HTML structure.

### JSON-LD Basics

JSON-LD is added in a `<script>` tag, typically in the `<head>`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Your Article Title",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "datePublished": "2024-01-15",
  "image": "https://example.com/image.jpg"
}
</script>
```

### Common Schema Types for WordPress

#### Article / BlogPosting

For blog posts and news articles:

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/your-post/"
  },
  "headline": "Complete Guide to WordPress SEO",
  "description": "Learn how to optimize your WordPress site for search engines.",
  "image": {
    "@type": "ImageObject",
    "url": "https://example.com/wp-content/uploads/featured.jpg",
    "width": 1200,
    "height": 630
  },
  "author": {
    "@type": "Person",
    "name": "John Doe",
    "url": "https://example.com/author/john/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Your Site Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png",
      "width": 600,
      "height": 60
    }
  },
  "datePublished": "2024-01-15T08:00:00+00:00",
  "dateModified": "2024-02-20T10:30:00+00:00"
}
```

#### LocalBusiness

For business websites with physical locations:

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Your Business Name",
  "description": "Brief description of your business",
  "image": "https://example.com/storefront.jpg",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "City",
    "addressRegion": "State",
    "postalCode": "12345",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "telephone": "+1-555-555-5555",
  "url": "https://example.com",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "17:00"
    }
  ],
  "priceRange": "$$"
}
```

#### Product (for WooCommerce)

For e-commerce product pages:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "description": "Product description here",
  "image": [
    "https://example.com/product-1.jpg",
    "https://example.com/product-2.jpg"
  ],
  "sku": "ABC123",
  "brand": {
    "@type": "Brand",
    "name": "Brand Name"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product/",
    "priceCurrency": "USD",
    "price": "49.99",
    "priceValidUntil": "2024-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "24"
  }
}
```

**Note:** WooCommerce and SEO plugins add Product schema automatically. Only add custom schema if you need additional fields.

#### FAQPage

For FAQ sections — displays expandable Q&A directly in search results:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is WordPress?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "WordPress is an open-source content management system used to build websites and blogs."
      }
    },
    {
      "@type": "Question",
      "name": "Is WordPress free?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, WordPress software is free. You only pay for hosting and optional premium themes/plugins."
      }
    }
  ]
}
```

#### BreadcrumbList

For navigation breadcrumbs:

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Blog",
      "item": "https://example.com/blog/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "SEO Guide",
      "item": "https://example.com/blog/seo-guide/"
    }
  ]
}
```

#### HowTo

For tutorial and instructional content:

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Install WordPress",
  "description": "Step-by-step guide to installing WordPress on your server.",
  "totalTime": "PT15M",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "USD",
    "value": "0"
  },
  "step": [
    {
      "@type": "HowToStep",
      "name": "Download WordPress",
      "text": "Go to wordpress.org and download the latest version.",
      "url": "https://example.com/install-guide/#step1"
    },
    {
      "@type": "HowToStep",
      "name": "Upload to Server",
      "text": "Upload the WordPress files to your web server via FTP.",
      "url": "https://example.com/install-guide/#step2"
    }
  ]
}
```

### Adding Schema in WordPress

#### Method 1: SEO Plugin (Recommended)

Both Yoast SEO and Rank Math automatically add:
- Article/BlogPosting for posts
- WebPage for pages
- Organization/Person for site
- BreadcrumbList for navigation
- Product for WooCommerce (with extensions)

Configure in the plugin's Schema settings. Add page-specific schema in the post editor.

#### Method 2: Theme Integration

Add schema output in your theme's `functions.php`:

```php
function add_article_schema() {
    if (!is_single()) return;

    global $post;
    $author = get_the_author_meta('display_name', $post->post_author);
    $image = get_the_post_thumbnail_url($post->ID, 'full');

    $schema = [
        '@context' => 'https://schema.org',
        '@type' => 'Article',
        'headline' => get_the_title(),
        'author' => [
            '@type' => 'Person',
            'name' => $author
        ],
        'datePublished' => get_the_date('c'),
        'dateModified' => get_the_modified_date('c'),
        'image' => $image ?: ''
    ];

    echo '<script type="application/ld+json">' .
         wp_json_encode($schema, JSON_UNESCAPED_SLASHES) .
         '</script>';
}
add_action('wp_head', 'add_article_schema');
```

#### Method 3: Block or Shortcode

Create a reusable block or shortcode for FAQ schema:

```php
function faq_schema_shortcode($atts, $content = null) {
    // Parse FAQ content and generate schema
    // This is a simplified example
    $faqs = parse_faq_content($content);

    $schema = [
        '@context' => 'https://schema.org',
        '@type' => 'FAQPage',
        'mainEntity' => array_map(function($faq) {
            return [
                '@type' => 'Question',
                'name' => $faq['question'],
                'acceptedAnswer' => [
                    '@type' => 'Answer',
                    'text' => $faq['answer']
                ]
            ];
        }, $faqs)
    ];

    return '<script type="application/ld+json">' .
           wp_json_encode($schema, JSON_UNESCAPED_SLASHES) .
           '</script>' . $content;
}
add_shortcode('faq_schema', 'faq_schema_shortcode');
```

### Validation and Testing

Always validate your structured data before and after deployment.

#### Google Rich Results Test

**URL:** https://search.google.com/test/rich-results

- Tests if your page is eligible for rich results
- Shows which schema types were detected
- Highlights errors and warnings
- Preview how rich results might appear

#### Schema Markup Validator

**URL:** https://validator.schema.org/

- Validates all Schema.org markup (not just Google-supported)
- More comprehensive error checking
- Useful for debugging complex nested schemas

#### Google Search Console

In Search Console > Enhancements:

- See schema types detected across your site
- Track valid items vs. errors over time
- Identify pages with invalid markup
- Monitor rich result impressions

### Common Schema Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Missing required fields | Rich results won't show | Check Google's documentation for required fields |
| Incorrect data types | Validation errors | Use strings for text, numbers for prices |
| Markup doesn't match content | Manual action risk | Schema must describe visible page content |
| Duplicate schema | Conflicting data | Use one source (plugin OR custom, not both) |
| Hidden content in schema | Against guidelines | Only include content users can see |
| Self-serving reviews | Spam violation | Never add fake or internal reviews |

### Schema and Rich Results by Type

| Schema Type | Potential Rich Result | Requirements |
|-------------|----------------------|--------------|
| Article | Article carousel, Top stories | headline, image, author, datePublished |
| Product | Price, availability, ratings | name, offers, review or aggregateRating |
| FAQPage | Expandable Q&A | At least one Question with Answer |
| HowTo | Step-by-step in SERP | name, step array with text |
| LocalBusiness | Knowledge panel, Maps | name, address, telephone |
| Recipe | Recipe card with image | name, image, recipeIngredient |
| Event | Event listing | name, startDate, location |
| BreadcrumbList | Breadcrumb trail | itemListElement array |

### Debugging Schema Issues

If rich results aren't appearing:

1. **Test the live URL** (not just the code) in Rich Results Test
2. **Check Search Console** for manual actions or errors
3. **Verify indexing** — the page must be indexed first
4. **Wait** — rich results can take weeks to appear
5. **Check eligibility** — not all pages qualify for rich results
6. **Review guidelines** — ensure compliance with Google's policies

### Plugin Recommendations for Schema

| Need | Recommendation |
|------|----------------|
| General SEO + Schema | Rank Math (free includes most schema types) |
| WooCommerce Product Schema | Built into WooCommerce + SEO plugin |
| Custom/Advanced Schema | Schema Pro, WP Schema (paid) |
| FAQ Schema specifically | Yoast FAQ Block, Rank Math FAQ Block |
| Local Business | Rank Math Local SEO, Yoast Local SEO |

## Further Reading

- [Google's Structured Data Documentation](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
- [Schema.org Full Hierarchy](https://schema.org/docs/full.html)
- [Rich Results Test](https://search.google.com/test/rich-results)
- [WordPress Native Sitemaps Documentation](https://developer.wordpress.org/apis/sitemaps/)
- [Performance for SEO](./04-performance-for-seo.md) — Core Web Vitals and speed optimization
