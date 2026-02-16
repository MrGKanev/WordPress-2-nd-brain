# WordPress Fundamentals

## What is WordPress?

WordPress is an open-source CMS written in PHP that runs roughly 43% of the web. That number isn't a marketing gimmick—it reflects two decades of pragmatic decisions: easy hosting on cheap LAMP/LEMP stacks, a plugin system that lets non-developers add features, and a theme layer that separates design from logic.

At its core, WordPress is a PHP application backed by MySQL (or MariaDB). You install plugins and themes into `wp-content/`, WordPress handles routing, querying, and rendering, and the result is HTML sent to the browser. Simple in principle, nuanced in practice.

## WordPress.org vs WordPress.com

| WordPress.org | WordPress.com |
|---------------|---------------|
| Self-hosted software | Hosted service |
| Full control | Limited control |
| Install anywhere | Only on their servers |
| Any plugin/theme | Restricted (paid plans) |
| You handle updates | They handle updates |
| Free software | Free tier + paid plans |

This book focuses on **WordPress.org** (self-hosted).

## How WordPress Works

### The Request Lifecycle

Understanding this flow helps you debug problems and optimize performance. When a page loads slowly, you can pinpoint where the delay happens—is it the database query? A slow plugin loading in `wp-settings.php`? The template rendering?

```
Browser Request
      ↓
Web Server (Apache/Nginx)
      ↓
index.php
      ↓
wp-blog-header.php
      ↓
wp-load.php → wp-config.php
      ↓
wp-settings.php (loads core, plugins, theme)
      ↓
Parse request → Determine query type
      ↓
Run main query
      ↓
Load template (via template hierarchy)
      ↓
Output HTML
      ↓
Browser renders page
```

Every plugin you install adds code that runs during `wp-settings.php`. Every theme function fires before the template loads. Fifty plugins means fifty extra files loaded and initialized on every single request—even if most of them do nothing on that particular page. That's the cost of WordPress's flexibility.

### Key Concepts

**Everything is a hook.** WordPress uses actions and filters to allow plugins and themes to modify behavior without editing core files. Think of hooks as "announcement points"—WordPress announces "I'm about to show the title" and any plugin can respond "Wait, let me modify that first." This is how a security plugin can block login attempts without touching WordPress core, or how an SEO plugin adds meta tags to every page.

**Everything is a post.** Posts, pages, attachments, menu items—they're all stored in the `wp_posts` table with different `post_type` values. This might seem strange at first, but it's elegant: one table, one set of functions, infinite content types. When you add a WooCommerce product, it's just a post with `post_type = 'product'`.

**Configuration lives in the database.** Site settings, plugin options, widget configurations—stored in `wp_options`. This means you can't just copy WordPress files to migrate a site; you need the database too. It also means careless plugins can bloat your options table with thousands of rows that never get cleaned up.

## Directory Structure

```
wordpress/
├── wp-admin/              # Admin dashboard files
├── wp-content/            # YOUR CONTENT (themes, plugins, uploads)
│   ├── themes/
│   │   ├── theme-name/
│   │   └── theme-name-child/
│   ├── plugins/
│   │   └── plugin-name/
│   ├── uploads/           # Media library files
│   │   └── 2024/01/       # Organized by year/month
│   ├── upgrade/           # Temp files during updates
│   └── mu-plugins/        # Must-use plugins (always active, can't be disabled)
├── wp-includes/           # Core WordPress files
├── wp-config.php          # Database credentials, constants
├── .htaccess              # Apache rewrite rules
└── index.php              # Entry point
```

**Golden rule:** Only modify files in `wp-content/`. Everything else gets overwritten on updates.

**Why mu-plugins exist:** Must-use plugins load before regular plugins and can't be deactivated from the admin panel. This is useful for critical functionality that should never be accidentally disabled—like custom security rules, performance optimizations, or client-specific code that shouldn't be touched.

## Database Structure

WordPress uses ~12 core tables (default prefix `wp_`):

| Table | Purpose |
|-------|---------|
| `wp_posts` | All content (posts, pages, CPTs, attachments) |
| `wp_postmeta` | Custom fields for posts |
| `wp_terms` | Categories, tags, custom taxonomy terms |
| `wp_term_taxonomy` | Taxonomy definitions |
| `wp_term_relationships` | Links posts to terms |
| `wp_users` | User accounts |
| `wp_usermeta` | User profile data |
| `wp_options` | Site settings, plugin options |
| `wp_comments` | Comments on posts |
| `wp_commentmeta` | Comment metadata |
| `wp_links` | Blogroll (legacy, rarely used) |

**Why separate "meta" tables?** WordPress uses a flexible key-value pattern for custom data. Instead of adding columns to the main tables (which would require schema changes), plugins store custom fields in meta tables. A post can have unlimited custom fields without changing the database structure. The trade-off: meta queries can be slower than direct column lookups, especially at scale.

### The Posts Table

The most important table. Everything is a post:

```sql
SELECT post_type, COUNT(*)
FROM wp_posts
GROUP BY post_type;
```

Common post types:
- `post` - Blog posts
- `page` - Static pages
- `attachment` - Media files
- `revision` - Post revisions
- `nav_menu_item` - Menu items
- `custom_type` - Your custom post types

## Core Concepts

### Posts vs Pages

| Posts | Pages |
|-------|-------|
| Time-based content | Timeless content |
| Categories & tags | Hierarchical (parent/child) |
| Appear in feeds | Don't appear in feeds |
| Blog entries, news | About, Contact, Services |

### Taxonomies

Ways to organize content:

- **Categories** - Hierarchical grouping (parent → child)
- **Tags** - Flat labels
- **Custom taxonomies** - Your own groupings (genres, locations, etc.)

### Users and Roles

Built-in roles:

| Role | Capabilities |
|------|--------------|
| Super Admin | Multisite network admin |
| Administrator | Full site control |
| Editor | Manage all content |
| Author | Publish own posts |
| Contributor | Write posts, can't publish |
| Subscriber | Read only, manage profile |

### The Loop

The Loop is WordPress's way of iterating through query results and displaying content. It's called "The Loop" because it literally loops through posts one by one, setting up global variables for each post so template tags like `the_title()` know which post to display.

```php
<?php if ( have_posts() ) : ?>
    <?php while ( have_posts() ) : the_post(); ?>
        <h2><?php the_title(); ?></h2>
        <?php the_content(); ?>
    <?php endwhile; ?>
<?php endif; ?>
```

**How it works:** Before the template loads, WordPress runs a database query based on the URL (e.g., "get all posts in category X" or "get the page with slug Y"). The Loop then iterates through those results. The `the_post()` function is crucial—it advances to the next post and sets up all the global variables that template tags rely on.

Every WordPress page uses some form of The Loop—even a single page view loops through one result.

## The Hooks System (Preview)

Hooks let you modify WordPress without editing core files.

**Actions** - Do something at a specific point:
```php
// Run code when WordPress initializes
add_action( 'init', 'my_function' );
```

**Filters** - Modify data passing through:
```php
// Change the post title
add_filter( 'the_title', 'my_title_modifier' );
```

This is covered in depth in the [Plugin Development](../08-plugin-development/02-hooks-system.md) chapter.

## When to Use WordPress

**Good fit:**
- Content-heavy websites
- Blogs and news sites
- Business websites
- E-commerce (with WooCommerce)
- Membership sites
- Portfolio sites
- Sites where clients need to edit content

**Think twice before using WordPress for:**
- Pure web applications with complex client-side state (React/Vue SPAs do this better)
- Real-time features as the core product (WebSocket-based tools are a better fit)
- API-only backends where you'll never need a UI (Laravel, Express, or Go will serve you better)
- Simple brochure sites with no dynamic content (a static site generator builds faster and costs nothing to host)

## Essential Tools

### Local Development

Never develop directly on a live site. Local development gives you a safe environment to experiment, make mistakes, and test changes without risking your production site. You can break things, restore quickly, and work offline.

- **[Local](https://localwp.com/)** - Easiest local WordPress setup (one-click install, great for beginners)
- **[DDEV](https://ddev.com/)** - Docker-based, more flexible (better for teams with complex setups)
- **[Lando](https://lando.dev/)** - Another Docker option
- **MAMP/XAMPP** - Traditional approach (works but harder to manage multiple sites)

### Browser Tools

- **Query Monitor** - Essential debugging plugin
- **Chrome DevTools** - Network, performance, console
- **React DevTools** - For block editor development

### Command Line

- **[WP-CLI](https://wp-cli.org/)** - WordPress command line interface
- Essential for automation, bulk operations, deployments

## The Block Editor (Gutenberg)

WordPress 5.0 (December 2018) replaced the classic TinyMCE editor with Gutenberg—a block-based editor built on React. This wasn't just a UI change; it fundamentally shifted how WordPress thinks about content.

**Before Gutenberg:** Content was a single blob of HTML in the `post_content` field. Layout required shortcodes, page builders, or manual HTML.

**After Gutenberg:** Content is a series of structured blocks—paragraphs, headings, images, columns, custom blocks—each with its own settings and markup. The blocks are still stored as HTML in `post_content`, but with special comment delimiters that Gutenberg can parse:

```html
<!-- wp:paragraph -->
<p>This is a paragraph block.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":42} -->
<figure class="wp-block-image"><img src="photo.jpg" alt=""/></figure>
<!-- /wp:image -->
```

**Why this matters for developers:**
- Themes are moving from PHP templates to `theme.json` + block templates
- Custom blocks are built with React (JSX) and PHP for server-side rendering
- The Site Editor (Full Site Editing) lets users edit headers, footers, and page templates visually
- Classic themes still work, but new WordPress features increasingly assume blocks

You don't have to love Gutenberg, but you do have to understand it. The block editor is where WordPress is heading, and block theme development is covered in the [Theme Development](../07-theme-development/03-block-themes.md) chapter.

## Learning Path

After this chapter, proceed in this order:

1. **[Maintenance](../02-maintenance/README.md)** - Learn to manage WordPress sites
2. **[Security](../03-security/README.md)** - Understand security basics
3. **[Performance](../04-performance/README.md)** - Optimize your sites
4. **[SEO](../05-seo/README.md)** - Search engine optimization
5. **[E-commerce](../06-e-commerce/README.md)** - WooCommerce basics
6. **[Theme Development](../07-theme-development/README.md)** - Build themes
7. **[Plugin Development](../08-plugin-development/README.md)** - Build plugins

## Further Reading

- [WordPress.org Documentation](https://wordpress.org/documentation/)
- [Developer Resources](https://developer.wordpress.org/)
- [Learn WordPress](https://learn.wordpress.org/) - Free official courses
- [Database Operations](../08-plugin-development/03-database-operations.md) - Advanced queries and custom tables
- [Plugin Development](../08-plugin-development/README.md) - Custom capabilities, CPTs, and the full hooks system
