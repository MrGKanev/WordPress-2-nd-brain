# Privacy & Data Governance

Privacy work begins with knowing what data exists, why it is processed, where it goes and how long it remains accessible. A privacy policy alone does not answer these operational questions.

## Data Map

Create a map for each important data flow:

| Data | Purpose | System | Access | Retention |
|------|---------|--------|--------|-----------|
| Contact form details | Respond to enquiry | WordPress + email provider | Support team | Defined support period |
| Order information | Fulfilment/accounting | WooCommerce + ERP | Operations/finance | Legal and business requirement |
| Analytics identifiers | Measure site use | Analytics provider | Marketing | Configured analytics period |

Include backups, logs, error trackers, email platforms and plugin vendors. These are often the places where personal data remains after it is deleted from the WordPress admin.

## Consent and User Rights

Consent must be specific to the processing that requires it and should be recorded in a way that can be audited. Do not load non-essential tracking before the applicable consent choice. Give users a practical way to change that choice.

Build procedures for access, export, correction and deletion requests. Verify the requester appropriately, define who approves exceptions and document which connected systems must receive the request. A deletion request may need to preserve records required for legal or accounting reasons; explain the retained data and reason rather than silently failing the request.

## Data-Minimizing Design

Collect only fields required for the task, use a restricted role for exports and avoid placing sensitive data in free-form notes, debug logs or analytics events. Review data flows whenever a new plugin, payment method or marketing integration is introduced.

See [GDPR Implementation](../03-security/04-gdpr-implementation.md) and [Migrations & Data Lifecycle](../09-production-workflows/09-migrations-data-lifecycle.md).

## Privacy Review for a New Feature

Review a feature before it collects or transmits data:

- What personal data is essential to the stated purpose?
- Is the data entered by a visitor, inferred, imported or received from another system?
- Which processors, plugins and team roles can access it?
- What lawful basis, consent state or contractual requirement applies?
- How will the data be exported, corrected or removed?
- What happens to it in logs, backups and failed-job queues?

Record the answer with the feature decision. This is faster than discovering after launch that a marketing widget or diagnostic integration has created a new untracked data flow.

## Breach Readiness

Maintain an incident contact list, evidence-preservation process and decision owner for suspected data exposure. Practice the first hour: contain the issue, identify affected systems, preserve logs and avoid speculative public statements. Legal notification duties depend on the situation and jurisdiction, so escalation must happen early.
