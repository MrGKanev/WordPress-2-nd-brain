# Integration Architecture

An integration is a contract between systems with different failure modes, data models and release schedules. Design for authentication, retries, rate limits and partial failure before treating an API request as a simple function call.

## Contract First

For every integration, document the endpoint/event, authentication method, required fields, ownership, timeout, retry policy and error behavior. Version payloads deliberately when the receiving system cannot evolve at the same time.

```text
Event: order.fulfilled.v1
Producer: warehouse system
Consumer: WooCommerce integration
Identity: signed webhook with timestamp
Idempotency: external event ID
Failure: queue for retry; alert after threshold
```

Use a stable external identifier instead of matching records by mutable display values such as customer name or product title.

## Reliable Delivery

External calls can timeout after the remote system completed the action. Therefore, make commands idempotent, store delivery attempts and retry with bounded backoff. Distinguish a retryable failure (temporary network error) from a permanent failure (invalid data or unauthorized request).

Verify webhook signatures before parsing or acting on the payload, enforce a timestamp/replay window and acknowledge quickly after durable receipt. Process expensive work asynchronously. Do not put a long ERP or email call in the visitor's checkout request.

## Rate Limits and Observability

Respect vendor rate limits with queues, batching and backoff. Monitor latency, error rate, queue age and the number of records awaiting reconciliation. An integration dashboard should answer which records failed, why and whether retrying is safe.

See [WooCommerce REST API](../06-e-commerce/07-woocommerce-rest-api.md), [Background Processing](../08-plugin-development/10-background-processing.md) and [WooCommerce Operations & Integrations](../09-production-workflows/08-woocommerce-operations.md).

## Replay and Reconciliation

Build a safe way to replay an integration event without resending a charge, shipment or email. Store the event ID, source timestamp, processing result and the external record ID created by the handler. A replay tool should show what will happen before it performs it and restrict destructive actions to authorized operators.

Schedule reconciliation for data that matters financially or operationally. Compare a bounded time range between systems, identify missing or divergent records and resolve them through the documented source-of-truth rules. Reconciliation turns an eventual-consistency design into a controllable business process.

## Contract Change Checklist

- [ ] New fields are optional until every consumer can read them.
- [ ] Removed fields have a communicated deprecation period.
- [ ] Payload version, examples and validation rules are documented.
- [ ] Staging has tested retries, duplicates, invalid signatures and provider outage behavior.
- [ ] Monitoring identifies failures by event type and external record ID.
