# Lab: Rehearse a Release & Rollback

This lab turns a release checklist into a safe rehearsal. Use staging and a harmless version change such as a visible template string or a non-critical plugin release.

## Before the Rehearsal

- Record the current commit or release artifact.
- Confirm the previous artifact can be selected or deployed.
- Define a health check and one primary user journey.
- Identify cache purge, migration or queue actions the release requires.

## Exercise

```text
Deploy approved artifact
  → run health check
  → verify primary journey
  → inspect errors and cache behavior
  → deploy previous artifact
  → repeat the same checks
```

Time both deployment and recovery. Record unclear steps, missing credentials and checks that depended on one person's memory. Those are the real findings of the lab.

## Completion Criteria

The team can identify the running version, prove the new release works and restore the previous release without editing live files manually. If a database migration is involved, rehearse an additive migration or restore plan rather than assuming application-code rollback is enough.

See [CI/CD & Quality Gates](../09-production-workflows/02-ci-cd-quality-gates.md) and [Release & Upgrade Playbooks](../09-production-workflows/16-release-upgrade-playbooks.md).
