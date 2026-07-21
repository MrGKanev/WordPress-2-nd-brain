# Audit Templates

Audits turn a broad concern into evidence, findings and owned follow-up work. Use these templates as a starting point; tailor the depth to the site's risk and complexity.

## Performance Audit

**Scope:** key public pages, logged-in paths, checkout/admin paths and background jobs.

- [ ] Measure cold and warm response times for representative pages.
- [ ] Review Core Web Vitals or real-user performance data.
- [ ] Inspect slow database queries, PHP-FPM saturation and cache hit ratio.
- [ ] Verify page-cache exclusions and WooCommerce cookie bypasses.
- [ ] Review image sizes, third-party scripts and unused frontend assets.
- [ ] Check cron/Action Scheduler backlog and failed actions.

For each finding, record the affected journey, evidence, likely cause, recommended action, owner and expected impact. Do not rank findings only by a synthetic score; a slow checkout usually matters more than a minor landing-page optimization.

## Security Audit

- [ ] Confirm supported WordPress, PHP, plugins and themes.
- [ ] Review administrator accounts, passwords, MFA and integration tokens.
- [ ] Inventory active extensions, must-use plugins and Composer dependencies.
- [ ] Verify backups, restore testing, logging and incident contacts.
- [ ] Check file permissions, debug settings, public endpoints and security headers.
- [ ] Review data flows for forms, analytics, payment and external integrations.

Security findings need a severity, exposure description, mitigation and target date. Avoid claiming a site is "secure"; the useful output is a prioritized and verifiable risk-reduction plan.

## Accessibility Audit

- [ ] Test keyboard navigation and focus order on primary journeys.
- [ ] Check semantic structure, headings, landmarks, labels and error messages.
- [ ] Test responsive reflow, zoom, contrast and visible focus states.
- [ ] Scan representative pages with an automated accessibility tool.
- [ ] Test menus, dialogs, forms and checkout with a screen reader.
- [ ] Review reusable blocks and components, not only one page.

Write the issue, affected users, reproduction steps, severity and component owner. Link repeated page-level defects to the shared component that should be fixed.

## Audit Output Format

| Priority | Finding | Evidence | Owner | Target date | Verification |
|----------|---------|----------|-------|-------------|--------------|
| High | Checkout error lacks announcement | Keyboard/screen-reader test | Store team | Date | Repeat test passes |

Close a finding only after verification. A task marked complete without retesting is an assumption, not an audit result.
