# Editorial Review Backlog

This page tracks high-risk or version-sensitive material separately from tested
compatibility claims. A documentation review is not a staging test.

Every chapter now declares its state: reviewed pages carry dated metadata and
legacy pages carry an explicit `Review status: Unverified` warning. CI rejects
new chapter files without one of those markers.

## Documentation Review Completed 2026-09

| Area | Pages reviewed | Result |
|------|----------------|--------|
| Deployment | `02-maintenance/10-deployment-configuration-management.md`, `04-performance/05-development-workflow.md` | Assumptions and rollback risk made explicit; official WordPress references added |
| Security | `03-security/01-cloudflare-hardening.md`, `03-security/02-server-hardening.md` | Cloudflare references updated; unsafe ownership, firewall reset and obsolete header guidance corrected |
| Performance | `04-performance/02-php-optimization.md`, `04-performance/03-php-fpm-optimization.md` | Unsupported benchmark multipliers removed; measurement requirements added |
| Commerce | `06-e-commerce/03-woocommerce-performance.md`, `06-e-commerce/04-checkout-customization.md` | HPOS, Action Scheduler and Checkout Blocks guidance aligned with official documentation |
| Integrations | `06-e-commerce/05-payment-gateways.md`, `06-e-commerce/07-woocommerce-rest-api.md` | Volatile pricing and PCI claims removed; credential and rate-limit guidance hardened |

## Remaining Validation

The pages now state that their 2026-09 review was documentation-only. Before a
specific recommendation is labelled "tested with", run its representative
commands and flows on a disposable or staging WordPress installation and record
the exact WordPress, PHP, WooCommerce and vendor versions. See
[EDITORIAL-GUIDE.md](EDITORIAL-GUIDE.md).
