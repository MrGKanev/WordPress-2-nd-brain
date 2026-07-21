# Benchmarking & Capacity Planning

Performance work needs a baseline. A benchmark without a defined scenario, environment and success criterion cannot show whether a change helped or merely moved work elsewhere.

## Define Representative Scenarios

Measure the requests that matter to users and infrastructure:

| Scenario | Cache state | What it reveals |
|----------|-------------|-----------------|
| Homepage or article | Warm public cache | CDN/page-cache effectiveness |
| Product or category page | Cold and warm cache | PHP, database and object-cache work |
| Cart and checkout | Dynamic session | PHP capacity, payment and database pressure |
| Admin/order screen | Authenticated | Staff experience and query volume |
| Background queue | Concurrent workload | Action Scheduler and integration throughput |

For each scenario, record response time percentiles, error rate, requests per second, CPU, memory, database latency and cache hit rate. Averages hide painful tail latency; p95 or p99 is usually more useful for visitor experience.

## Test Safely

Load testing can place real orders, exhaust API quotas and overload a shared host. Prefer staging with production-like data and integrations configured for sandbox use. If production testing is unavoidable, set a strict request limit, exclude checkout/payment actions and schedule a monitored window.

```bash
# Example: a small read-only baseline against a cacheable page.
wrk -t2 -c10 -d30s https://staging.example.com/sample-page/
```

Use a tool and command that the team can repeat. Preserve the command, date, application version, infrastructure size and results alongside the change being evaluated.

## Capacity Model

Capacity planning estimates the limiting resource before a campaign exposes it. Start with measured worker memory, database connections and dynamic-request duration:

```text
Available PHP memory ÷ average worker memory = upper worker limit
Workers ÷ average dynamic request time = approximate steady-state throughput
```

This is an estimate, not a target. CPU, database locks, payment latency and external APIs can reduce real capacity first. Apply a safety margin and test at expected peak concurrency rather than sizing to the theoretical maximum.

## Make Results Actionable

Every performance experiment should end with a decision: keep the change, revert it, gather another measurement or create capacity work. Store before/after values and note trade-offs such as increased cache memory or slower writes. Capacity is an operational budget, not a one-time benchmark score.
