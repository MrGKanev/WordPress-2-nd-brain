# Backups & Disaster Recovery

> Last reviewed: 2026-07
> Tested with: WordPress backup and WP-CLI workflows; adapt commands to the host and storage provider.
> Risk: High — a restore can overwrite current production data.

A backup is only a copy. Disaster recovery is the ability to restore the right
copy, within an acceptable time, without making the incident worse. Plan both
before an outage, compromise, failed update or accidental deletion occurs.

This chapter is about recovering a WordPress site. It does not replace the
evidence-preservation and cleanup steps in [Incident Response](../03-security/05-incident-response.md) when compromise is suspected.

## Define Recovery Objectives

Write down these two values for every production site before choosing a backup
schedule:

| Objective | Question | Example |
|-----------|----------|---------|
| **RPO** (Recovery Point Objective) | How much data can we lose? | At most 1 hour of orders |
| **RTO** (Recovery Time Objective) | How long can the site be unavailable? | Checkout back within 2 hours |

A brochure site may tolerate a daily RPO and a next-business-day RTO. An active
WooCommerce store generally cannot: orders, stock changes, customers and payment
events may occur between a nightly backup and an outage. State the business
decision in the client handoff or operations document; do not silently assume
that a daily backup is sufficient.

## What a Complete Backup Contains

For a conventional WordPress install, capture all of the following:

- The **database**, including all tables with the site's prefix.
- `wp-content/uploads/` for media.
- Custom themes, plugins and must-use plugins.
- `wp-config.php` or a separately documented, secure way to recreate its
  configuration and secrets.
- Server configuration that is not version-controlled: web-server vhost, PHP
  settings, cron jobs, redirects and cache configuration.
- A small recovery record: PHP version, database engine/version, document root,
  domain/DNS provider, storage location and the person with access.

Core WordPress can usually be reinstalled from a trusted release, so it need not
be the only copy of the site. However, an image-level host backup alone is not a
substitute for a documented database-and-files restore procedure.

## Design the Backup Strategy

Use the **3-2-1 rule** as a baseline: at least three copies, on two different
storage media or systems, with one copy off-site. For important sites, make the
off-site copy immutable or protected from routine deletion.

| Site type | Suggested database cadence | Suggested files cadence | Restore drill |
|-----------|----------------------------|-------------------------|---------------|
| Personal or brochure site | Daily | Daily | Every 6 months |
| Lead-generation site | Daily; before major changes | Daily | Quarterly |
| WooCommerce store | Hourly or transaction-aware | Daily plus before deploys | Quarterly and before peak periods |
| Membership or learning site | Hourly or transaction-aware | Daily | Quarterly |

These are starting points, not a vendor prescription. Match retention to legal,
contractual and business needs. Keep several restore points: a recent bad backup
is not useful after unnoticed corruption or malware.

### Storage and Access

- Keep backup storage in a separate account or provider from the production
  server where possible.
- Encrypt backups at rest and in transit; protect encryption keys separately.
- Give restore access only to the people who need it, and test that access before
  an emergency.
- Enable storage versioning or immutability where supported.
- Do not put database dumps, `.env` files or production credentials in Git.
- Alert on failed jobs and low storage capacity; "configured" is not "working".

## Before You Need a Restore

Maintain a short runbook with the facts an on-call developer would otherwise
have to discover under pressure:

```text
Site: example.com
RPO / RTO: 1 hour / 2 hours
Backup provider and account owner: …
Last successful database and file backup: …
Hosting, DNS and email contacts: …
Production PHP / database versions: …
Critical flows to test: homepage, login, contact form, checkout, webhooks
```

Store credentials in an approved password manager, not in the runbook itself.
Use the [Client Handoff](./08-client-handoff.md) process to make ownership and
emergency contacts explicit.

## Restore Drill: The Normal Way to Test Recovery

Do not test a backup by looking at a green checkmark. Restore it to an isolated
staging environment that cannot send real email, charge cards, call production
webhooks or be indexed by search engines.

1. Record the backup identifier, date and expected contents.
2. Create an isolated temporary environment with equivalent PHP and database
   versions where practical.
3. Restore files and database using the backup provider's documented process.
4. Set a temporary URL or local hosts entry. Do not point public DNS at the test.
5. Disable outbound mail and payment/webhook integrations before opening the
   restored admin.
6. Run a search-replace only against the copied database if URLs must change.
7. Test the critical flows listed in the runbook.
8. Record duration, errors, missing data and the next actions. Destroy the test
   environment and its copied personal data when finished.

For a command-line database restore, use a disposable database only:

```bash
# Destructive: imports over the database configured for this environment.
# Confirm WP_ENVIRONMENT_TYPE is not production before running.
wp db import /secure/path/backup.sql

# Check the restored site's database connection and application health.
wp core is-installed
wp option get siteurl
```

Never use `wp search-replace` with `--all-tables-with-prefix` on production as a
shortcut for a staging restore. Export and restore a copy first, then verify
serialized data and application behavior.

### Restore Drill Checklist

- [ ] Restored backup date and identifier recorded
- [ ] Production DNS, mail, payments and webhooks cannot be reached from test
- [ ] Database, uploads, custom plugins, themes and mu-plugins present
- [ ] Admin login works with a test account
- [ ] Key public pages render and media loads
- [ ] Forms do not send to real recipients
- [ ] Checkout/payment flow uses a sandbox or is disabled
- [ ] Error logs reviewed; no unexpected fatal errors
- [ ] Restore duration compared with the RTO
- [ ] Findings, owner and due date recorded

## Production Recovery Procedure

Use this only after deciding that recovery is safer than a targeted fix. For a
security incident, preserve evidence first and follow [Incident Response](../03-security/05-incident-response.md).

1. **Declare the incident.** Assign a technical owner and one person for client
   or customer communication. Note the time, symptoms and last known good state.
2. **Limit impact.** Enable maintenance mode or take the service behind a safe
   maintenance response. Do not delete logs or files during a suspected breach.
3. **Protect current state.** Take a fresh database export and file snapshot
   before overwriting anything. It may contain data created after the selected
   backup or evidence needed later.
4. **Choose the restore point.** Prefer the last known-good point, not simply the
   most recent backup. Confirm its age against the RPO.
5. **Restore in the provider's documented order.** Usually files, database,
   configuration, then cache purge. Keep maintenance mode enabled.
6. **Reapply only verified changes.** Update known-vulnerable components and
   rotate credentials after a compromise. Do not reintroduce unreviewed files.
7. **Validate before reopening.** Test public pages, admin, cache, forms,
   scheduled tasks and the site's critical business flow.
8. **Communicate and learn.** State what happened, customer impact, data-loss
   window and next update time. Afterwards, document the root cause and improve
   the runbook, schedule or monitoring.

## WooCommerce and Other Transactional Sites

Restoring a database can roll the store back while a payment provider, warehouse
or email platform still has newer events. Treat the time after the restore point
as a reconciliation problem.

- Export orders, refunds, customers and stock changes created after the backup
  before restoring when the site is still reachable.
- Compare payment-provider transactions with restored WooCommerce orders.
- Check subscriptions, renewals, gift cards, bookings and stock adjustments.
- Prevent duplicate fulfillment and duplicate customer emails while reconciling.
- Do not assume a database restore reverses actions already sent to external
  systems; it does not.

For stores with a tight RPO, use provider-supported real-time or transaction-aware
backup capabilities and rehearse reconciliation with the business owner.

## Common Mistakes

| Mistake | Better approach |
|---------|-----------------|
| Only backing up the database | Include uploads, custom code, configuration and recovery information |
| Keeping backups on the same server | Keep at least one protected off-site copy |
| Restoring directly to production for the first test | Restore to isolated staging first |
| Treating a nightly backup as enough for a store | Define the RPO from actual transaction volume |
| Forgetting outbound integrations in staging | Disable mail, payments, webhooks and indexing before testing |
| Assuming restore success equals business recovery | Reconcile orders and external systems after recovery |

## Further Reading

- [Incident Response](../03-security/05-incident-response.md) — Preserving evidence and recovering from compromise
- [Monitoring & Alerting](./07-monitoring-alerting.md) — Detecting backup failures and outages early
- [Client Handoff](./08-client-handoff.md) — Ownership, credentials and support expectations
- [WP-CLI Database Commands](https://developer.wordpress.org/cli/commands/db/) — Official command reference
