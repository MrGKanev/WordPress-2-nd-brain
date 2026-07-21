# Release & Upgrade Playbooks

A playbook is a repeatable plan for a change that affects users. It defines who acts, what is checked, when to stop and how to return to a known-good state.

## Standard Release Playbook

### Before

- Confirm the release scope, owner and deployment window.
- Ensure CI checks, code review and staging validation have passed.
- Record the current release version and verify backups/rollback access.
- Identify cache, database migration, queue and external-service effects.
- Prepare a short customer/support message if the change may be visible.

### During

1. Deploy one immutable, approved artifact.
2. Run required migrations or queue work using the documented command.
3. Purge or revalidate only the cache entries the release requires.
4. Run automated health checks and the highest-value manual journey.
5. Watch errors, latency and business signals during the rollback window.

### After

Record the deployed version, timestamps, validation result and any exception. Close the release only when monitoring remains stable. If something was done manually, add it to the playbook or create an improvement task.

## Major Upgrade Playbook

Major WordPress, PHP, WooCommerce or database upgrades need a compatibility assessment before the release:

| Stage | Required outcome |
|-------|------------------|
| Inventory | Exact current versions and critical dependencies are known |
| Staging | Core journeys and integrations pass against the target versions |
| Migration | Schema/data changes are additive, tested and recoverable |
| Rollout | Owner, monitoring window and rollback conditions are agreed |
| Follow-up | Deprecated code and temporary compatibility paths have an owner |

Upgrade one major boundary at a time when possible. The goal is not speed alone; it is knowing which change caused a regression and being able to restore service safely.

## Blameless Postmortems

After a meaningful incident, write a concise record while the facts are available:

1. What users experienced and for how long.
2. Timeline of detection, decisions, actions and recovery.
3. Technical and process factors that allowed the incident.
4. What worked well during response.
5. Specific preventive actions with owners and target dates.

Focus on improving the system rather than assigning personal fault. A postmortem has value only when its actions are tracked and later verified.
