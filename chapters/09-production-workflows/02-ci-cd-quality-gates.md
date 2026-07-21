# CI/CD & Quality Gates

Continuous integration turns routine checks into a requirement for every change. Continuous delivery makes releases repeatable rather than a sequence of manual server edits.

## Minimum Pipeline

1. Install the locked dependencies.
2. Run coding-standard, static-analysis and automated test checks.
3. Build the deployable artifact without development-only files.
4. Deploy to staging, run smoke tests, then promote to production.

Every release needs a recorded version, a deployment log and a rollback path. Start small: even a pipeline that only validates PHP syntax, coding standards and the book build prevents many avoidable mistakes.

## Useful Gates

- PHP_CodeSniffer with WordPress standards
- PHPStan or another static analyzer for custom PHP
- Unit, integration and browser tests for critical flows
- A visual or functional smoke test after deployment

## A Release Flow

Use the same artifact through staging and production. Rebuilding between environments creates the possibility that production contains code which staging never tested.

```text
Pull request
  → automated checks
  → review and approval
  → immutable build artifact
  → staging deployment + smoke tests
  → production deployment
  → health check and monitored rollback window
```

For WordPress, the artifact should normally include custom themes, custom plugins and Composer-managed dependencies. Uploads, runtime caches and environment-specific configuration should not be overwritten by the deployment unless they are explicitly managed elsewhere.

## Deployment Safety

Database migrations need special treatment. Code can usually be rolled back quickly; a destructive schema or data change may not be reversible after real requests have used it. Prefer additive changes first: add the new structure, deploy code that can use both forms, migrate data in batches, then remove the legacy form in a later release.

Before deploying, define:

- the health endpoint or user flow that proves the release works;
- the exact command or release identifier used for rollback;
- the owner who decides whether to roll back;
- the time window during which errors and conversion signals are watched.

## Pull-Request Checklist

- [ ] The change has an issue, purpose or acceptance criteria.
- [ ] Custom PHP passes linting, standards and static analysis.
- [ ] Critical behavior has automated coverage or a documented manual test.
- [ ] New configuration is documented without exposing a secret.
- [ ] Database, cache and background-job effects are considered.
- [ ] The rollback behavior is understood.

CI is valuable even when the deployment is still manual. Start by making the checks trustworthy; automate promotion only after the team can explain what each gate protects.

## Deployment Strategies

Choose a strategy that matches the project's ability to roll back:

| Strategy | Suitable when | Main requirement |
|----------|---------------|------------------|
| In-place deploy | Small site and short maintenance tolerance | Verified backup and atomic file switch where possible |
| Release directories | A server can keep current and previous releases | Shared uploads/configuration and a symlink switch |
| Blue/green deployment | High availability is important | Traffic switch and compatible database changes |

Do not copy a theme over live files one by one. Visitors can receive a mixture of old PHP, new CSS and missing assets. Build the release first, then switch the active release as one operation.

## Database Changes in CI/CD

Track custom schema and data migrations in code with a unique identifier and an explicit version. A migration should be safe to rerun or should record that it completed successfully. For large tables, process rows in small batches through a background job; do not turn a request or deployment into a multi-minute database lock.

Keep compatibility during a staged release:

```text
Release 1: add new field/table and deploy code that reads both forms
Release 2: backfill data in controlled batches
Release 3: read only the new form after verification
Release 4: remove old data in a separate, recoverable change
```

This pattern reduces the chance that rolling back application code leaves it unable to read the database.

## Post-Deployment Verification

Automate what is safe to automate: HTTP checks, login page availability, a public-page render, a non-destructive API call and queue health. Then perform a short human check for the most valuable flow. Save the release version with the check result so a later incident can be correlated with a deployment.
