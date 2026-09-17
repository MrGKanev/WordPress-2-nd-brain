# Changelog

All notable changes to this book are recorded here. Entries describe changes to the published reference, not every editorial typo fix.

## Unreleased

### Added

- Production Workflows & Advanced Topics, including release, incident, cache, migration and observability guidance.
- Platform Architecture & Governance, including block themes, content modeling, integrations, privacy and access management.
- Hands-on labs for a site plugin, webhook processing, cache validation and release verification.

### Changed

- The book build is pinned to the current mdBook version listed in `.mdbook-version`.
- CI validates generated navigation, internal links and the rendered HTML book.
- High-risk deployment, security, PHP and WooCommerce pages now distinguish documentation review from staging tests and avoid unsupported performance, pricing and compliance claims.

### Fixed

- CI can execute the downloaded mdBook binary and validates links after rendering.
- Section links resolve to generated `index.html` pages, and project documentation is included in the book.
- The orphaned theme-versus-plugin note is incorporated into the plugin structure chapter.
- Local and release PDF builds share the pinned mdBook, cover, print stylesheet and TOC pipeline.
- GitHub Pages validates navigation and rendered links before deployment.
- Unreviewed chapters are explicitly labelled, while volatile vendor pricing and limits are no longer presented as durable facts.

## Changelog Rules

- Add an entry for a new chapter, a materially changed recommendation or an upgrade that affects readers.
- Link to an issue, pull request or decision record when one exists.
- Use **Added**, **Changed**, **Deprecated**, **Removed**, **Fixed** and **Security** headings when applicable.
