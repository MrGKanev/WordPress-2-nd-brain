# WordPress SEO Optimization

## Overview

SEO for WordPress involves technical configuration, content strategy, and performance optimization working together. This chapter focuses on the technical side - what developers and site administrators can control to help search engines discover, crawl, and index content effectively.

> **Key principle**: Technical SEO removes obstacles. It doesn't make bad content rank, but it ensures good content can be found. A technically perfect site with poor content won't rank, but great content on a technically broken site won't either.

## What This Chapter Covers

### [Technical SEO Fundamentals](./01-technical-seo-fundamentals.md)

The foundation of search engine visibility. Covers:

- How search engines crawl and index WordPress
- URL structure and permalinks
- Indexability vs. crawlability
- Site architecture and internal linking
- Common WordPress-specific issues

### [Optimizing robots.txt](./02-optimizing-robots.txt.md)

Controlling what search engines can access. Covers:

- Default WordPress robots.txt behavior
- What to block and what to allow
- Common mistakes to avoid
- Sitemap references

### [XML Sitemaps and Structured Data](./03-xml-sitemaps-and-structured-data.md)

Helping search engines understand your content. Covers:

- WordPress sitemap options
- Schema markup implementation
- Rich results eligibility
- Testing and validation

### [Performance Optimization for SEO](./04-performance-optimization-for-seo.md)

Speed as a ranking factor. Covers:

- Core Web Vitals and Google rankings
- Mobile-first indexing
- Crawl budget optimization
- Server response time

## SEO Priorities for WordPress

When optimizing a WordPress site for search, address these in order:

1. **Crawlability** - Can search engines access your pages?
2. **Indexability** - Should they add pages to their index?
3. **Content quality** - Is the content worth ranking?
4. **Technical performance** - Does the site meet speed thresholds?
5. **User experience** - Does the site work well for visitors?

### [International SEO](./05-international-seo.md)

Multilingual and multi-region SEO. Covers:

- Hreflang tags and implementation
- URL structures for multilingual sites
- WordPress multilingual plugins (WPML, Polylang, TranslatePress)
- WooCommerce multilingual and multi-currency

### [E-commerce SEO](./06-ecommerce-seo.md)

WooCommerce-specific SEO. Covers:

- Product schema markup and rich snippets
- Category page optimization
- Faceted navigation SEO pitfalls
- Out-of-stock product handling
- Google Merchant Center integration

### [JavaScript SEO](./07-javascript-seo.md)

JavaScript rendering and search engine visibility. Covers:

- How Google renders JavaScript (two-phase pipeline)
- Headless WordPress SEO challenges
- Rendering strategies (SSR, SSG, CSR, ISR)
- AJAX content loading and lazy loading
- Dynamic rendering as a workaround

## What This Chapter Doesn't Cover

This chapter focuses on technical SEO. For related topics, see:

- **Content optimization** - Keyword research, writing, content strategy
- **Link building** - Outreach, PR, earning backlinks
- **Local SEO** - Google Business Profile, local citations

## Further Reading

- [WordPress Optimization](../04-performance/README.md) - Server and code performance
- [Plugin Architecture](../08-plugin-development/README.md) - Building SEO-friendly plugins
