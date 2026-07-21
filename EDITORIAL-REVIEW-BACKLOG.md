# Editorial Review Backlog

This backlog identifies high-risk or version-sensitive material that should receive verified review metadata before a broad editorial pass. It deliberately does not claim an unverified test result.

## First Review Wave

| Area | Pages to review | Evidence needed |
|------|-----------------|-----------------|
| Deployment | `02-maintenance/10-deployment-configuration-management.md`, `04-performance/05-development-workflow.md` | Supported deployment commands, rollback and host assumptions |
| Security | `03-security/01-cloudflare-hardening.md`, `03-security/02-server-hardening.md` | Current vendor settings, TLS and operating-system guidance |
| Performance | `04-performance/02-php-optimization.md`, `04-performance/03-php-fpm-optimization.md` | Supported PHP versions, pool settings and measured assumptions |
| Commerce | `06-e-commerce/03-woocommerce-performance.md`, `06-e-commerce/04-checkout-customization.md` | WooCommerce/Blocks/HPOS compatibility and checkout tests |
| Integrations | `06-e-commerce/05-payment-gateways.md`, `06-e-commerce/07-woocommerce-rest-api.md` | Provider API versions, authentication and webhook behavior |

## Review Method

For each page, verify primary documentation, test representative commands in staging where possible, add review metadata only after evidence exists, and create a changelog entry for material reader-facing corrections. See [EDITORIAL-GUIDE.md](EDITORIAL-GUIDE.md).
