# Identity & Access Management

Access management protects content, customer data and the ability to change production systems. Start with WordPress roles, then include hosting, DNS, source control, CI and vendor dashboards in the same access model.

## Least Privilege

Give each person the smallest set of permissions needed for their work. Prefer individual accounts to shared logins so actions can be traced and access can be revoked cleanly.

| Role | Typical capability | Should not receive by default |
|------|--------------------|-------------------------------|
| Author | Create/edit own drafts | Plugin, user or site settings access |
| Editor | Publish and manage content | Hosting or payment-provider access |
| Store manager | Orders, products and refunds | WordPress code/plugin installation |
| Developer | Staging code and diagnostics | Broad production customer-data export |
| Administrator | Site configuration | Unnecessary vendor/hosting super-admin access |

WordPress's default roles are a starting point. Review custom capabilities introduced by plugins, especially those that expose exports, payment settings or integration credentials.

## Authentication and Offboarding

Require strong, unique passwords and multi-factor authentication for administrator, hosting, source-control and payment-provider accounts. Use SSO where the organization can manage it reliably, but retain a documented, protected emergency-access path.

On role change or departure, remove access promptly from WordPress, hosting, DNS, repositories, CI, password managers and vendor dashboards. Rotate shared or exposed credentials rather than assuming that removing the user account is sufficient.

## Access Review Evidence

Maintain a periodic review record: who checked the list, which systems were included, what changed and any exceptions. This small discipline finds forgotten agency accounts and old API tokens before they become an incident.

See [Supply-Chain Security](../09-production-workflows/04-supply-chain-security.md) and [Server-Level Security Hardening](../03-security/02-server-hardening.md).

## Access Request Workflow

Make access changes traceable and reversible:

```text
Request states the role, system, reason and expiry date
  → system owner approves the minimum permission
  → access is granted to an individual account
  → requester confirms it works
  → scheduled review removes or renews it
```

Time-limit elevated support and developer access where possible. Break-glass administrator access should be protected, logged and reviewed after use. It is a recovery control, not a daily account.

## Account Compromise Response

If an account may be compromised, revoke its sessions and tokens, reset or rotate relevant credentials, review recent privileged actions and preserve logs. Do not delete evidence before determining scope. Update the access process if the incident exposed a weak approval, MFA or offboarding control.
