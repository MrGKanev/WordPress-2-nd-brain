# Lab: Build a Site Plugin

This lab creates a small plugin for site-specific behavior. It demonstrates why business rules should not live in a theme and how to make a change easy to remove.

## Goal

Register a shortcode that renders a controlled callout. The example has no database writes, external requests or administrator configuration, so it is safe to run locally.

## Implementation

Create `wp-content/plugins/site-tools/site-tools.php`:

```php
<?php
/**
 * Plugin Name: Site Tools Lab
 * Description: Minimal site-specific plugin used for the book lab.
 * Version: 0.1.0
 */

defined( 'ABSPATH' ) || exit;

add_shortcode( 'site_callout', function( $attributes, $content = '' ) {
	$attributes = shortcode_atts(
		[ 'title' => 'Note' ],
		$attributes,
		'site_callout'
	);

	return sprintf(
		'<aside class="site-callout"><strong>%s</strong><div>%s</div></aside>',
		esc_html( $attributes['title'] ),
		wp_kses_post( do_shortcode( $content ) )
	);
} );
```

Activate it, then add this in a Shortcode block:

```text
[site_callout title="Before you deploy"]
Test the change on staging first.
[/site_callout]
```

## Validate and Extend

Confirm that HTML in the title is escaped and permitted markup in the content renders as expected. Next, move the callback into a namespaced class and add a unit test before introducing settings, REST endpoints or database state.

## Rollback

Delete the Shortcode block content before deactivating the plugin. Deactivation is safe because this lab does not create persistent data.

See [Advanced Plugin Engineering](../10-platform-architecture-governance/02-advanced-plugin-engineering.md).
