# Lab: Verify a Release

This lab turns a deployment into an observable, reversible operation. Run it after a staging or production release with an agreed owner and rollback path.

## Release Flow

```text
Approved artifact
  → deploy
  → health checks
  → primary user journey
  → monitor rollback window
  → record outcome
```

## Verification Checklist

- [ ] Record the release identifier and deployment time.
- [ ] Confirm public homepage/page rendering and expected static assets.
- [ ] Confirm login or administrator access where relevant.
- [ ] Exercise the most valuable workflow: form, search, checkout or API action.
- [ ] Check error tracking, queue health and cache/origin behavior.
- [ ] Confirm the previous release can still be restored.

For a store, use a sandbox payment in staging; do not create unplanned production charges merely to prove a deployment succeeded. For a migration, confirm both new data and a recovery path before removing old structures.

## Record the Result

Add a short entry to [CHANGELOG.md](../../CHANGELOG.md) or the operational changelog: release ID, validation performed, monitoring window and any follow-up work. This is the evidence needed to correlate a later incident with a change.

See [Release & Upgrade Playbooks](../09-production-workflows/16-release-upgrade-playbooks.md).
