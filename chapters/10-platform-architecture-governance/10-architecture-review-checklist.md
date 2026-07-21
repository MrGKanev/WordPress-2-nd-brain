# Architecture Review Checklist

Use this checklist before a new major feature, host move, commerce integration, headless frontend or large redesign. The purpose is to expose assumptions early, not to delay ordinary content work.

## Problem and Scope

- [ ] The user/business problem and success measure are explicit.
- [ ] The data model, primary owner and user roles are known.
- [ ] Public, authenticated and administrator journeys are identified.
- [ ] Alternatives—including extending existing functionality—were considered.
- [ ] The change has a named technical and business owner.

## Security, Privacy and Reliability

- [ ] Authentication, authorization and secret storage are designed.
- [ ] Personal-data fields, processors and retention are mapped.
- [ ] External calls have timeout, retry, idempotency and reconciliation behavior.
- [ ] Failure modes and a safe degraded state are documented.
- [ ] Backup, rollback and incident-response effects are understood.

## Performance and Operations

- [ ] Cacheability and variation factors are defined.
- [ ] Expected traffic, queue volume and database effects are estimated.
- [ ] Logs, metrics and alerts identify user impact and component failure.
- [ ] Deployment, migration and rollback steps are repeatable.
- [ ] Monitoring and support owners have access to the needed evidence.

## Editorial and Accessibility Quality

- [ ] Editors have appropriate blocks, fields, patterns and permissions.
- [ ] Content migration and redirect needs are planned.
- [ ] Keyboard, screen-reader, zoom and error-state behavior are testable.
- [ ] Localization, SEO metadata and language/currency variation are considered where relevant.

## Review Outcome

Record one of three outcomes: approved, approved with tracked conditions, or needs redesign. Link the decision to an ADR, issue or pull request. The review is useful only if its unanswered questions become owned work rather than disappearing after the meeting.

See [Decision Records & Proven Patterns](../09-production-workflows/20-decision-records-proven-patterns.md), [Integration Architecture](./07-integration-architecture.md) and [Platform Adoption Roadmap](./09-platform-adoption-roadmap.md).
