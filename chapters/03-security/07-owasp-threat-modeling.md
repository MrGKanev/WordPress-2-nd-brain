# OWASP Threat Modeling for WordPress

The OWASP Top 10 is an awareness framework, not a WordPress configuration checklist. Use it to ask how a feature could be misused, which data would be affected and what control reduces the risk before code is deployed.

## Map Common Risks to WordPress Work

| Risk area | WordPress example | First control |
|-----------|-------------------|---------------|
| Broken access control | A REST endpoint exposes another customer's order | Capability/ownership check on every request |
| Injection | Custom SQL concatenates request data | `$wpdb->prepare()` and input validation |
| Security misconfiguration | Debug output or a staging admin is public | Safe environment defaults and access review |
| Vulnerable components | Abandoned plugin remains active | Inventory, updates and replacement plan |
| Authentication failures | Shared administrator account or weak login protection | Individual accounts, MFA and rate limiting |
| SSRF | Import feature fetches arbitrary user-supplied URLs | Allowlist destinations and validate URLs |

The categories overlap. A product import can involve authorization, SSRF, data validation, logging and third-party dependencies at the same time.

## A Small Threat-Model Workshop

For a new feature, answer these questions before implementation:

1. What data enters, leaves or changes state?
2. Which users, services and roles may perform each action?
3. What happens if a request is repeated, forged, delayed or made by the wrong user?
4. Which logs prove what happened without exposing sensitive data?
5. How is the feature disabled or recovered if it is abused?

Write the outcome in an issue or decision record. A five-minute model for a webhook, file upload or payment action often finds a missing permission check earlier than a security scan does.

## Validation

Test both success and refusal paths: a user without the capability, an object owned by another user, malformed input, duplicate delivery and unavailable dependency. Treat a passing happy path as incomplete security testing.

Further reading: [OWASP Top 10](https://owasp.org/Top10/2021/), [Input Sanitization & Output Escaping](./03-data-validation.md), [Identity & Access Management](../10-platform-architecture-governance/05-identity-access-management.md).
