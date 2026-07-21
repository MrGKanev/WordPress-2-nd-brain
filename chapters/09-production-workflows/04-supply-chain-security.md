# Supply-Chain Security

Every plugin, theme, Composer package and deployment credential becomes part of the site's attack surface. Security includes deciding what enters the project and how updates are verified.

## Working Rules

- Install extensions from maintained, reputable sources and record why each one exists.
- Keep WordPress core, plugins, themes and Composer dependencies updated through staging first.
- Remove unused code instead of merely deactivating it.
- Restrict write access, protect deployment credentials and rotate secrets after an incident.
- Review administrator accounts and integration tokens regularly.

An update policy should define who approves security updates, how they are tested, and how a failed release is rolled back. Avoid unmanaged "must-have" plugins: fewer, well-understood dependencies are easier to secure.

See [Plugin Recommendations](../02-maintenance/01-plugin-recommendations.md) and [Incident Response](../03-security/05-incident-response.md).

## Dependency Inventory

Maintain an inventory of active plugins, theme packages, Composer dependencies and external services. For each dependency, record its purpose, owner, source, update method and whether the site can operate without it. This turns an emergency update from a scavenger hunt into a controlled change.

Before adding a plugin, ask:

- Does WordPress core, WooCommerce or an existing extension already provide this capability?
- Is the code actively maintained and compatible with the supported PHP and WordPress versions?
- What data does it receive, store or transmit?
- Does it add an administrator account, cron job, webhook or frontend asset?
- How will it be removed if the vendor disappears?

## Updates Without Surprises

Subscribe to security notices for core and critical vendors, but do not automatically deploy every update directly to production. Test updates in staging with the site’s key workflows, review release notes for breaking changes, then deploy a known version through the normal release path.

Emergency security fixes are different: use a shorter approval path, take a verified backup, document the exact versions before and after, and perform focused smoke tests immediately after deployment. Follow up later with the same review and documentation expected of a normal change.

## Credentials and Access

Use separate credentials for local, staging and production systems. Give people the smallest access level that supports their work, prefer individual accounts over shared administrator logins, and revoke access when a contractor or integration no longer needs it.

Secrets belong in a secret manager, deployment environment or protected configuration—not in Git, browser-side JavaScript or WordPress options visible to administrators. If a secret is exposed, rotate it; deleting the visible copy does not invalidate the credential.

## Plugin Governance

Treat each extension as a maintained asset. A lightweight register can contain:

| Field | Example |
|-------|---------|
| Purpose | VAT validation at checkout |
| Owner | E-commerce team |
| Source | Official marketplace or vendor repository |
| Data access | Billing address and VAT number |
| Criticality | Checkout-blocking |
| Update/exit plan | Test quarterly; export settings before replacement |

Review this register at least during major releases and after an incident. It identifies abandoned dependencies before they become the only component preventing a PHP or WordPress update.

## Secure Build and Deploy Access

The CI system deserves the same protection as production: it can publish code and often holds credentials. Use protected branches, review requirements, scoped deployment tokens and separate credentials per environment. Log deployments and revoke a token that is no longer needed.

Do not give a build job a broad production shell account merely because it is convenient. Prefer a constrained deployment mechanism that can upload the intended release and run only the required health or migration commands.

## Response to a Dependency Vulnerability

1. Identify whether the vulnerable component and affected version are active.
2. Assess exposure: public endpoint, authenticated admin path, stored data or build-only dependency.
3. Apply the vendor fix or mitigations on staging, then production through the emergency process.
4. Review logs and accounts for evidence of exploitation.
5. Document the version, timeline and follow-up controls.

If no fix exists, reduce exposure first—disable the affected feature, restrict access or replace the dependency. Waiting for a perfect upgrade plan can leave a known public vulnerability in place.
