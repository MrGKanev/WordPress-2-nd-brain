# Client Handoff Documentation

The site is built, tested, and ready. Now comes the part many developers skip: handing it over so the client can actually use it. A clean handoff prevents "how do I...?" emails for the next six months and sets clear expectations about maintenance responsibility.

## What Clients Need

### Documentation Hierarchy

| Priority | What | Why |
|----------|------|-----|
| **Must have** | Login credentials, basic content editing | Can't use the site without these |
| **Should have** | Plugin guide, backup info, update instructions | Self-sufficiency for routine tasks |
| **Nice to have** | Video walkthroughs, advanced feature docs | Reduces support requests |

## Handoff Checklist

### Technical Handoff

- [ ] All login credentials documented (WordPress, hosting, domain registrar, email, CDN)
- [ ] DNS configuration documented (nameservers, key records)
- [ ] Hosting control panel access provided
- [ ] SSL certificate auto-renewal verified
- [ ] Backup system configured and tested
- [ ] Staging environment set up (if applicable)
- [ ] SMTP/email configuration documented
- [ ] Analytics/Search Console access shared
- [ ] Payment gateway credentials documented (WooCommerce)
- [ ] All third-party API keys and service accounts listed

### Content Management Handoff

- [ ] Admin account created with appropriate role
- [ ] Content editing guide provided
- [ ] Media upload guidelines (image sizes, formats)
- [ ] Menu management explained
- [ ] Form submissions/notifications tested
- [ ] SEO plugin basics explained (meta titles, descriptions)
- [ ] WooCommerce product management (if applicable)

## Credential Documentation

### What to Document

```
Site: example.com

WordPress Admin
  URL: https://example.com/wp-admin
  Username: client-admin
  Password: [stored in password manager]
  Role: Administrator

Hosting
  Provider: Kinsta / Cloudways / etc.
  Dashboard: https://my.kinsta.com
  Login: client@example.com

Domain Registrar
  Provider: Cloudflare / Namecheap / etc.
  Dashboard: https://dash.cloudflare.com

Email (SMTP)
  Service: Mailgun / Postmark
  Dashboard: [URL]

Google
  Search Console: https://search.google.com/search-console
  Analytics: https://analytics.google.com

Payment (if WooCommerce)
  Stripe Dashboard: https://dashboard.stripe.com
  PayPal Business: https://business.paypal.com
```

**Never send credentials in plain text email.** Use a password manager shared vault (1Password, Bitwarden) or a secure one-time link service.

## Content Editing Guide

### Keep It Simple

Clients don't need to know about hooks, filters, or PHP. They need to know:

1. How to log in
2. How to create/edit posts and pages
3. How to add media
4. How to update menus
5. Who to contact when something breaks

### Page Structure Example

```
How to Edit a Page:
1. Log in at example.com/wp-admin
2. Go to Pages → All Pages
3. Click the page title to edit
4. Make changes in the editor
5. Click "Update" to save

Important: Don't change page slugs (URLs) without telling us.
This can break links and hurt SEO.
```

### Content Guidelines Document

| Topic | Guidance |
|-------|---------|
| **Images** | Upload JPG/PNG, minimum 1200px wide, max 500KB. The site will resize automatically. |
| **Headings** | Use H2 for main sections, H3 for subsections. Never use H1 (that's the page title). |
| **Links** | Link to internal pages when relevant. External links open in a new tab. |
| **Videos** | Paste YouTube/Vimeo URLs on their own line. Don't upload video files directly. |
| **Categories/Tags** | Use existing categories. Ask before creating new ones. |

## Admin Customization for Clients

### Custom Dashboard Widget

Replace the default WordPress dashboard with something useful:

```php
add_action( 'wp_dashboard_setup', function() {
    // Remove default widgets clients don't need
    remove_meta_box( 'dashboard_quick_press', 'dashboard', 'side' );
    remove_meta_box( 'dashboard_primary', 'dashboard', 'side' );
    remove_meta_box( 'dashboard_activity', 'dashboard', 'normal' );

    // Add custom welcome widget
    wp_add_dashboard_widget(
        'custom_help_widget',
        'Site Help & Support',
        function() {
            echo '<h3>Quick Links</h3>';
            echo '<ul>';
            echo '<li><a href="' . admin_url( 'edit.php?post_type=page' ) . '">Edit Pages</a></li>';
            echo '<li><a href="' . admin_url( 'upload.php' ) . '">Media Library</a></li>';
            echo '<li><a href="' . admin_url( 'nav-menus.php' ) . '">Edit Menus</a></li>';
            echo '</ul>';
            echo '<h3>Need Help?</h3>';
            echo '<p>Email: <a href="mailto:support@agency.com">support@agency.com</a></p>';
        }
    );
} );
```

### Hide Unnecessary Admin Items

```php
// Remove admin menu items clients shouldn't touch
add_action( 'admin_menu', function() {
    if ( ! current_user_can( 'manage_network' ) ) {
        remove_menu_page( 'tools.php' );
        remove_menu_page( 'edit-comments.php' ); // If comments disabled
    }
} );

// Remove admin bar items
add_action( 'wp_before_admin_bar_render', function() {
    global $wp_admin_bar;
    $wp_admin_bar->remove_menu( 'wp-logo' );
    $wp_admin_bar->remove_menu( 'comments' );
    $wp_admin_bar->remove_menu( 'new-content' );
} );
```

### Custom Login Page

```php
// Custom login logo
add_action( 'login_enqueue_scripts', function() {
    echo '<style>
        .login h1 a {
            background-image: url(' . esc_url( get_template_directory_uri() . '/assets/images/logo.svg' ) . ') !important;
            background-size: contain;
            width: 200px;
        }
    </style>';
} );

// Change login logo URL
add_filter( 'login_headerurl', function() {
    return home_url();
} );
```

## White-Labeling

For agencies delivering WordPress sites:

### Plugins for White-Labeling

| Plugin | Features |
|--------|----------|
| **White Label CMS** | Custom dashboard, login page, menus, footers |
| **Admin Menu Editor** | Reorganize and rename menu items |
| **Flavor** | Lightweight admin customization |

### Manual White-Label Basics

```php
// Change admin footer text
add_filter( 'admin_footer_text', function() {
    return 'Built by <a href="https://agency.com">Agency Name</a>. Need help? <a href="mailto:support@agency.com">Contact us</a>.';
} );

// Remove WordPress version from footer
add_filter( 'update_footer', '__return_empty_string', 11 );

// Custom admin color scheme
add_action( 'admin_enqueue_scripts', function() {
    wp_enqueue_style( 'custom-admin', get_template_directory_uri() . '/css/admin.css' );
} );
```

## Training

### Video Walkthroughs

Record short videos (2-5 minutes each) showing:

| Video | Content |
|-------|---------|
| Logging in | URL, credentials, dashboard overview |
| Editing pages | Open editor, make changes, save |
| Adding blog posts | Create, add featured image, categories, publish |
| Managing media | Upload, organize, find images |
| WooCommerce basics | Add product, manage orders, check reports |

### Tools for Recording

| Tool | Cost | Platform |
|------|------|----------|
| **Loom** | Free (25 videos) | Web, desktop |
| **OBS Studio** | Free | Desktop |
| **ScreenPal** | Free basic | Web, desktop |
| **CloudApp** | $9.95/month | Mac |

Host videos privately (unlisted YouTube, Loom link, or client portal) — not on public YouTube.

## Maintenance Agreements

### What to Include

| Tier | Includes | Typical Price |
|------|----------|---------------|
| **Basic** | Updates, backups, uptime monitoring | $50-100/month |
| **Standard** | Basic + monthly content changes, security scanning | $150-300/month |
| **Premium** | Standard + performance monitoring, priority support, dev hours | $300-500+/month |

### What to Define

- **Response time**: How quickly you'll respond to issues
- **Scope**: What's included vs. billable extra
- **Update policy**: How updates are tested and applied
- **Backup retention**: How far back backups go
- **Termination**: What happens if the agreement ends (full access handover)

## Post-Handoff Support

### Common Client Requests (First 30 Days)

| Request | Prevention |
|---------|-----------|
| "How do I change the menu?" | Include in documentation |
| "I can't log in" | Password manager, recovery instructions |
| "The site looks broken" | Cache clearing instructions |
| "I accidentally deleted a page" | Show revision/trash recovery |
| "I need to change the phone number everywhere" | Explain where site-wide settings are |

### Knowledge Base

For agencies with multiple clients, maintain a shared knowledge base:

- FAQ articles for common questions
- Video library indexed by topic
- Troubleshooting guides (cache, login, permissions)

## Further Reading

- [WP-CLI Essentials](./03-wp-cli-essentials.md) — CLI for efficient maintenance
- [Monitoring & Alerting](./07-monitoring-alerting.md) — Setting up monitoring for clients
- [Email Deliverability](./06-email-deliverability.md) — Ensuring site emails work
- [Plugin Recommendations](./01-plugin-recommendations.md) — Curated plugin choices
