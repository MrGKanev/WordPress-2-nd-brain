# Decision Records & Proven Patterns

Architecture decisions outlive the people who made them. A short decision record explains why a project uses a particular cache strategy, payment integration or hosting model, and what conditions would justify revisiting it.

## Architecture Decision Record (ADR)

Use one ADR for a decision that is expensive to reverse or affects multiple teams:

```text
Title: Use a system cron and CLI queue worker for WooCommerce actions
Status: Accepted
Context: HTTP-triggered cron causes unpredictable checkout load and delayed jobs.
Decision: Disable WP-Cron and run due cron/actions through the server scheduler.
Consequences: Requires monitored server cron and documented failure alerting.
Review trigger: Hosting migration or a move to multiple application nodes.
```

An ADR is not a long design document. It captures the decision, alternatives considered, consequences and a review trigger. Link it from related configuration and runbooks.

## Proven Pattern Criteria

Mark a pattern as proven only after it has evidence: repeatable tests, a stable production outcome or a successful recovery. Record the context in which it works and its trade-offs.

| Pattern | Evidence needed | Common trade-off |
|---------|-----------------|------------------|
| Targeted cache purge | Correctness and origin-load test | More integration work than global purge |
| Asynchronous webhook processing | Duplicate-event and outage tests | Queue monitoring and reconciliation required |
| Release directories | Tested rollback | Shared uploads/configuration must be managed |
| HPOS migration | Extension compatibility and order validation | Legacy integrations may need replacement |

Avoid universal rules such as "always use Redis" or "never use a page builder." A useful pattern includes the conditions under which it is appropriate.

## Retiring Decisions

Decisions expire when their assumptions change: traffic grows, a vendor changes an API, WordPress introduces a native capability or the team acquires different operational capacity. Review ADRs during major upgrades and retire them explicitly when a new decision supersedes them. Keeping old reasoning visible prevents the team from rediscovering the same trade-off repeatedly.
