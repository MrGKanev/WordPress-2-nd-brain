# WordPress Platform Governance

Platform governance defines how a team keeps many WordPress changes coherent: who owns the theme and plugins, what quality bar applies, how exceptions are approved and when old code is retired.

## Standards That Matter

Keep standards short, enforceable and tied to real risks:

- custom functionality belongs in plugins, not a theme, unless it is purely presentational;
- production changes use version control and a documented release path;
- new dependencies have an owner, purpose and update/exit plan;
- custom code follows agreed quality checks and translation/accessibility rules;
- direct database edits are an exceptional, documented recovery action.

Publish starter templates for plugins, blocks and integrations so a developer can begin with the approved structure rather than copying an old production file.

## Ownership and Deprecation

Every custom theme, plugin and integration should have a technical owner and a business owner. The technical owner maintains compatibility; the business owner decides whether the capability remains worth its cost.

For retiring code, announce the replacement, add a compatibility period where practical, measure remaining use and remove it in a scheduled release. Unmaintained code should not stay active indefinitely simply because nobody is certain whether it is used.

## Multisite Governance

For a network, decide what is network-managed, what individual sites may configure and how plugins/themes are approved. Shared code can create shared incidents, so test network-wide changes against representative sites and document exceptions. See [WordPress Multisite Considerations](../02-maintenance/04-multisite-basics.md) and [Multisite Performance](../04-performance/18-multisite-performance.md).

## Change Intake and Exceptions

Create a lightweight intake for a new plugin, integration or custom feature. It should identify the business need, owner, data access, supported versions, operational impact and removal plan. This prevents urgent requests from becoming permanent, unowned code.

When a standard cannot be followed, record the exception, risk, compensating control, owner and expiry date. Exceptions without expiry tend to become undocumented policy. Review them during the same cadence as dependency and security reviews.

## Platform Health Indicators

Track the small number of indicators that reveal whether the platform is becoming harder to maintain: unsupported dependencies, plugins without an owner, overdue access reviews, failed backups, pending migrations and repeated incident causes. Governance succeeds when these signals improve while delivery remains practical for the team.
