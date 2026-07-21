# Review Cadence & Operational Changelog

Documentation stays useful only when it is reviewed as part of normal work. A lightweight cadence prevents version drift, unowned alerts and stale runbooks from accumulating until an incident exposes them.

## Suggested Cadence

| Frequency | Review |
|-----------|--------|
| Per release | Deployment result, errors, rollback notes and cache/migration effects |
| Monthly | Compatibility matrix, backups, failed jobs, administrator access and critical alerts |
| Quarterly | Plugin inventory, restore exercise, performance baseline and accessibility regression review |
| Before campaigns | Capacity, checkout, payment, stock sync and support escalation path |
| After an incident | Postmortem actions, runbook changes and monitoring improvements |

The exact schedule can be smaller for a brochure site and stricter for a store. What matters is that a named person performs the review and records the outcome.

## Operational Changelog

Keep an operational changelog separate from marketing release notes. It should answer what changed in the running system and how it was verified.

```text
2026-07-21 — Release 2026.07.21.1
Changed: Updated custom checkout plugin and cache rules.
Validated: Sandbox checkout, guest/cart cache test, Action Scheduler health.
Observed: No error-rate increase during 30-minute monitoring window.
Rollback: Previous artifact 2026.07.14.2 remains available.
```

This record is invaluable when performance changes, a vendor asks when an issue began or an auditor needs evidence of operational control. Keep entries factual and link to the pull request, incident or benchmark where appropriate.

## Documentation as a Deliverable

Include documentation updates in the definition of done for changes that alter configuration, a dependency, a user journey or an operational procedure. A runbook that is not updated after a successful change becomes a source of risk for the next person.
