# Deployment & Configuration Management

> Last reviewed: 2026-07
> Tested with: Git-based WordPress theme/plugin and WP-CLI workflows; hosting-specific release tools differ.
> Risk: High — a deployment can change live code, schema and customer-facing behavior.

Deployment is the controlled movement of a verified change into production. It
is not simply uploading files. A reliable process makes each change traceable,
keeps environment-specific configuration out of the codebase, validates the
release and gives the team a practical rollback path.

For local development tooling, code quality and team collaboration, also see
[Development Workflow](../04-performance/05-development-workflow.md).

## Separate Environments

At minimum, keep local development, staging and production distinct. They should
not share credentials, payment keys, mail recipients or databases.

| Environment | Purpose | Data and integrations |
|-------------|---------|-----------------------|
| Local | Fast development and experiments | Synthetic or anonymized data; sandbox services |
| Staging | Release candidate and regression testing | Sanitized copy where possible; sandbox or blocked integrations |
| Production | Real users and transactions | Live data and approved production services |

Set `WP_ENVIRONMENT_TYPE` correctly for every install. Use it to make unsafe
behavior visible, such as a staging banner or disabled outbound mail, but do not
rely on it as the only protection against accidental sends.

```php
// wp-config.php, supplied per environment and never committed with secrets.
define( 'WP_ENVIRONMENT_TYPE', 'staging' );
define( 'WP_DEBUG', false );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', false );
```

## Configuration and Secrets

Version-control application code and reviewed configuration templates, not
environment secrets. A deployed release should be reproducible from a Git tag
or commit plus documented environment configuration.

Keep these outside the repository or inject them through your host, CI secret
store or a protected configuration file:

- Database credentials and WordPress salts
- SMTP, payment, webhook and API keys
- Object-cache credentials
- Cloud storage and backup credentials
- Private license keys and service-account files

Use a committed example file only when it contains placeholders:

```text
# .env.example — safe to commit
WP_ENVIRONMENT_TYPE=staging
DB_NAME=replace_me
DB_USER=replace_me
DB_PASSWORD=replace_me
```

Do not log secrets, paste them into tickets or copy a production `wp-config.php`
to staging. If a secret enters a repository, treat it as exposed: revoke or
rotate it, then remove it from history according to the repository's security
process.

## What Belongs in a Release

Define this per project. A typical release contains custom theme/plugin code,
compiled frontend assets, dependency lock files and reviewed configuration
changes. It usually does not contain live uploads, cache files, generated logs
or the production database.

Before automating a deployment, document these decisions:

| Item | Decide explicitly |
|------|-------------------|
| `wp-content/uploads` | Persistent shared storage; never overwrite during a routine code deploy |
| WordPress core and vendor dependencies | Who updates them, how versions are pinned and how integrity is verified |
| Database changes | Migration owner, backup point, compatibility and rollback approach |
| Cache | Which layers must be purged after release |
| Scheduled jobs | Whether cron workers must be paused or resumed |
| Plugins/themes | Whether updates occur through code, Composer, WP-CLI or the host |

## Prepare a Release

Use a short release record. It can live in a pull request, ticket or changelog,
but it must name the exact commit or version being deployed.

1. **Scope the change.** State user impact, dependencies, feature flag status
   and whether database changes are involved.
2. **Review and test.** Run automated checks; test the intended behavior and
   relevant regressions on staging with production-like PHP and database
   versions.
3. **Create a recovery point.** Confirm a recent backup and take a pre-release
   database snapshot for changes that can alter data.
4. **Choose the timing.** Avoid peak traffic and staff the release when a rapid
   rollback would be harmful or difficult.
5. **Prepare validation.** Write the small set of browser, admin, API, checkout,
   email or cron checks that prove the release works.
6. **Announce ownership.** One person deploys; another person can help validate
   or communicate if necessary.

For a change that affects orders, subscriptions, payment logic or irreversible
data, agree on the rollback strategy before merge. A code rollback alone cannot
undo a schema migration or an email already sent.

## Deploy in Small, Observable Steps

The exact commands depend on the host. The sequence matters more than a generic
copy-paste deployment script.

```bash
# Examples only: run from the production document root after confirming
# the environment, branch/tag and maintenance window.
wp core is-installed
wp plugin status
wp option get siteurl

# After the release, clear only the cache layers your project uses.
wp cache flush

# Confirm scheduled events remain registered; do not blindly run all events.
wp cron event list --due-now
```

Recommended sequence:

1. Put the release identifier in the log or deployment record.
2. Enable a short maintenance response only when the change cannot be safely
   applied while requests are served.
3. Deploy the immutable code artifact or checked-out release.
4. Run the documented, idempotent migration if one exists.
5. Clear the application, object and CDN caches that can serve stale assets or
   templates.
6. Run the prepared smoke tests while monitoring error logs and uptime checks.
7. Remove maintenance mode and continue enhanced monitoring for a defined period.

Never combine an unreviewed WordPress-core update, several plugin updates, a
theme redesign and a database migration in one release. Small releases make
cause and rollback understandable.

## Database Changes Need Their Own Plan

Database changes are often the point where a simple rollback fails. Before any
schema or data migration, answer these questions:

- Is the migration idempotent and safe to rerun?
- Is the new code compatible with both old and new schema during rollout?
- Is a backup sufficient, or would restoring it discard new orders/content?
- Can the change be split into an additive migration, a backfill and a later
  cleanup release?
- Who reconciles records created while a rollback is in progress?

Prefer an **expand–migrate–contract** approach for important systems:

1. Add the new field/table/index without removing the old one.
2. Deploy code that can read the old and new format; backfill in controlled
   batches.
3. Verify behavior and data.
4. Remove the old structure only in a later release when it is safe.

The [Database Migrations](../08-plugin-development/11-database-migrations.md)
chapter covers WordPress plugin migration patterns; this chapter covers the
release discipline around them.

## Validate and Roll Back

Immediately after deployment, validate the actual user path—not just a 200 HTTP
response:

- [ ] Homepage and one uncached key page render correctly
- [ ] Administrator login and a relevant edit/save operation work
- [ ] Critical forms, API endpoints and scheduled jobs respond as expected
- [ ] WooCommerce checkout uses the intended payment mode; no real test charge
- [ ] Error logs, uptime monitor and browser console show no new failures
- [ ] New assets have loaded after cache/CDN purge

Define the rollback trigger in advance: for example, checkout failure, fatal
error rate above baseline or a failed smoke test. Roll back to the last known
good artifact, purge affected caches and rerun the validation list. If data was
changed, stop and use the pre-agreed reconciliation plan rather than restoring a
database blindly.

Record the release result, validation evidence and any follow-up task. This
turns a deployment into an operational learning loop.

## Common Mistakes

| Mistake | Better approach |
|---------|-----------------|
| Editing production through the theme editor or FTP | Deploy a reviewed, traceable artifact |
| Sharing staging and production keys | Use separate credentials and sandbox integrations |
| Keeping secrets in Git | Use a secret store or protected environment configuration |
| Treating a database migration like a file change | Plan compatibility, backup and reconciliation separately |
| Deploying without observability | Prepare smoke tests, logs and rollback triggers first |
| Assuming cache purge fixes every release | Validate code, data, assets and external integrations |

## Further Reading

- [Backups & Disaster Recovery](./09-backup-disaster-recovery.md) — Recovery objectives and restore drills
- [Development Workflow](../04-performance/05-development-workflow.md) — Local tooling, Git and testing practices
- [Database Migrations](../08-plugin-development/11-database-migrations.md) — Plugin schema migration patterns
- [WP-CLI](https://developer.wordpress.org/cli/commands/) — Official command reference
