# Lab: Add a Playwright Smoke Test

This lab adds a minimal browser test for a public page. Run it against a local or staging URL, never against a production checkout that could trigger real integrations.

## Test File

Install Playwright in a separate test project, set `SITE_URL`, then create `tests/public-page.spec.js`:

```javascript
import { test, expect } from '@playwright/test';

const siteUrl = process.env.SITE_URL || 'http://localhost:8080';

test('homepage renders a visible main heading', async ({ page }) => {
  await page.goto(siteUrl, { waitUntil: 'networkidle' });
  await expect(page.locator('main h1')).toBeVisible();
});
```

Run it with:

```bash
SITE_URL=https://staging.example.com npx playwright test
```

## Extend Safely

Add one test per critical journey: a public page, search, a form validation error and, on staging, cart/checkout behavior with sandbox payment. Keep selectors based on accessible roles, labels or stable test IDs rather than fragile CSS layout classes.

Save screenshots, traces or videos only for failures and make sure artifacts do not contain customer data or credentials.

See [E2E Testing & Visual Regression](../08-plugin-development/15-e2e-testing-visual-regression.md) and [Accessibility Quality Assurance](../09-production-workflows/05-accessibility-quality.md).
