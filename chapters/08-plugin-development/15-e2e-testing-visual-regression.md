# E2E Testing & Visual Regression

> Last reviewed: 2026-07
> Tested with: Playwright and the WordPress Playwright test-utilities approach; pin tool versions in each project.
> Risk: Medium — test setup can create data or trigger integrations if it points at a real environment.

Unit and integration tests prove that code behaves in controlled conditions.
End-to-end (E2E) tests prove that a user can complete a workflow in a running
browser: edit content, save settings, submit a form or complete checkout. Visual
regression adds a second check: has the rendered page changed meaningfully?

Use E2E tests for the small set of workflows whose failure would be expensive or
embarrassing. Do not try to automate every click in the WordPress admin.

## What to Test

| Test level | Best for | Avoid using it for |
|------------|----------|--------------------|
| Unit | Pure functions and calculations | Browser and WordPress integration |
| Integration | Hooks, REST callbacks, permissions | Pixel-level UI behavior |
| E2E | Critical user journeys across browser, UI and server | Every edge case |
| Visual regression | Layout and template regressions | Dynamic or variable content |

Good initial E2E candidates are a plugin settings page, a custom block that
renders on the frontend, a critical public form, or a WooCommerce purchase path.
Keep permission permutations and data edge cases in PHPUnit; E2E should give
confidence in the journeys a customer or editor actually uses.

## Use a Disposable Environment

Never aim browser tests at production. They can create posts, orders, accounts,
uploads and email.

- Use a dedicated local, Docker or CI environment and test database.
- Disable real mail, payment, fulfillment, analytics and webhooks.
- Use sandbox gateways and clearly labelled test products for WooCommerce.
- Seed only the fixtures needed by the scenario; reset state between tests.
- Run the PHP/WordPress/WooCommerce versions that matter for the release, not
  only "latest".

`wp-env`, DDEV, Docker Compose and host-provided ephemeral environments can all
work. Repeatability matters more than the specific tool.

## Playwright Setup

Playwright provides browser automation, parallel execution, traces, videos,
screenshots and snapshot comparisons. WordPress has migrated its E2E work to
Playwright; `@wordpress/e2e-test-utils-playwright` adds admin, editor and
request helpers for WordPress workflows.

```bash
npm install --save-dev @playwright/test @wordpress/e2e-test-utils-playwright
npx playwright install --with-deps chromium
```

Pin these versions in the project's lock file. Do not store credentials in test
configuration; inject a dedicated test account via CI secrets or environment
setup.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:8888',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [ { name: 'chromium', use: { ...devices['Desktop Chrome'] } } ],
} );
```

## Write Stable Tests

Flaky E2E tests usually fail because of timing, animation, random fixtures or a
third-party request—not because the product is broken. Prefer user-visible,
accessible locators and Playwright's automatic waiting.

```ts
import { test, expect } from '@playwright/test';

test( 'subscriber cannot open plugin settings', async ( { page } ) => {
  // Authentication belongs in a reusable fixture or storageState, not inline.
  await page.goto( '/wp-admin/admin.php?page=my-plugin' );
  await expect(
    page.getByRole( 'heading', { name: /permission|access denied/i } )
  ).toBeVisible();
} );
```

Prefer, in order: `getByRole()`, `getByLabel()`, stable visible text, then a
deliberate `data-testid`. Avoid CSS classes, DOM-position selectors, random
product names and `waitForTimeout()`.

For block-editor tests, use WordPress's Playwright helpers rather than rebuilding
each admin interaction:

```ts
import { test, expect } from '@wordpress/e2e-test-utils-playwright';

test( 'custom block renders on the frontend', async ( { admin, editor, page } ) => {
  await admin.createNewPost();
  await editor.insertBlock( { name: 'my-plugin/notice' } );
  await editor.publishPost();
  await page.goto( '/' );
  await expect( page.getByText( 'My plugin notice' ) ).toBeVisible();
} );
```

The available helpers depend on the pinned package version. Check the official
reference while configuring a real project.

## WooCommerce Critical Paths

Use sandbox payments and assert the final state, not just a click on "Place
order":

```text
Guest opens product → adds in-stock variation → applies coupon
→ enters valid checkout data → selects sandbox payment
→ reaches confirmation → test verifies expected order state
```

Run this against the checkout type the store really uses. With Checkout Blocks,
also test validation errors, shipping changes, payment failure/retry and browser
refresh/session restoration. See [Modern WooCommerce Architecture](../06-e-commerce/12-modern-woocommerce-architecture.md).

## Visual Regression

Visual regression compares a current screenshot with an approved baseline. Use
it for deterministic, high-value pages: a product page, checkout, custom block,
homepage hero or client dashboard.

```ts
import { test, expect } from '@playwright/test';

test( 'product page keeps the approved layout', async ( { page } ) => {
  await page.goto( '/product/test-product/' );
  await expect( page ).toHaveScreenshot( 'test-product.png', {
    fullPage: true,
    animations: 'disabled',
  } );
} );
```

Baseline updates are product decisions, not a way to make CI green. Review each
difference for intentional design change, missing assets, font fallback or
unexpected third-party content. Reduce noise by fixing viewport, browser,
locale, timezone and fixtures; disable analytics and dynamic widgets; generate
baselines on the same OS/browser family as CI.

## CI and Failure Artifacts

Run a small critical E2E suite on pull requests and broader browser/version
coverage nightly or before a release. Upload traces, screenshots and the HTML
report only when a test fails.

```yaml
- name: Run browser tests
  run: npx playwright test
  env:
    E2E_BASE_URL: http://127.0.0.1:8888

- name: Upload Playwright report
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-report
    path: playwright-report/
    if-no-files-found: ignore
```

Use retries to collect a trace, not to hide defects. A recurring flake needs an
owner and investigation.

## Checklist

- [ ] E2E runs only against a disposable, integration-safe environment
- [ ] Critical editor, permission, form or checkout flow has a browser test
- [ ] Tests use semantic locators and deterministic fixtures
- [ ] Failure traces/screenshots are available in CI
- [ ] Visual baselines are reviewed deliberately
- [ ] WooCommerce tests cover the actual cart/checkout architecture

## Further Reading

- [WordPress Playwright test utilities](https://developer.wordpress.org/block-editor/reference-guides/packages/packages-e2e-test-utils-playwright/)
- [WordPress E2E testing guidance](https://developer.wordpress.org/block-editor/contributors/code/testing-overview/e2e/)
- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots)
- [Plugin Testing](./13-plugin-testing.md)
- [Modern WooCommerce Architecture](../06-e-commerce/12-modern-woocommerce-architecture.md)
