# Advanced Plugin Engineering

As a custom plugin grows, organize it around clear services and boundaries rather than a large collection of hooks in one file. Good structure makes features testable, upgrade-safe and easier to disable or replace.

## Suggested Structure

```text
my-plugin/
├── my-plugin.php          # Bootstrap and metadata
├── composer.json
├── src/
│   ├── Admin/
│   ├── Domain/
│   ├── Integrations/
│   └── Support/
├── templates/
├── tests/
└── uninstall.php
```

Use Composer autoloading and namespaces for custom code. The bootstrap file should register the plugin only after dependencies are available; it should not contain business logic.

## Service Boundaries

Separate WordPress integration from the domain rule it triggers. For example, a REST controller should validate the request and call an order-export service; the service should not depend directly on global request state. This makes it possible to test behavior without booting a full admin screen.

Use feature flags for risky or gradual rollouts. A feature flag should have an owner, default, expiry/review date and a way to turn it off without a code deployment. Do not let old flags accumulate permanently; they become invisible branches in production behavior.

## Lifecycle and Compatibility

Plan activation, upgrade and uninstall paths. Activation should create only the minimum required state. Long migrations belong in resumable background work. Uninstall should remove data only when the plugin's data-ownership policy permits it—never surprise an administrator by deleting business records without warning.

For public hooks, REST endpoints, database tables and stored options, define a compatibility policy. Deprecated APIs should warn, document the replacement and have a removal version or date. See [Plugin Structure](../08-plugin-development/01-plugin-structure.md), [Database Migrations](../08-plugin-development/11-database-migrations.md) and [Plugin Testing](../08-plugin-development/13-plugin-testing.md).

## Test at the Boundary

Test the plugin where failures are most costly:

| Boundary | Example test |
|----------|--------------|
| Domain logic | A pricing or permission rule returns the expected result from plain input |
| WordPress hook | A save action sanitizes input and persists only permitted fields |
| REST endpoint | An unauthorized request is rejected and a valid request has a stable response |
| External integration | Duplicate events do not repeat the business action |
| Upgrade path | An old stored option or record is still readable after deployment |

Use dependency injection sparingly but consistently at integration boundaries. Passing a database, HTTP or clock abstraction into a service makes failures reproducible in tests without turning every small value object into a framework.
