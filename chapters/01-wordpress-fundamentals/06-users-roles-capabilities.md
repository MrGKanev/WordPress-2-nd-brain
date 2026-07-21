# Users, Roles & Capabilities

WordPress authorization is based on capabilities, not only role names. A role is a bundle of capabilities; plugins may add their own capabilities, and custom workflows can grant a specific action without granting broad administrator access.

## Default Roles

| Role | Typical responsibility |
|------|------------------------|
| Subscriber | Manage own profile and limited member features |
| Contributor | Write drafts but cannot publish by default |
| Author | Publish and manage own posts |
| Editor | Manage and publish content across authors |
| Administrator | Manage site settings, users, plugins and themes |

On a multisite network, Super Admin is a separate, highly privileged network-level role. Do not give it to a site editor or store manager merely because a task is inconvenient.

## Capability Checks in Code

Always check the action-specific capability, then validate the request and object ownership. Do not check only whether someone is logged in or whether their role name is `administrator`.

```php
if ( ! current_user_can( 'edit_post', $post_id ) ) {
	wp_die( esc_html__( 'You cannot edit this content.', 'my-plugin' ) );
}
```

The `edit_post` meta capability lets WordPress evaluate the relevant user and post. For custom features, define a capability that expresses the business action—such as `manage_inventory_imports`—rather than reusing a broad unrelated capability.

## Operational Controls

Use individual accounts, remove inactive users and review elevated access regularly. Roles are not a replacement for authentication: require strong passwords and multi-factor authentication for privileged accounts, protect application passwords and preserve an audit trail for sensitive actions.

See [Identity & Access Management](../10-platform-architecture-governance/05-identity-access-management.md), [Input Sanitization & Output Escaping](../03-security/03-data-validation.md) and [WordPress Multisite Considerations](../02-maintenance/04-multisite-basics.md).
