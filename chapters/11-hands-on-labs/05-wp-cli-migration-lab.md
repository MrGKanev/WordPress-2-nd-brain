# Lab: Run a Safe WP-CLI URL Migration

This lab rehearses a common migration operation without corrupting serialized WordPress data. Run it on staging first and take a verified backup before any non-dry-run command.

## Dry Run

```bash
wp search-replace 'https://old.example' 'https://new.example' \
  --all-tables-with-prefix --skip-columns=guid --dry-run
```

Read the count and affected tables. A surprising number of rows often indicates cached data, logs or a plugin table that needs separate review. `--skip-columns=guid` is a conservative default for a standard site move; document a different policy if feeds or integrations require it.

## Execute and Validate

```bash
wp search-replace 'https://old.example' 'https://new.example' \
  --all-tables-with-prefix --skip-columns=guid
wp cache flush
wp rewrite flush --hard
```

Then test representative pages, media, login, forms, canonical URLs, redirects and an order flow for stores. Do not use a raw database search-and-replace: serialized values can break when string lengths change.

## Rollback

Restore the verified database backup if the migration produces unexpected data changes. A second reverse replacement is not a reliable rollback for every changed value.

See [Migrations & Data Lifecycle](../09-production-workflows/09-migrations-data-lifecycle.md).
