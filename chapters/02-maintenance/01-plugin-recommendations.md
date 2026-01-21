# Plugin Recommendations

Plugin selection significantly impacts WordPress performance, security, and maintainability. A plugin can be 2 lines of efficient code or a massive resource hog. The quantity matters less than whether each plugin earns its place.

**Guiding principle:** Fewer plugins, better quality.

## Understanding Plugin Performance Impact

Before choosing plugins, understand how they affect your site.

### How Plugins Impact Performance

| Area | Impact | Measurement |
|------|--------|-------------|
| **PHP execution** | Plugins load on every request | Query Monitor → PHP time |
| **Database queries** | Extra queries per page load | Query Monitor → Queries by Component |
| **JavaScript** | Frontend scripts blocking render | Browser DevTools → Network |
| **CSS** | Stylesheet loading | Browser DevTools → Network |
| **External requests** | API calls, license checks | Query Monitor → HTTP API Calls |
| **Cron jobs** | Background processing | WP Crontrol |

### Typical Performance Overhead

| Plugin Type | Typical Impact | Notes |
|-------------|----------------|-------|
| **Page builder** | +200-500ms | Elementor, Divi load heavy assets |
| **Security plugin** | +50-150ms | Wordfence scans every request |
| **SEO plugin** | +20-50ms | Acceptable for the functionality |
| **Form plugin** | +10-30ms | Only on pages with forms ideally |
| **Slider plugin** | +100-300ms | Consider if really needed |
| **Social sharing** | +50-200ms | External API calls |
| **Live chat** | +100-400ms | Heavy third-party scripts |

### Measuring Plugin Impact

```bash
# Install Query Monitor
wp plugin install query-monitor --activate
```

Then check:
1. **Queries by Component:** Which plugins run most queries
2. **PHP execution time:** Total time and per-component breakdown
3. **HTTP API Calls:** External requests slowing things down
4. **Scripts/Styles:** Which plugins add most assets

---

## Essential Plugins by Site Type

### Every WordPress Site

| Plugin | Purpose | Performance Impact | Alternative |
|--------|---------|-------------------|-------------|
| **Query Monitor** | Debugging & profiling | Minimal (dev only) | Code Profiler |
| **Backup solution** | Disaster recovery | Varies | Host backups |
| **Object cache** | Database query cache | Major positive | Built into some hosts |

**Object cache options:**

| Plugin | When to Use |
|--------|-------------|
| Redis Object Cache | Redis available on server |
| LiteSpeed Cache | LiteSpeed server |
| W3 Total Cache | Multiple cache types needed |

### Blog / Content Site

| Plugin | Purpose | Why |
|--------|---------|-----|
| **Rank Math** or **SEOPress** | SEO | Full-featured, reasonable performance |
| **ShortPixel** or **EWWW** | Image optimization | Auto-converts to WebP |
| **Converter for Media** | WebP/AVIF | Lightweight, free |
| **Enable Media Replace** | Update images | Keep URLs when replacing |
| **Safe SVG** | SVG uploads | Security-sanitized SVG support |

### WooCommerce Store

| Plugin | Purpose | Why |
|--------|---------|-----|
| **WooCommerce** | E-commerce | The standard |
| **Disable Cart Fragments** | Performance | Eliminates admin-ajax on every page |
| **High-Performance Order Storage** | Performance | Enable HPOS in WooCommerce settings |
| **WP-Sweep** or **Advanced DB Cleaner** | Database cleanup | Cleans WooCommerce session data |
| **Solid Security** | Security | Lighter than Wordfence |
| **Payment gateway plugin** | Payments | Stripe/PayPal official plugins |

**WooCommerce-specific performance:**

| Issue | Solution |
|-------|----------|
| Cart fragments AJAX | Disable Cart Fragments AJAX plugin |
| Order storage | Enable HPOS (built into WooCommerce) |
| Session bloat | Regular database cleanup |
| Admin slowness | Disable WooCommerce marketing hub |

```php
// Disable WooCommerce marketing hub
add_filter( 'woocommerce_marketing_menu_items', '__return_empty_array' );
add_filter( 'woocommerce_admin_features', function( $features ) {
    return array_diff( $features, ['marketing', 'analytics'] );
});
```

### Agency / Client Sites

| Plugin | Purpose | Why |
|--------|---------|-----|
| **Admin and Site Enhancements** | Admin cleanup | Removes clutter, simplifies for clients |
| **Simple History** | Audit log | Track who changed what |
| **Limit Login Attempts Reloaded** | Security | Basic brute force protection |
| **WP Mail SMTP** | Email deliverability | Reliable email sending |
| **MainWP** (external) | Multi-site management | Manage many sites from one dashboard |

### Developer Sites

| Plugin | Purpose | Notes |
|--------|---------|-------|
| **Query Monitor** | Debugging | Essential for development |
| **Code Snippets** | Custom PHP | Safer than editing functions.php |
| **ACF** or **Meta Box** | Custom fields | ACF simpler, Meta Box more performant |
| **Custom Post Type UI** | CPT/taxonomy UI | Or register in code |
| **WP Crontrol** | Cron management | Debug scheduled tasks |
| **User Switching** | Testing roles | Quick user switching |

---

## Plugin Alternatives

Often there's a lighter alternative to popular heavy plugins.

### Page Builders

| Heavy Option | Lighter Alternative | Notes |
|--------------|---------------------|-------|
| Elementor Pro | Gutenberg + GenerateBlocks | Native, much faster |
| Divi | Gutenberg + Kadence Blocks | Better performance |
| WPBakery | Gutenberg (native) | Modern approach |

**Page builder impact:**

```
Elementor typical page:
├── 200-400KB JavaScript
├── 100-200KB CSS
├── +300-500ms load time

Gutenberg + GenerateBlocks:
├── 30-50KB JavaScript
├── 20-40KB CSS
├── +50-100ms load time
```

### SEO Plugins

| Plugin | Size | Features | Recommendation |
|--------|------|----------|----------------|
| **Yoast SEO** | Heavy | Full featured | Established, but bloated |
| **Rank Math** | Medium | Full featured | Good balance |
| **SEOPress** | Medium | Full featured | Clean code |
| **Slim SEO** | Light | Basic | Minimal overhead |
| **The SEO Framework** | Light | Automated | Set and forget |

### Security Plugins

| Plugin | Approach | Impact | Recommendation |
|--------|----------|--------|----------------|
| **Wordfence** | PHP-level firewall | High (every request scanned) | Use only if no WAF |
| **Sucuri** | Cloud + PHP | Medium | Redundant with Cloudflare |
| **Solid Security** | Focused features | Low | Good lightweight option |
| **Two-Factor** | 2FA only | Minimal | Does one thing well |

**Better approach:** Use Cloudflare for WAF, server-level security (fail2ban), and minimal WordPress security plugin.

### Caching Plugins

| Plugin | Best For | Complexity |
|--------|----------|------------|
| **LiteSpeed Cache** | LiteSpeed servers | Low |
| **WP Rocket** | Most sites | Low (paid) |
| **W3 Total Cache** | Advanced users | High |
| **WP Super Cache** | Basic caching | Low |
| **Redis Object Cache** | Object caching only | Low |

**Note:** Don't stack caching plugins. Pick one full solution or separate page cache + object cache.

---

## Plugins to Avoid

### Known Performance Problems

| Plugin | Issue | Alternative |
|--------|-------|-------------|
| **Jetpack** (full) | 30+ modules, heavy | Use individual solutions |
| **Broken Link Checker** | Constant DB/HTTP activity | Use external service (Ahrefs, Screaming Frog) |
| **Revive Old Posts** | Constant API calls | Schedule manually or use Buffer |
| **WP Smush (heavy scan)** | Scans entire library repeatedly | ShortPixel (on-upload only) |
| **Heavy sliders** | Large JS/CSS, often unnecessary | Static images or CSS-only solutions |

### Plugin Categories to Question

| Category | Why Questionable | Better Approach |
|----------|------------------|-----------------|
| **Social sharing buttons** | External scripts, tracking | Static SVG icons with share URLs |
| **Related posts** | Often inefficient queries | FLAVOR Related Posts (or none) |
| **Popup builders** | Heavy JS, UX issues | Simple CSS/JS popup |
| **Live chat widgets** | Massive third-party JS | Defer loading until interaction |
| **Performance "boosters"** | Often snake oil | Proper caching and optimization |

### Red Flags When Evaluating

| Red Flag | Why It Matters |
|----------|----------------|
| "Speed up your site instantly!" | Usually doesn't work that way |
| Installs tracking pixels | Privacy and performance concern |
| Makes external requests on every page load | Slows TTFB |
| No changelog or documentation | Likely abandoned |
| Single developer, no recent updates | Risk of abandonment |
| Requires constant "optimization" runs | Doing work on every visit |

---

## Plugin Selection Criteria

### Before Installing Any Plugin

| Question | Action |
|----------|--------|
| Can this be done without a plugin? | 3-line code snippet often better |
| Can I use a lighter alternative? | Check alternatives table |
| What's the performance impact? | Test with Query Monitor |
| Is it actively maintained? | Check last update, support forum |
| Is there an exit strategy? | Can you remove it cleanly? |
| Does it duplicate existing functionality? | Check for conflicts |

### Quality Indicators

**Good signs:**

- Regular updates (every 1-6 months)
- Active support forum with developer responses
- Clear documentation
- Tested with your WP/WooCommerce version
- Code available for review
- Known developer/company

**Warning signs:**

- Last updated 2+ years ago
- Support requests go unanswered
- No documentation
- Only tested with old WP versions
- Obfuscated code
- Unknown developer, no website

### Performance Testing Process

```
1. Install Query Monitor
2. Note baseline metrics:
   - Page load time
   - Database queries
   - HTTP API calls

3. Install plugin (don't activate)
4. Activate plugin
5. Measure again
6. Calculate difference

7. If impact > acceptable threshold:
   - Look for alternatives
   - Consider if benefit justifies cost
```

---

## WooCommerce Plugin Compatibility

### HPOS (High-Performance Order Storage)

WooCommerce's HPOS moves order data from meta tables to dedicated tables. This breaks plugins that directly query order meta.

**Before installing WooCommerce plugins, verify HPOS compatibility:**

| Status | Meaning |
|--------|---------|
| **Compatible** | Works with HPOS enabled |
| **Uncertain** | Hasn't been tested |
| **Incompatible** | Will break with HPOS |

Check: WooCommerce → Settings → Advanced → Features → See "Order data storage" compatible plugins.

### Block Checkout Compatibility

WooCommerce's new block-based checkout breaks many checkout customizations.

**Before customizing checkout:**

1. Check if plugin supports block checkout
2. Test thoroughly in staging
3. Have fallback to classic checkout if needed

```php
// Force classic checkout (temporary workaround)
add_filter( 'woocommerce_use_block_based_cart', '__return_false' );
add_filter( 'woocommerce_use_block_based_checkout', '__return_false' );
```

---

## Plugin Audit Process

### Monthly Quick Check

```
[ ] Any plugins need updates? Update in staging first
[ ] Any security advisories for installed plugins?
[ ] Any plugins showing errors in logs?
```

### Quarterly Deep Audit

```
1. List all active plugins
2. For each plugin:
   [ ] Is it still being used?
   [ ] Is it still maintained?
   [ ] Is there a better alternative?
   [ ] Does Query Monitor show excessive impact?

3. Remove unnecessary plugins
4. Replace outdated with alternatives
5. Document reasoning for each remaining plugin
```

### Annual Review

```
[ ] Full performance audit with/without each plugin
[ ] Check for functionality overlap
[ ] Evaluate new alternatives that have emerged
[ ] Review security advisories from past year
[ ] Update documentation for plugin choices
```

---

## Topic-Specific Plugin Lists

Detailed plugin recommendations are found in their relevant sections:

| Topic | Location | Key Plugins |
|-------|----------|-------------|
| Image optimization | [Image Optimizations](../04-performance/06-image-optimizations.md) | ShortPixel, EWWW, Converter for Media |
| Database maintenance | [Database Optimization](../04-performance/07-database-optimizations.md) | WP-Sweep, Index WP MySQL For Speed |
| Caching | [PHP Optimization](../04-performance/02-php-optimization.md) | Redis Object Cache, LiteSpeed Cache |
| Security | [Cloudflare Hardening](../03-security/01-cloudflare-hardening.md) | Two-Factor, Simple Cloudflare Turnstile |
| SEO | [Technical SEO](../05-seo/01-technical-seo-fundamentals.md) | Rank Math, Slim SEO, SEOPress |
| WooCommerce | [WooCommerce Performance](../06-e-commerce/03-woocommerce-performance.md) | Disable Cart Fragments |
| Debugging | [Debugging & Profiling](../04-performance/10-debugging-profiling.md) | Query Monitor, Code Profiler |
| Payment | [Payment Gateways](../06-e-commerce/05-payment-gateways.md) | Stripe, PayPal official plugins |

---

## Quick Reference: Recommended Stacks

### Minimal Blog

```
Plugins (5):
├── Rank Math (SEO)
├── ShortPixel (images)
├── Redis Object Cache (if Redis available)
├── UpdraftPlus (backup)
└── Query Monitor (dev only)
```

### Business Site

```
Plugins (7):
├── Rank Math (SEO)
├── ShortPixel (images)
├── WP Rocket or LiteSpeed Cache
├── WP Mail SMTP
├── Solid Security
├── UpdraftPlus (backup)
└── Query Monitor (dev only)
```

### WooCommerce Store

```
Plugins (10):
├── WooCommerce
├── Payment gateway (Stripe/PayPal)
├── Rank Math (SEO)
├── ShortPixel (images)
├── WP Rocket or LiteSpeed Cache
├── Redis Object Cache
├── Disable Cart Fragments AJAX
├── WP-Sweep (database cleanup)
├── UpdraftPlus (backup)
└── Query Monitor (dev only)
```

## Further Reading

- [Hosting Selection](./02-hosting-selection.md) — Host-provided functionality vs plugins
- [Performance Optimization](../04-performance/README.md) — Measuring plugin impact
- [Debugging & Profiling](../04-performance/10-debugging-profiling.md) — Query Monitor usage
- [WooCommerce Performance](../06-e-commerce/03-woocommerce-performance.md) — Store-specific optimizations
