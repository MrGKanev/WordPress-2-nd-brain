# Multilingual WordPress Sites

Multilingual projects need a source-of-truth language, a translation workflow and consistent URLs—not just a language switcher. Content, media, menus, strings, SEO metadata and WooCommerce data all need an explicit ownership model.

## Design Decisions

- Choose URL structure early: subdirectories, subdomains or separate domains.
- Define which content is translated manually and which is synchronized from the source language.
- Keep language-specific SEO metadata, canonical URLs and `hreflang` annotations accurate.
- Test navigation, search, emails and transactional WooCommerce screens in every supported language.

Translation plugins reduce implementation work but do not resolve content governance. A release checklist should include changed strings, redirected URLs and language-specific page-cache behavior.

See [International SEO](../05-seo/05-international-seo.md) and [Internationalization](../08-plugin-development/07-internationalization.md).

## Translation Model

Decide whether each content type is a translation, a localized adaptation or shared global data. Product names and legal terms may need independent editorial control; stock, SKU and order state often remain shared. Write this down before configuring the translation plugin, because the data model influences permissions, APIs and imports.

Use a stable source-language workflow:

```text
Source content drafted
  → reviewed and published
  → translation task created
  → localized content reviewed
  → language pages published together or tracked as incomplete
```

Avoid silently copying a source page as if it were a finished translation. The translation status should be visible to editors and support staff.

## Technical Checklist

- Add `hreflang` values only for equivalent, indexable pages.
- Give every language its own canonical URL and XML sitemap entries.
- Translate page titles, descriptions, Open Graph data, menus and image text where relevant.
- Keep locale-specific currency, tax, date and address formats consistent with business rules.
- Include every language in redirects, search, error pages and cache tests.

For a multilingual store, test a shopper who switches language with items in the cart. Decide intentionally whether the cart, pricing, coupons and account session are shared or language-specific; do not leave this behavior to whichever plugin happens to run first.

## Custom Code

All user-facing strings in a theme or plugin should use WordPress internationalization functions and a stable text domain. Avoid building translated sentences by concatenating fragments, because word order and plural rules differ between languages. The code should expose a complete meaning to translators, not just isolated words.

## Release Checklist for a New Language

Adding a language is a release, not a configuration toggle. Use a checklist that covers the visitor journey:

- [ ] Language selector is reachable, named clearly and preserves the equivalent page where possible.
- [ ] Homepage, navigation, search, contact details and legal pages are translated or deliberately unavailable.
- [ ] Metadata, sitemaps, canonicals and `hreflang` URLs have been checked in the rendered HTML.
- [ ] Forms, validation messages, cookie-consent text and transactional emails are localized.
- [ ] Analytics, error reporting and support workflows can identify the active locale.
- [ ] Cache and CDN variants use the language URL as part of the cache key.

Do not point a language selector to a generic homepage when an equivalent translation is missing without signaling that behavior. It is usually better to show a clear fallback than to make a visitor believe they are reading the matching page.

## Translation Quality and Change Management

Create a glossary for product names, formal/informal address, legal wording and technical terms. This gives translators and support staff one consistent vocabulary. Keep a short style guide with capitalization, punctuation and date/number conventions for each locale.

When the source changes after translation, identify whether the change is editorial, legal, commercial or structural. Legal and price-related changes often require immediate translation review; a small typo may not. Tracking this distinction prevents a source update from silently invalidating every translated page.
