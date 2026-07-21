# Production Observability

Monitoring tells you that a service is down. Observability helps explain why a specific request, checkout or background task is slow or failing.

## Signals to Collect

| Signal | Questions it answers |
|--------|----------------------|
| Logs | What error occurred and for which request? |
| Metrics | Is latency, error rate or resource use changing? |
| Traces/APM | Which PHP call, query or external request caused the delay? |
| Real-user monitoring | What do visitors experience on real devices and networks? |

Use a request or correlation ID where possible, redact personal data, and assign an owner for every alert. Alerts should be tied to user impact—failed checkout, elevated error rate or unavailable service—not merely a noisy infrastructure threshold.

See also [Monitoring & Alerting](../02-maintenance/07-monitoring-alerting.md) and [Debugging & Profiling Tools](../04-performance/10-debugging-profiling.md).

## Start with User Journeys

Instrument the journeys that make the site useful, not only the server that hosts it. For a content site, this may be page rendering, search and form delivery. For a WooCommerce store, it should include add-to-cart, checkout, payment confirmation, order email and background fulfilment.

For each journey, define a small service-level objective (SLO). For example: "99% of checkout requests complete without a server error over 30 days." The threshold is less important than having a shared definition of acceptable behavior and a response when it is breached.

## Logging Rules

Logs should help connect an error to an action without becoming a second customer database. Include timestamp, severity, request or order correlation ID, component and a concise message. Do not log passwords, access tokens, full payment data, customer addresses or raw request bodies by default.

```php
error_log( wp_json_encode( [
	'event'      => 'inventory_sync_failed',
	'product_id' => $product_id,
	'job_id'     => $action_id,
	'message'    => $exception->getMessage(),
] ) );
```

Use a site-specific logger or an error-tracking service for production code when possible. `error_log()` is suitable for a small, controlled diagnostic but does not replace retention, search and access controls.

## Alert Design

An alert should state the impact, the affected system and the first response. Good alerts are actionable: a sustained checkout error rate, a failed backup or an exhausted queue. Avoid alerts for every individual warning; group, deduplicate and escalate only when the signal needs attention.

Review alerts after an incident. If nobody acted on an alert, either improve it, route it to the right owner or remove it. Alert fatigue is an operational failure, not a reason to ignore the monitoring system.

## Dashboard Design

A useful operational dashboard answers three questions in under a minute: are visitors succeeding, where is time being spent and what changed? Keep the first view small:

| Area | Signals |
|------|---------|
| Visitor experience | Availability, p95 response time, Core Web Vitals or real-user errors |
| Application | PHP errors, failed REST/AJAX requests, slow transactions |
| Dependencies | Database latency, object-cache availability, external API failure rate |
| Store operations | Checkout completion, failed payments, queue backlog, order-email failures |

Annotate deployments, maintenance windows and campaigns on the time series. Without change context, a performance graph tells you that something changed but not which release or event to investigate first.

## Incident Workflow

During an incident, protect customers before optimizing diagnosis:

1. Confirm scope and user impact from more than one signal.
2. Stabilize: roll back a recent release, disable the failing integration or serve a safe degraded response.
3. Communicate the current impact, owner and next update time.
4. Preserve relevant logs and metrics before retention or retries remove evidence.
5. Write a brief follow-up with cause, remediation and prevention work.

Avoid making several unrelated production changes at once. Change one variable, observe the result and record it. Fast guessing makes recovery slower and obscures the actual cause.

## Privacy and Access

Observability tools are production systems. Limit who can read logs and traces, set retention periods and review integrations that forward data outside the hosting environment. Redaction rules must be tested with real error cases, because sensitive data often appears in exception messages or request parameters rather than in intentionally logged fields.
