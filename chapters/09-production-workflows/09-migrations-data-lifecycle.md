# Migrations & Data Lifecycle

Moving a WordPress site involves more than copying files and tables. URLs, serialized data, media, environment configuration, scheduled jobs and third-party integrations must all be accounted for.

## Migration Plan

1. Inventory data, files, credentials, DNS and external integrations.
2. Rehearse the migration on staging with a production-like dataset.
3. Take a verified backup and define a time-bounded rollback plan.
4. Validate content, redirects, media, forms, cron, email and checkout after cutover.

Use WordPress-aware tools for URL replacement because serialized data must remain valid. Define retention periods for backups, logs and customer data, then periodically test restoration instead of assuming that a backup is usable.

See [Backups & Disaster Recovery](../02-maintenance/09-backup-disaster-recovery.md) and [Database Migrations](../08-plugin-development/11-database-migrations.md).

## Classify the Change

Not every migration has the same risk. Classify it before selecting tools and downtime:

| Change | Main risk | Typical safeguard |
|--------|-----------|-------------------|
| Domain or host move | DNS, TLS, URLs and email | Lower TTL in advance; verify redirects and mail |
| Theme or plugin replacement | Broken layout or lost settings | Parallel staging test and content inventory |
| Database/schema migration | Data loss or incompatible code | Additive migration and tested rollback |
| WooCommerce migration | Orders, stock and payments | Freeze window, reconciliation and delayed cutover |

Large stores need a plan for data that changes during the move. A one-time database copy is not enough if customers can continue placing orders. Use a short maintenance window, a final incremental sync or a verified reconciliation process.

## Validation After Cutover

Validate outcomes, not only HTTP status codes:

- login and password reset;
- representative pages, media and search;
- forms, transactional email and scheduled tasks;
- redirects from important legacy URLs;
- payment authorization, order creation and refund flow for stores;
- backups and monitoring on the new environment.

Record the validation result and the person who performed it. If a check cannot be completed before opening the site, document the risk and assign a deadline rather than quietly accepting it.

## Data Retention

Data lifecycle includes deletion as well as migration. Define how long backups, logs, failed-job payloads and exported customer data are retained, who may access them and how they are securely removed. Retention should reflect legal obligations and recovery needs; keeping every copy forever is neither a backup strategy nor a privacy strategy.

## WordPress-Aware URL Replacement

URLs often occur inside serialized WordPress options and post meta. A plain text replacement can corrupt the serialized value length and break the affected setting. Use a WordPress-aware command and rehearse it first:

```bash
# Inspect the impact before modifying the database.
wp search-replace 'https://old.example' 'https://new.example' \
  --all-tables-with-prefix --skip-columns=guid --dry-run

# Run only after a verified backup and staging validation.
wp search-replace 'https://old.example' 'https://new.example' \
  --all-tables-with-prefix --skip-columns=guid
```

Whether `guid` should change depends on the migration and feed requirements; skipping it is a conservative default for ordinary site moves. Record the chosen policy rather than treating it as a command-line habit.

## Cutover Timeline

Prepare a written timeline with named owners:

```text
T-7 days  Rehearse migration and validate backup restoration
T-1 day   Lower DNS TTL where appropriate; freeze non-essential changes
T-0       Final backup, maintenance mode or write freeze, final data sync
T+0       Switch traffic, validate critical journeys, monitor errors
T+1 day   Reconcile orders/forms and retire temporary access only when stable
```

For a store, reconcile orders and payment events that occurred around the cutover. For a content site, compare high-value URLs, redirects and search indexing signals. Keep the previous environment read-only but available for the agreed rollback window.
