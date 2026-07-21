# Installation, Configuration & Environments

A WordPress installation becomes maintainable when code, configuration and content are treated differently. Code should be repeatable, configuration should vary safely by environment, and content should be backed up and migrated deliberately.

## Environment Model

| Environment | Purpose | Rules |
|-------------|---------|-------|
| Local | Development and debugging | Sandbox services; no real customer data |
| Staging | Release and integration validation | Production-like configuration; controlled test data |
| Production | Real traffic | Minimal debugging; monitored and backed up |

Use the same theme and plugin code path across environments. Change only connection details, URLs, credentials, cache endpoints and debug settings through environment-specific configuration.

## Configuration Principles

Keep database credentials, API keys and SMTP passwords out of Git. Provide an example configuration file that names required values without exposing them. Set safe production defaults: debug output must not appear to visitors, and mail/payment sandbox modes should be obvious outside production.

```php
define( 'WP_DEBUG_DISPLAY', false );
define( 'DB_PASSWORD', getenv( 'WORDPRESS_DB_PASSWORD' ) );
```

Validate that an environment variable exists before relying on it. A blank password or missing API key should fail deployment safely rather than connect to an unintended service.

## Installation Checklist

- [ ] Current supported WordPress and PHP versions are selected.
- [ ] HTTPS, DNS, backups and database access are configured.
- [ ] Administrator access uses an individual account and strong authentication.
- [ ] Permalinks, timezone, language and email delivery are tested.
- [ ] Staging and production have separate secrets and payment/email behavior.
- [ ] A restore and rollback path exists before importing content.

See [Local Development Environments](../09-production-workflows/01-local-development.md), [Deployment & Configuration Management](../02-maintenance/10-deployment-configuration-management.md) and [Backups & Disaster Recovery](../02-maintenance/09-backup-disaster-recovery.md).
