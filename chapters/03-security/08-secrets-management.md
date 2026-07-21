# Secrets Management & Key Rotation

Secrets include database passwords, WordPress salts, payment keys, webhook signing keys, SMTP credentials and deployment tokens. They must be treated as configuration with owners and rotation procedures—not as values to paste into source code or WordPress options.

## Where Secrets Belong

| Location | Appropriate use | Avoid |
|----------|-----------------|-------|
| Environment/secret manager | Production keys and credentials | Printing values in build logs |
| Protected deployment configuration | Per-environment runtime settings | Reusing one credential across environments |
| Local untracked file | Developer sandbox values | Committing it or sharing through chat |
| Vendor dashboard | Key issuance, scope and revocation | Giving every administrator vendor access |

Commit an example file that lists names but contains no values. For example, `PAYMENT_WEBHOOK_SECRET=` documents the requirement without exposing it.

## Rotation Process

Rotation should be planned before a leak. Many services allow two keys during a transition:

```text
Create replacement key → deploy configuration that accepts new key
  → verify requests use it → revoke old key → record completion
```

For a webhook, accept both the old and new signing secret only for the short transition window, then remove the old path. For a database password, confirm every application process has reloaded configuration before disabling the prior account.

## Exposure Response

If a secret appears in Git, a ticket, a browser log or a public paste, assume it has been exposed. Revoke or rotate it immediately, review its scope and search relevant logs for misuse. Removing the visible string later does not make the credential safe again.

Further reading: [WordPress Hardening](https://developer.wordpress.org/advanced-administration/security/hardening/), [Supply-Chain Security](../09-production-workflows/04-supply-chain-security.md) and [Deployment & Configuration Management](../02-maintenance/10-deployment-configuration-management.md).
