# Incident Knowledge Base

Postmortems describe a single event. An incident knowledge base turns repeated lessons into faster future response. It should be searchable, concise and grounded in verified evidence rather than folklore.

## What to Capture

For each resolved incident or significant near miss, record:

- a plain-language title and affected service;
- user impact, start/end time and detection method;
- symptoms that distinguish it from similar failures;
- confirmed cause and contributing conditions;
- safe mitigation, rollback or recovery steps;
- links to logs, dashboards, vendor tickets and the full postmortem;
- prevention actions and their completion status.

Avoid storing secrets, customer data or full sensitive logs in the knowledge base. Reference a protected evidence location when needed.

## Example Entry Structure

```text
Title: Checkout requests time out during payment-provider latency
Symptoms: Orders remain pending; PHP-FPM workers saturated; gateway API latency rises.
First response: Pause deployments, check provider status, reduce unsafe retries.
Do not: Retry payments blindly or edit order data directly in the database.
Recovery: Reconcile provider events, process idempotent queue work, notify support.
Prevention: Timeout budget, queue monitoring and load-test scenario.
```

The most valuable field is often "Do not." It preserves hard-earned knowledge about actions that create duplicate charges, data loss or a longer outage.

## From Incident to Standard Practice

When the same mitigation appears twice, turn it into a runbook, automated check or architectural control. When a monitoring signal detects an issue late, update the alert. The knowledge base is successful when future responders need less improvisation, not when it contains the longest narrative.
