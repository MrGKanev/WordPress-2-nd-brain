# Compatibility Matrix & Upgrade Policy

WordPress projects are combinations of core, PHP, database, WooCommerce, plugins, themes and infrastructure. A compatibility matrix makes those combinations visible before an update becomes an emergency.

## What to Track

Maintain one matrix per application, ideally in the repository or a shared operational document:

| Component | Current | Supported target | Owner | Validation |
|-----------|---------|------------------|-------|------------|
| WordPress core | Recorded deployed version | Approved upgrade line | Platform owner | Staging smoke test |
| PHP runtime | Recorded deployed version | Hosting-supported version | Platform owner | Plugin/theme tests |
| WooCommerce | Recorded deployed version | Approved upgrade line | Store owner | Checkout and HPOS tests |
| Theme/custom plugins | Release tag or commit | Tested release | Development owner | Automated + manual tests |
| Critical extensions | Exact version | Vendor-supported version | Feature owner | Critical journey test |

Do not rely on a vague label such as "latest". Record the exact deployed version and the date it was verified. The matrix is useful only when it reflects reality.

## Support Policy

Define how long each project remains on a version and what triggers an upgrade:

- Security fixes: expedited assessment and deployment path.
- Routine updates: scheduled staging test and release window.
- Major versions: compatibility assessment, migration plan and rollback criteria.
- End-of-life runtimes: upgrade project with a business owner and a deadline.

An old PHP version or abandoned plugin is not simply technical debt; it can block security updates across the whole stack. Flag unsupported components early, while replacement options still exist.

## Upgrade Sequence

Change one major compatibility boundary at a time where possible. For example, update PHP on staging, resolve compatibility problems, then update WordPress or WooCommerce in a later controlled release. Combining several major updates makes a regression difficult to attribute and a rollback difficult to scope.

For a WooCommerce store, test these before approving an upgrade:

- product browsing, variations, coupons, cart and checkout;
- payment authorization and webhook confirmation;
- order admin, refunds, emails and background actions;
- subscriptions, bookings, tax and shipping extensions if present;
- HPOS and Cart/Checkout Block compatibility.

## Review Cadence

Review the matrix monthly for critical sites and before a campaign, host migration or PHP change. Record the test environment, tester and result. A matrix becomes a decision tool when it answers: "Can we safely make this upgrade now, and how do we prove it?"
