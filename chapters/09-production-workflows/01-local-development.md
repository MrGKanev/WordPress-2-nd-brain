# Local Development Environments

A local environment should resemble production closely enough that a change can be tested before it reaches users. Docker-based tooling, DDEV or `wp-env` can provide repeatable PHP, database, web-server and WordPress versions.

## Baseline

- Keep project dependencies in Composer and lock their versions.
- Store safe configuration defaults in version control; keep secrets in environment variables or an untracked local file.
- Use an anonymized database snapshot and non-production API credentials.
- Document the one command that starts the project, imports data and runs checks.

## Before Production

Verify that the local environment uses compatible PHP and database versions, has the expected plugins and theme, and does not send real email, payments or webhooks. A reproducible environment makes a bug report something another developer can actually reproduce.

## A Practical Project Shape

The environment does not need to imitate every production service on day one. It does need to make the important assumptions explicit. A useful project normally defines:

| Concern | Keep reproducible | Keep outside version control |
|---------|-------------------|------------------------------|
| Application | WordPress version, theme, plugins, Composer lockfile | Production-only vendor credentials |
| Services | PHP, database and web-server versions | Production database dump |
| Configuration | Sample environment file and documented defaults | API keys, SMTP password and payment secrets |
| Data | Sanitized fixture or import procedure | Customer, order and subscriber data |

Use a `.env.example` file to list required variables without their values. A new developer should be able to copy it, provide local credentials and start the site without asking which hidden settings are required.

## Safe Local Integrations

Local development must not affect customers or third-party systems. Configure separate sandbox keys for payment providers, an email catcher or log transport for mail, and mock endpoints for webhooks where practical. Add a visible environment indicator in the admin area so a developer does not mistake a local site for production.

For a WooCommerce store, also disable live payment methods, prevent outbound fulfillment requests and avoid importing customer data unless it has been anonymized. If a production-like database is necessary for a hard-to-reproduce issue, restrict access, remove sensitive fields and delete the copy after the investigation.

## Working Agreement

Document a small set of commands in the repository README:

```bash
# Examples — adapt these to the project's chosen tool
composer install
docker compose up -d
wp core install --url=http://localhost:8080 --title="Local site"
wp plugin activate --all
```

The exact tooling can change. The important promise is that the documented steps create the same result on every machine. Treat a manual server tweak as a defect in that process: either capture it in code or document why it is intentionally exceptional.

## Configuration by Environment

Use the same codebase in every environment and vary only the configuration that must differ. Typical environment-specific values are site URLs, database connection details, cache endpoints, mail transport, third-party credentials and debugging settings.

```php
// Example: do not enable production debugging by accident.
if ( getenv( 'WP_ENVIRONMENT_TYPE' ) === 'production' ) {
	define( 'WP_DEBUG', false );
} else {
	define( 'WP_DEBUG', true );
	define( 'WP_DEBUG_LOG', true );
}
```

Keep the configuration mechanism simple and make the production default the safest one. A developer should opt into verbose logging or a sandbox integration, not need to remember to opt out before deployment.

## Test Data and Resetting State

Reliable test data is more useful than a large, stale production copy. Create fixtures for the cases the project actually supports: a basic editor account, a subscriber, a variable product, a discounted cart, a failed payment and an order needing fulfilment.

Provide a reset process for databases, uploads and queue state. A test environment that accumulates old orders, expired sessions and unknown plugin settings eventually stops being trustworthy. Resetting it between major test runs also makes failures easier to reproduce.

## Troubleshooting Parity Gaps

When a bug happens only in production, compare assumptions in this order:

1. PHP, database and WordPress versions.
2. Active plugins, theme revision and must-use plugins.
3. Environment configuration, object cache and page-cache behavior.
4. Traffic, cron/queue timing and external API responses.
5. Production-only data shape or permissions.

Avoid fixing a production-only issue by changing the local environment until it no longer resembles production. Capture the difference, decide whether it is intentional, then improve the environment or deployment process accordingly.
