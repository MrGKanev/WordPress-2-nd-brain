# Operational Ownership & Service Catalog

A system with no named owner is difficult to improve and slow to recover. Operational ownership does not mean that one person performs every task; it means the team knows who makes decisions, receives alerts and maintains each critical capability.

## Service Catalog

Create a small catalog for the services that make the site work:

| Service | Owner | Dependencies | Failure impact | First response |
|---------|-------|--------------|----------------|----------------|
| Public website | Web team | CDN, host, database | Visitors cannot browse | Check availability and recent deploys |
| Checkout | E-commerce team | WooCommerce, gateway, session store | Revenue loss | Pause changes, inspect gateway/order signals |
| Transactional email | Operations | SMTP/API provider, cron | Customers miss updates | Check queue and provider status |
| Inventory sync | Operations | ERP/WMS, Action Scheduler | Overselling or stale stock | Pause conflicting updates, reconcile source |

Keep it close to the code or operational documentation. The catalog should be short enough to read during an incident and detailed enough to identify the first owner without a meeting.

## Roles During Change and Incident Response

For significant releases and incidents, assign these responsibilities explicitly:

- **Change owner** — understands the release and performs or coordinates it.
- **Approver** — confirms risk, scope and rollback readiness.
- **Responder** — receives the alert and starts the incident process.
- **Communicator** — provides status to stakeholders and support.
- **Escalation contact** — can reach the host, payment provider or vendor.

One person can fill several roles on a small project, but the roles must still be visible. Ambiguity is most expensive when a checkout failure happens outside normal working hours.

## Access Review

Review production administrators, hosting accounts, CI credentials, DNS access and third-party integration tokens on a regular cadence. Remove access that no longer has a business purpose and confirm emergency access works before it is needed. Ownership and least privilege reinforce each other: the person accountable for a service should know who can change it.
