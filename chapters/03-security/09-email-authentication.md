# Transactional Email Authentication

WordPress email is part of the security boundary: password resets, order confirmations and account notices must be delivered from an authenticated domain. Use a transactional email provider or correctly configured SMTP service instead of relying on an unverified server mail setup.

## Authentication Layers

| Control | Purpose |
|---------|---------|
| SPF | Lists services allowed to send mail for a domain |
| DKIM | Adds a cryptographic signature to mail from a domain |
| DMARC | Tells recipients how to handle failed/aligned authentication and provides reports |
| TLS | Protects transport between mail servers where supported/required |

For Gmail recipients, current sender rules require authentication and TLS; bulk senders have additional SPF, DKIM, DMARC and alignment requirements. Verify the requirements of every major recipient ecosystem and your sending provider rather than assuming one DNS record solves deliverability everywhere.

## Safe Rollout

1. Inventory every service that sends as the domain: WordPress, help desk, CRM, newsletter and transactional provider.
2. Publish and validate SPF/DKIM for the actual sending services.
3. Start DMARC monitoring with a reporting policy appropriate for the organization.
4. Review reports for legitimate senders before moving to stronger enforcement.
5. Send test password-reset and order emails, then inspect message authentication results.

Do not publish multiple independent SPF records for one domain; combine authorized senders into the provider-approved record. Keep marketing and transactional sending identities distinct where the provider and operational model allow it.

## WordPress Checks

Confirm the visible `From` domain aligns with the authenticated sender, mail failures are logged without storing sensitive content, and staging cannot send to real customer lists. Test unsubscribe and consent handling for marketing messages separately from operational receipts or password resets.

Further reading: [Gmail sender guidelines](https://support.google.com/mail/answer/81126?hl=en), [Email Deliverability](../02-maintenance/06-email-deliverability.md) and [Privacy & Data Governance](../10-platform-architecture-governance/06-privacy-data-governance.md).
