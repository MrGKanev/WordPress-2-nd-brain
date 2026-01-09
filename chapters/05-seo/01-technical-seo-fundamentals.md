# Technical SEO Fundamentals

## Overview

Technical SEO is the foundation that makes your content discoverable. Think of it as building a house - you can have beautiful furniture (content), but without solid foundations (technical SEO), the house won't stand.

Unlike on-page SEO (keywords, content quality) or off-page SEO (backlinks), technical SEO focuses on how search engines access, crawl, interpret, and index your site.

> **Key insight**: Technical SEO doesn't directly make you rank higher. It removes obstacles that prevent search engines from understanding your site. A technically perfect site with poor content won't rank, but great content on a technically broken site won't either.

## How Search Engines See Your WordPress Site

### The Crawling Process

Search engines discover your site through links. When Googlebot visits a page, it:

1. **Fetches the HTML** - Downloads your page's source code
2. **Parses the content** - Extracts text, links, and metadata
3. **Renders JavaScript** - Executes JS to see dynamic content (delayed)
4. **Follows links** - Discovers new pages to crawl
5. **Stores in index** - Adds to searchable database

WordPress sites have an advantage here - they generate clean, semantic HTML by default. However, plugins and themes can complicate this with excessive JavaScript, broken markup, or slow loading times.

### What Search Engines Prioritize

| Priority | Element | Why It Matters |
|----------|---------|----------------|
| High | Page content | What the page is actually about |
| High | Title tag | Primary signal for page topic |
| High | Internal links | How pages relate to each other |
| Medium | Headings (H1-H6) | Content structure and hierarchy |
| Medium | URL structure | Context about page content |
| Medium | Meta description | Doesn't affect ranking, but affects clicks |
| Low | Meta keywords | Completely ignored by Google since 2009 |

## URL Structure

### Why URLs Matter

URLs serve three audiences:

1. **Users** - Should understand what the page is about before clicking
2. **Search engines** - Use URLs as one signal for page content
3. **Other sites** - Clean URLs are more likely to be linked and shared

### WordPress Permalink Settings

WordPress offers several permalink structures. Here's how they compare:

| Structure | Example | SEO Value |
|-----------|---------|-----------|
| Plain | `?p=123` | Poor - no context |
| Day and name | `/2024/01/15/post-name/` | Okay - dates can age content |
| Month and name | `/2024/01/post-name/` | Okay - same issue |
| Post name | `/post-name/` | Best - clean and descriptive |
| Custom | `/blog/%postname%/` | Good - adds category context |

**Recommendation**: Use "Post name" (`/%postname%/`) for most sites. It's clean, descriptive, and doesn't include dates that make evergreen content appear outdated.

### URL Best Practices

**Keep URLs short but descriptive.** Google truncates long URLs in search results, and users prefer readable links. Compare:

- Bad: `/the-complete-ultimate-guide-to-everything-you-need-to-know-about-wordpress-seo-optimization-in-2024/`
- Good: `/wordpress-seo-guide/`

**Use hyphens, not underscores.** Google treats hyphens as word separators but underscores as word joiners:
- `wordpress-seo` = "wordpress" + "seo"
- `wordpress_seo` = "wordpressseo" (one word)

**Avoid URL parameters when possible.** URLs like `/products/?color=red&size=large` create duplicate content issues. Use clean URLs with proper canonical tags instead.

## Indexability vs. Crawlability

These terms are often confused but represent different concepts:

### Crawlability

Can search engines access your page?

Blocked by:
- `robots.txt` Disallow rules
- Server errors (5xx)
- Authentication requirements
- Firewall blocks (including overly aggressive security plugins)

### Indexability

Should search engines add your page to their index?

Controlled by:
- `noindex` meta tag or header
- Canonical tags pointing elsewhere
- Low-quality content (algorithmic)
- Manual penalties

### The Relationship

```
Crawlable + Indexable     = Page appears in search results
Crawlable + Not Indexable = Page is crawled but not shown
Not Crawlable             = Page is invisible to search engines
```

> **Common mistake**: Blocking pages in robots.txt doesn't remove them from Google. If other sites link to a blocked page, Google may still index the URL (without content). Use `noindex` to prevent indexing.

## WordPress-Specific Indexability Issues

### Taxonomy Archives

WordPress creates multiple ways to access the same content:

- Category archives: `/category/news/`
- Tag archives: `/tag/featured/`
- Author archives: `/author/admin/`
- Date archives: `/2024/01/`

Each of these can create thin content (pages with just post excerpts) and duplicate content issues. Consider:

| Archive Type | Keep Indexed? | Reasoning |
|--------------|---------------|-----------|
| Category | Usually yes | Provides navigation and topical organization |
| Tag | Usually no | Often creates thin, overlapping content |
| Author | Depends | Useful for multi-author sites, not for single author |
| Date | Usually no | Rarely useful for users, fragments content |

### Attachment Pages

By default, WordPress creates a separate page for every uploaded image. These pages contain only the image with minimal content - prime candidates for `noindex` or redirection to the parent post.

### Search Results Pages

Your internal search (`/?s=query`) should never be indexed. These pages:
- Create infinite URL variations
- Contain duplicate content
- Provide no unique value

Most SEO plugins handle this automatically, but it's worth verifying.

## HTTPS and Security

### Why HTTPS Matters for SEO

HTTPS is a confirmed (though minor) ranking factor. More importantly:

1. **Browser warnings** - Chrome marks HTTP sites as "Not Secure"
2. **User trust** - Users expect the padlock icon
3. **Data integrity** - Prevents content injection by ISPs
4. **Required for modern features** - HTTP/2, service workers, geolocation all require HTTPS

### Mixed Content Issues

After migrating to HTTPS, "mixed content" occurs when secure pages load insecure resources (images, scripts, stylesheets over HTTP). This can:

- Trigger browser warnings
- Break functionality
- Undermine security

WordPress sites commonly have mixed content from:
- Hardcoded HTTP URLs in content
- Old theme/plugin assets
- External embeds and iframes

## Mobile-First Indexing

Since 2019, Google predominantly uses mobile content for indexing. This means:

### What Google Sees

Google's crawler primarily behaves as a mobile device. If your mobile version:
- Has less content than desktop → Google sees less content
- Hides elements for mobile → Google may not see those elements
- Loads slower on mobile → Impacts crawl efficiency

### WordPress Responsive Design

Most modern WordPress themes are responsive, but issues can arise:

| Issue | Impact | Solution |
|-------|--------|----------|
| Hiding content with CSS | May be ignored by Google | Use responsive design, not hidden content |
| Mobile-only navigation | Can affect internal linking | Ensure all important links are accessible |
| Slow mobile loading | Hurts crawl budget | Optimize images, reduce JavaScript |
| Touch target sizes | UX issue, not ranking factor | Make buttons at least 48x48 pixels |

## Site Architecture

### The Importance of Depth

"Click depth" measures how many clicks from the homepage to reach a page. General guidelines:

- **1-2 clicks**: Most important content
- **3-4 clicks**: Secondary content
- **5+ clicks**: May be seen as less important, crawled less frequently

WordPress naturally creates depth through categories and pagination. A blog with 500 posts might have articles buried 10+ clicks deep. Solutions:

1. **Prominent category navigation** - Makes category pages 1 click from home
2. **Related posts** - Cross-links between articles
3. **HTML sitemaps** - Provide alternative navigation paths
4. **Reduce pagination** - Show more posts per archive page

### Internal Linking Strategy

Internal links do three things:

1. **Help users navigate** - Find related content
2. **Distribute "link equity"** - Pass authority between pages
3. **Establish hierarchy** - Show search engines what's important

The pages you link to most frequently signal importance. This is why many SEO strategies involve linking to key pages from:
- Navigation menus
- Footer links
- Sidebar widgets
- Within content (contextual links)

## Canonicalization

### The Duplicate Content Problem

The same content can often be accessed via multiple URLs:

```
https://example.com/page/
https://example.com/page
http://example.com/page/
http://www.example.com/page/
https://example.com/page/?utm_source=twitter
```

All five URLs show identical content. Search engines must decide which to index.

### How Canonical Tags Work

The `rel="canonical"` tag tells search engines: "This is the official version of this page."

WordPress handles basic canonicalization automatically, but you need plugins for:
- Cross-domain canonicals (syndicated content)
- Paginated content handling
- Query parameter management

### Self-Referencing Canonicals

Every page should have a canonical tag pointing to itself (self-referencing canonical). This:
- Confirms the preferred URL format
- Handles URL parameters automatically
- Prevents accidental duplicates

## Structured Data (Schema)

### What It Does

Structured data doesn't directly improve rankings, but it can enhance search results with "rich snippets":

- Star ratings for reviews
- Recipe details (cooking time, calories)
- FAQ accordions
- Event dates and locations
- Product prices and availability

### WordPress Implementation

You have three options:

| Method | Pros | Cons |
|--------|------|------|
| Theme/plugin built-in | Automatic, maintained | May be basic or incorrect |
| SEO plugin | Integrated with other SEO | Limited customization |
| Custom implementation | Full control | Requires maintenance |

Most sites should use an SEO plugin's structured data features. Custom implementation is only worthwhile for complex requirements or when existing solutions produce errors.

## Core Web Vitals as Technical SEO

Performance is now part of technical SEO. The Core Web Vitals measure:

- **LCP (Largest Contentful Paint)** - Loading speed
- **INP (Interaction to Next Paint)** - Responsiveness
- **CLS (Cumulative Layout Shift)** - Visual stability

For detailed optimization strategies, see [Performance Optimization for SEO](./04-performance-optimization-for-seo.md).

## Technical SEO Audit Checklist

When auditing a WordPress site, check these fundamentals:

### Crawlability
- [ ] Can Googlebot access all important pages?
- [ ] Is robots.txt properly configured?
- [ ] Are there server errors blocking crawling?
- [ ] Do security plugins block legitimate bots?

### Indexability
- [ ] Are important pages indexable?
- [ ] Are thin/duplicate pages set to noindex?
- [ ] Do canonical tags point to correct URLs?
- [ ] Is the XML sitemap submitted and error-free?

### URL Structure
- [ ] Are permalinks set to post name?
- [ ] Are URLs clean and descriptive?
- [ ] Do all URLs redirect to one canonical format?
- [ ] Is HTTPS properly implemented?

### Mobile & Performance
- [ ] Is the site mobile-friendly?
- [ ] Does mobile have the same content as desktop?
- [ ] Do Core Web Vitals pass thresholds?
- [ ] Is the site accessible globally?

## Common Technical SEO Mistakes in WordPress

### Over-blocking in robots.txt

Some guides recommend blocking `/wp-admin/`, `/wp-includes/`, and `/wp-content/plugins/`. This is outdated advice. Blocking CSS and JavaScript can prevent proper rendering and harm SEO.

### Relying on "SEO-friendly" Claims

Many themes and plugins claim to be "SEO-friendly" or "SEO-optimized." These terms are meaningless marketing. What matters:
- Clean HTML output
- Proper heading structure
- Schema markup implementation
- Performance optimization

### Ignoring Log Files

Server logs show exactly what search engines crawl. Regular log analysis reveals:
- Crawl errors you didn't know about
- Resources consuming crawl budget
- Blocked resources
- Crawl frequency changes

### Plugin Conflicts

Multiple SEO plugins often conflict, creating duplicate meta tags, conflicting canonicals, or multiple sitemaps. Use one comprehensive SEO plugin, not several overlapping ones.

## Further Reading

- [Optimizing robots.txt](./02-optimizing-robots.txt.md) - Detailed robots.txt configuration
- [XML Sitemaps and Structured Data](./03-xml-sitemaps-and-structured-data.md) - Sitemap best practices
- [Performance Optimization for SEO](./04-performance-optimization-for-seo.md) - Core Web Vitals and speed
