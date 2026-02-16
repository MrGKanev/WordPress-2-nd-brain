# International SEO

Serving content in multiple languages or targeting multiple countries requires more than translating text. Search engines need explicit signals about which language and region each page targets, and incorrect implementation can split your authority across duplicate versions or show the wrong language to visitors.

## Hreflang Tags

Hreflang tells search engines which language (and optionally, which country) a page targets, and links all versions together:

```html
<link rel="alternate" hreflang="en" href="https://example.com/" />
<link rel="alternate" hreflang="de" href="https://example.com/de/" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```

### Hreflang Rules

| Rule | Example | Notes |
|------|---------|-------|
| Language only | `hreflang="en"` | English, any region |
| Language + region | `hreflang="en-gb"` | English for UK |
| Default fallback | `hreflang="x-default"` | When no match, show this |
| Self-referencing | Required | Each page must include itself |
| Bidirectional | Required | If A points to B, B must point to A |

### Common Mistakes

| Mistake | Impact |
|---------|--------|
| Missing `x-default` | No fallback for unsupported languages |
| One-directional links | Google ignores hreflang if not reciprocal |
| Wrong language codes | `hreflang="uk"` (wrong) vs `hreflang="uk-ua"` (still wrong) vs `hreflang="en-gb"` |
| Missing self-reference | Page doesn't point to itself in the set |
| Hreflang on non-canonical URLs | Must match canonical URL exactly |

Language codes use ISO 639-1 (two-letter). Region codes use ISO 3166-1 Alpha 2. `en-us`, not `en-USA`.

## URL Structure for Multilingual Sites

| Structure | Example | Pros | Cons |
|-----------|---------|------|------|
| **Subdirectories** | `example.com/de/` | Easy setup, single domain authority | All languages share hosting |
| **Subdomains** | `de.example.com` | Can host separately | Treated as separate sites by Google |
| **ccTLDs** | `example.de` | Strong geo-signal | Expensive, separate authority per domain |
| **Parameters** | `example.com?lang=de` | Easy to implement | Google discourages, hard to crawl |

**Recommendation:** Subdirectories for most WordPress sites. Simplest to manage, keeps domain authority consolidated, and works well with all multilingual plugins.

## WordPress Multilingual Plugins

### Plugin Comparison

| Plugin | Approach | Cost | Best For |
|--------|----------|------|----------|
| **WPML** | Separate posts per language | $39-$159/year | Established sites, full translation control |
| **Polylang** | Separate posts per language | Free / $99+/year (Pro) | Budget-conscious, simpler needs |
| **TranslatePress** | Visual translation on frontend | Free / $89+/year | Non-technical users, visual editing |
| **Weglot** | SaaS-based auto-translation | From $15/month | Quick setup, low maintenance |
| **MultilingualPress** | Multisite-based (separate site per language) | $199+/year | Enterprise, full separation |

### WPML

The most established WordPress multilingual solution:

- Translates posts, pages, custom post types, taxonomies, menus, widgets
- String translation for theme and plugin strings
- Built-in translation management with translator roles
- WooCommerce multilingual support (separate currency per language)

**Performance note:** WPML adds database queries per language switch. On sites with many languages, query count can increase significantly. Use object caching.

### Polylang

A lighter alternative to WPML:

- Free version covers most needs (post/page/CPT translation, language switcher)
- Pro adds URL slug translation, duplicate content, and WooCommerce support
- Compatible with most page builders
- Similar database structure to WPML (taxonomy-based language assignment)

### TranslatePress

Different approach — translates visually on the frontend:

- See translations in context as you edit
- Auto-translation via Google Translate or DeepL API (then human review)
- Works with any theme and plugin (translates rendered output)
- SEO Pack add-on handles hreflang automatically

### Weglot

SaaS approach — translation happens outside WordPress:

- Automatic translation + human editing dashboard
- No plugin database overhead (translations stored on Weglot servers)
- Handles hreflang, sitemap, and URL structure automatically
- Content changes sync automatically

## WooCommerce Multilingual

Multilingual e-commerce adds complexity:

| Concern | What to Handle |
|---------|---------------|
| Product translations | Names, descriptions, attributes |
| Currency | Multi-currency display and checkout |
| Shipping | Different rates per country |
| Emails | Order emails in customer's language |
| Tax | VAT/tax rates per country |
| Payment | Gateways available per region |

### Multi-Currency Options

| Plugin | Currencies | Dynamic Conversion |
|--------|-----------|-------------------|
| **WPML + WooCommerce Multilingual** | Manual rates per currency | Yes |
| **Currency Switcher for WooCommerce** (Aelia) | Automatic exchange rates | Yes |
| **WooCommerce Payments** | Built-in multi-currency | Yes |

## SEO for Multilingual Sites

### Sitemap Configuration

Each language version needs its own sitemap entries with hreflang annotations:

```xml
<url>
    <loc>https://example.com/product/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://example.com/product/" />
    <xhtml:link rel="alternate" hreflang="de" href="https://example.com/de/produkt/" />
    <xhtml:link rel="alternate" hreflang="fr" href="https://example.com/fr/produit/" />
</url>
```

Both WPML and Polylang handle this automatically with Yoast SEO or Rank Math.

### Content Strategy

| Approach | Quality | Cost | Speed |
|----------|---------|------|-------|
| **Professional human translation** | Best | Highest | Slow |
| **AI translation + human review** | Good | Medium | Fast |
| **Machine translation only** | Variable | Lowest | Instant |
| **Localization** (cultural adaptation) | Best for conversions | Highest | Slowest |

**Translation is not localization.** Translating "Free shipping over $50" to German still needs the currency changed. Dates, phone formats, measurement units, cultural references — all need adaptation.

### Per-Language SEO Settings

With Yoast SEO or Rank Math:

- Set unique meta titles and descriptions per language
- Configure language-specific Open Graph images
- Submit separate sitemaps per language to Search Console
- Track rankings per language in Search Console (separate property per country/language)

## Geotargeting

### Google Search Console

For subdirectory or subdomain setups, set geographic targeting per section:

```
Search Console → Settings → International Targeting → Country
```

For ccTLDs, Google automatically associates the domain with the country.

### Cloudflare Workers for Geo-Redirect

```
Visitor from Germany → Redirect to /de/ (if not already there)
```

Be careful with auto-redirects:
- **Don't force redirects** — Show a banner suggesting the local version instead
- **Respect user choice** — If someone switches to English, don't redirect them back
- **Google crawls from the US** — Auto-redirect can prevent indexing of non-English versions

### Language Switcher Best Practices

| Practice | Why |
|----------|-----|
| Show language names in their own language | "Deutsch" not "German" |
| Don't use flags for languages | Spanish is spoken in 20+ countries |
| Place consistently (header or footer) | Users expect it in the same spot |
| Link to equivalent page, not homepage | Don't lose the user's context |

## Technical Checklist

- [ ] Hreflang tags on all translated pages (bidirectional, self-referencing)
- [ ] `x-default` hreflang set for fallback
- [ ] Canonical URLs correct per language version
- [ ] Separate XML sitemaps per language (or combined with hreflang)
- [ ] Language switcher links to translated equivalent (not homepage)
- [ ] URL slugs translated (not just content)
- [ ] Search Console property per language/country
- [ ] No automatic redirects based on IP (use suggestions instead)
- [ ] Date, currency, and number formats localized
- [ ] RTL stylesheet loaded for Arabic/Hebrew (if applicable)

## Further Reading

- [Technical SEO Fundamentals](./01-technical-seo-fundamentals.md) — Core SEO concepts
- [XML Sitemaps and Structured Data](./03-xml-sitemaps-and-structured-data.md) — Sitemap configuration
- [Tax Compliance](../06-e-commerce/10-tax-compliance.md) — International tax handling
- [Google's Hreflang Guide](https://developers.google.com/search/docs/specialty/international/localized-versions) — Official documentation
