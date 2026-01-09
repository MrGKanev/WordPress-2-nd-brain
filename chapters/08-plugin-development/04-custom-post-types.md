# Custom Post Types & Taxonomies

## Overview

Custom Post Types (CPTs) and taxonomies extend WordPress beyond posts and pages. They're fundamental to any plugin that stores structured content—products, events, portfolios, testimonials, or any domain-specific data.

Understanding CPTs well prevents common problems: broken permalinks, missing admin menus, permission issues, and performance problems from improper data modeling.

## When to Use Custom Post Types

Use CPTs when content:
- Has a distinct identity (events are not blog posts)
- Needs its own admin listing and editing interface
- Should be queryable separately from other content
- Benefits from WordPress's built-in features (revisions, featured images, etc.)

**Don't use CPTs for:**
- Data that belongs to another post (use post meta instead)
- Simple key-value settings (use options)
- User-specific data (use user meta)
- High-volume transactional data (consider custom tables)

## Registering a Custom Post Type

### Basic Registration

```php
add_action( 'init', 'register_event_post_type' );

function register_event_post_type() {
    $labels = array(
        'name'               => 'Events',
        'singular_name'      => 'Event',
        'menu_name'          => 'Events',
        'add_new'            => 'Add New',
        'add_new_item'       => 'Add New Event',
        'edit_item'          => 'Edit Event',
        'new_item'           => 'New Event',
        'view_item'          => 'View Event',
        'search_items'       => 'Search Events',
        'not_found'          => 'No events found',
        'not_found_in_trash' => 'No events found in trash',
    );

    $args = array(
        'labels'              => $labels,
        'public'              => true,
        'has_archive'         => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'show_in_rest'        => true,  // Enables block editor & REST API
        'menu_icon'           => 'dashicons-calendar',
        'supports'            => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
        'rewrite'             => array( 'slug' => 'events' ),
    );

    register_post_type( 'event', $args );
}
```

### Important Arguments Explained

| Argument | Purpose | Common Values |
|----------|---------|---------------|
| `public` | Master switch for visibility | `true` for content, `false` for internal data |
| `has_archive` | Creates archive page at `/events/` | `true` or custom slug string |
| `show_in_rest` | Enables block editor and REST API | `true` for modern WordPress |
| `supports` | Features available when editing | `title`, `editor`, `thumbnail`, `excerpt`, `custom-fields`, `revisions` |
| `rewrite` | URL structure | `array( 'slug' => 'events' )` or `false` |
| `menu_position` | Admin menu placement | `5` = below Posts, `20` = below Pages |
| `capability_type` | Permission model | `post` (default) or custom |

### Visibility Options

Different combinations for different use cases:

```php
// Public content (blog posts, products, events)
'public'              => true,
'publicly_queryable'  => true,
'show_ui'             => true,
'show_in_menu'        => true,
'has_archive'         => true,

// Admin-only (internal records, logs)
'public'              => false,
'publicly_queryable'  => false,
'show_ui'             => true,
'show_in_menu'        => true,

// Completely hidden (programmatic use only)
'public'              => false,
'show_ui'             => false,
'show_in_menu'        => false,
```

### Custom Capabilities

By default, CPTs use post capabilities. For separate permissions:

```php
$args = array(
    'capability_type' => 'event',
    'map_meta_cap'    => true,  // Maps meta capabilities automatically
    'capabilities'    => array(
        'edit_post'          => 'edit_event',
        'read_post'          => 'read_event',
        'delete_post'        => 'delete_event',
        'edit_posts'         => 'edit_events',
        'edit_others_posts'  => 'edit_others_events',
        'publish_posts'      => 'publish_events',
        'read_private_posts' => 'read_private_events',
    ),
);
```

Then grant capabilities to roles:

```php
// Run once on plugin activation
function add_event_caps() {
    $admin = get_role( 'administrator' );
    $admin->add_cap( 'edit_events' );
    $admin->add_cap( 'edit_others_events' );
    $admin->add_cap( 'publish_events' );
    $admin->add_cap( 'read_private_events' );
    $admin->add_cap( 'delete_events' );
}
register_activation_hook( __FILE__, 'add_event_caps' );
```

## Custom Taxonomies

Taxonomies organize and classify posts. WordPress has two built-in: categories (hierarchical) and tags (flat).

### Hierarchical Taxonomy (like Categories)

```php
add_action( 'init', 'register_event_type_taxonomy' );

function register_event_type_taxonomy() {
    $labels = array(
        'name'              => 'Event Types',
        'singular_name'     => 'Event Type',
        'search_items'      => 'Search Event Types',
        'all_items'         => 'All Event Types',
        'parent_item'       => 'Parent Event Type',
        'parent_item_colon' => 'Parent Event Type:',
        'edit_item'         => 'Edit Event Type',
        'update_item'       => 'Update Event Type',
        'add_new_item'      => 'Add New Event Type',
        'new_item_name'     => 'New Event Type Name',
        'menu_name'         => 'Event Types',
    );

    $args = array(
        'labels'            => $labels,
        'hierarchical'      => true,  // Like categories
        'public'            => true,
        'show_ui'           => true,
        'show_admin_column' => true,  // Show in post list table
        'show_in_rest'      => true,  // Enable in block editor
        'rewrite'           => array( 'slug' => 'event-type' ),
    );

    register_taxonomy( 'event_type', array( 'event' ), $args );
}
```

### Flat Taxonomy (like Tags)

```php
add_action( 'init', 'register_event_tag_taxonomy' );

function register_event_tag_taxonomy() {
    $labels = array(
        'name'                       => 'Event Tags',
        'singular_name'              => 'Event Tag',
        'search_items'               => 'Search Event Tags',
        'popular_items'              => 'Popular Event Tags',
        'all_items'                  => 'All Event Tags',
        'edit_item'                  => 'Edit Event Tag',
        'update_item'                => 'Update Event Tag',
        'add_new_item'               => 'Add New Event Tag',
        'new_item_name'              => 'New Event Tag Name',
        'separate_items_with_commas' => 'Separate tags with commas',
        'add_or_remove_items'        => 'Add or remove event tags',
        'choose_from_most_used'      => 'Choose from the most used event tags',
    );

    $args = array(
        'labels'            => $labels,
        'hierarchical'      => false,  // Like tags
        'public'            => true,
        'show_ui'           => true,
        'show_admin_column' => true,
        'show_in_rest'      => true,
        'rewrite'           => array( 'slug' => 'event-tag' ),
    );

    register_taxonomy( 'event_tag', array( 'event' ), $args );
}
```

### Taxonomy for Multiple Post Types

```php
// One taxonomy shared across multiple post types
register_taxonomy( 'location', array( 'event', 'venue', 'post' ), $args );
```

## Rewrite Rules and Permalinks

### The Flush Problem

WordPress caches rewrite rules. After registering a new CPT or taxonomy, you must flush:

```php
// On plugin activation - flush rewrite rules
register_activation_hook( __FILE__, 'my_plugin_activate' );
function my_plugin_activate() {
    register_event_post_type();  // Register first
    flush_rewrite_rules();       // Then flush
}

// On plugin deactivation - clean up
register_deactivation_hook( __FILE__, 'my_plugin_deactivate' );
function my_plugin_deactivate() {
    flush_rewrite_rules();
}
```

**Never flush on every page load** - it's expensive and will slow your site.

### Custom URL Structures

```php
// Simple slug
'rewrite' => array( 'slug' => 'events' ),
// URL: /events/my-event/

// With category-like structure
'rewrite' => array(
    'slug'       => 'events',
    'with_front' => false,  // Don't prepend /blog/ if that's the posts prefix
),

// Disable rewrite (for internal CPTs)
'rewrite' => false,
```

### Changing Slugs After Launch

If you change slugs after content exists:
1. Set up 301 redirects from old URLs
2. Update internal links
3. Flush rewrite rules
4. Test thoroughly

## Meta Boxes for Custom Fields

### Adding a Meta Box

```php
add_action( 'add_meta_boxes', 'add_event_meta_boxes' );

function add_event_meta_boxes() {
    add_meta_box(
        'event_details',           // ID
        'Event Details',           // Title
        'render_event_details',    // Callback
        'event',                   // Post type
        'normal',                  // Context (normal, side, advanced)
        'high'                     // Priority
    );
}

function render_event_details( $post ) {
    // Security nonce
    wp_nonce_field( 'event_details_nonce', 'event_details_nonce' );

    // Get saved values
    $date     = get_post_meta( $post->ID, '_event_date', true );
    $location = get_post_meta( $post->ID, '_event_location', true );
    $price    = get_post_meta( $post->ID, '_event_price', true );

    ?>
    <p>
        <label for="event_date">Event Date:</label>
        <input type="date"
               id="event_date"
               name="event_date"
               value="<?php echo esc_attr( $date ); ?>">
    </p>
    <p>
        <label for="event_location">Location:</label>
        <input type="text"
               id="event_location"
               name="event_location"
               value="<?php echo esc_attr( $location ); ?>"
               class="regular-text">
    </p>
    <p>
        <label for="event_price">Ticket Price:</label>
        <input type="number"
               id="event_price"
               name="event_price"
               value="<?php echo esc_attr( $price ); ?>"
               step="0.01"
               min="0">
    </p>
    <?php
}
```

### Saving Meta Box Data

```php
add_action( 'save_post_event', 'save_event_details' );

function save_event_details( $post_id ) {
    // Verify nonce
    if ( ! isset( $_POST['event_details_nonce'] ) ||
         ! wp_verify_nonce( $_POST['event_details_nonce'], 'event_details_nonce' ) ) {
        return;
    }

    // Check autosave
    if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
        return;
    }

    // Check permissions
    if ( ! current_user_can( 'edit_post', $post_id ) ) {
        return;
    }

    // Sanitize and save
    if ( isset( $_POST['event_date'] ) ) {
        update_post_meta( $post_id, '_event_date', sanitize_text_field( $_POST['event_date'] ) );
    }

    if ( isset( $_POST['event_location'] ) ) {
        update_post_meta( $post_id, '_event_location', sanitize_text_field( $_POST['event_location'] ) );
    }

    if ( isset( $_POST['event_price'] ) ) {
        update_post_meta( $post_id, '_event_price', floatval( $_POST['event_price'] ) );
    }
}
```

## Querying Custom Post Types

### Using WP_Query

```php
// Get upcoming events
$events = new WP_Query( array(
    'post_type'      => 'event',
    'posts_per_page' => 10,
    'meta_key'       => '_event_date',
    'orderby'        => 'meta_value',
    'order'          => 'ASC',
    'meta_query'     => array(
        array(
            'key'     => '_event_date',
            'value'   => date( 'Y-m-d' ),
            'compare' => '>=',
            'type'    => 'DATE',
        ),
    ),
) );

while ( $events->have_posts() ) {
    $events->the_post();
    // Display event
}
wp_reset_postdata();
```

### Query with Taxonomy

```php
// Events of a specific type
$events = new WP_Query( array(
    'post_type' => 'event',
    'tax_query' => array(
        array(
            'taxonomy' => 'event_type',
            'field'    => 'slug',
            'terms'    => 'conference',
        ),
    ),
) );
```

### Getting Terms

```php
// Get all event types
$types = get_terms( array(
    'taxonomy'   => 'event_type',
    'hide_empty' => false,  // Include empty terms
) );

foreach ( $types as $type ) {
    echo $type->name . ' (' . $type->count . ')';
}

// Get terms for a specific event
$event_types = get_the_terms( $post_id, 'event_type' );
```

## CPT vs Custom Tables

Sometimes a custom database table is better than a CPT:

| Use CPT When | Use Custom Table When |
|--------------|----------------------|
| Content needs revisions | High-volume transactional data |
| Content needs featured images | Complex relational data |
| WordPress admin editing is needed | Millions of records expected |
| SEO/URLs matter | Performance-critical queries |
| Standard WordPress query patterns | Non-content data (logs, analytics) |

### Example: When Custom Table Is Better

An event booking system might use:
- **CPT for Events** - public content, needs URLs, admin editing
- **Custom table for Bookings** - transactional, high-volume, relational (links users to events)

```php
// Events: CPT (content)
register_post_type( 'event', ... );

// Bookings: Custom table (transactions)
// Structure: id, event_id, user_id, quantity, status, created_at
global $wpdb;
$wpdb->query( "
    CREATE TABLE IF NOT EXISTS {$wpdb->prefix}event_bookings (
        id bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        event_id bigint(20) UNSIGNED NOT NULL,
        user_id bigint(20) UNSIGNED NOT NULL,
        quantity int(11) NOT NULL DEFAULT 1,
        status varchar(20) NOT NULL DEFAULT 'pending',
        created_at datetime NOT NULL,
        PRIMARY KEY (id),
        KEY event_id (event_id),
        KEY user_id (user_id)
    )
" );
```

## Complete Example: Events Plugin

```php
<?php
/**
 * Plugin Name: Events Manager
 * Description: Custom post type for events
 */

// Prevent direct access
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class Events_Manager {

    public function __construct() {
        add_action( 'init', array( $this, 'register_post_type' ) );
        add_action( 'init', array( $this, 'register_taxonomy' ) );
        add_action( 'add_meta_boxes', array( $this, 'add_meta_boxes' ) );
        add_action( 'save_post_event', array( $this, 'save_meta' ) );
    }

    public function register_post_type() {
        $labels = array(
            'name'               => __( 'Events', 'events-manager' ),
            'singular_name'      => __( 'Event', 'events-manager' ),
            'add_new_item'       => __( 'Add New Event', 'events-manager' ),
            'edit_item'          => __( 'Edit Event', 'events-manager' ),
            'view_item'          => __( 'View Event', 'events-manager' ),
            'search_items'       => __( 'Search Events', 'events-manager' ),
            'not_found'          => __( 'No events found', 'events-manager' ),
        );

        $args = array(
            'labels'              => $labels,
            'public'              => true,
            'has_archive'         => true,
            'show_in_rest'        => true,
            'menu_icon'           => 'dashicons-calendar-alt',
            'supports'            => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
            'rewrite'             => array( 'slug' => 'events' ),
        );

        register_post_type( 'event', $args );
    }

    public function register_taxonomy() {
        $labels = array(
            'name'          => __( 'Event Types', 'events-manager' ),
            'singular_name' => __( 'Event Type', 'events-manager' ),
            'add_new_item'  => __( 'Add New Event Type', 'events-manager' ),
        );

        $args = array(
            'labels'            => $labels,
            'hierarchical'      => true,
            'public'            => true,
            'show_admin_column' => true,
            'show_in_rest'      => true,
            'rewrite'           => array( 'slug' => 'event-type' ),
        );

        register_taxonomy( 'event_type', array( 'event' ), $args );
    }

    public function add_meta_boxes() {
        add_meta_box(
            'event_details',
            __( 'Event Details', 'events-manager' ),
            array( $this, 'render_meta_box' ),
            'event',
            'normal',
            'high'
        );
    }

    public function render_meta_box( $post ) {
        wp_nonce_field( 'event_meta_nonce', 'event_meta_nonce' );

        $date     = get_post_meta( $post->ID, '_event_date', true );
        $time     = get_post_meta( $post->ID, '_event_time', true );
        $location = get_post_meta( $post->ID, '_event_location', true );
        $price    = get_post_meta( $post->ID, '_event_price', true );

        ?>
        <table class="form-table">
            <tr>
                <th><label for="event_date"><?php _e( 'Date', 'events-manager' ); ?></label></th>
                <td><input type="date" id="event_date" name="event_date" value="<?php echo esc_attr( $date ); ?>"></td>
            </tr>
            <tr>
                <th><label for="event_time"><?php _e( 'Time', 'events-manager' ); ?></label></th>
                <td><input type="time" id="event_time" name="event_time" value="<?php echo esc_attr( $time ); ?>"></td>
            </tr>
            <tr>
                <th><label for="event_location"><?php _e( 'Location', 'events-manager' ); ?></label></th>
                <td><input type="text" id="event_location" name="event_location" value="<?php echo esc_attr( $location ); ?>" class="regular-text"></td>
            </tr>
            <tr>
                <th><label for="event_price"><?php _e( 'Price', 'events-manager' ); ?></label></th>
                <td><input type="number" id="event_price" name="event_price" value="<?php echo esc_attr( $price ); ?>" step="0.01" min="0"></td>
            </tr>
        </table>
        <?php
    }

    public function save_meta( $post_id ) {
        if ( ! isset( $_POST['event_meta_nonce'] ) ||
             ! wp_verify_nonce( $_POST['event_meta_nonce'], 'event_meta_nonce' ) ) {
            return;
        }

        if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
            return;
        }

        if ( ! current_user_can( 'edit_post', $post_id ) ) {
            return;
        }

        $fields = array(
            'event_date'     => 'sanitize_text_field',
            'event_time'     => 'sanitize_text_field',
            'event_location' => 'sanitize_text_field',
            'event_price'    => 'floatval',
        );

        foreach ( $fields as $field => $sanitize ) {
            if ( isset( $_POST[ $field ] ) ) {
                $value = call_user_func( $sanitize, $_POST[ $field ] );
                update_post_meta( $post_id, '_' . $field, $value );
            }
        }
    }
}

new Events_Manager();

// Activation hook - flush rewrite rules
register_activation_hook( __FILE__, function() {
    $manager = new Events_Manager();
    $manager->register_post_type();
    $manager->register_taxonomy();
    flush_rewrite_rules();
});

// Deactivation hook
register_deactivation_hook( __FILE__, function() {
    flush_rewrite_rules();
});
```

## Common Mistakes

**Forgetting to flush rewrite rules:**
```php
// 404 errors on CPT pages? Flush once:
flush_rewrite_rules();
// Or: Settings → Permalinks → Save (does the same thing)
```

**Flushing on every request:**
```php
// WRONG - extremely slow
add_action( 'init', function() {
    register_post_type( 'event', $args );
    flush_rewrite_rules();  // Don't do this!
});

// RIGHT - only on activation
register_activation_hook( __FILE__, function() {
    register_event_post_type();
    flush_rewrite_rules();
});
```

**Missing `show_in_rest` for block editor:**
```php
// Block editor won't work without this
'show_in_rest' => true,
```

**Registering too late:**
```php
// WRONG - too late for rewrite rules
add_action( 'wp_loaded', 'register_my_cpt' );

// RIGHT - early enough
add_action( 'init', 'register_my_cpt' );
```

## Further Reading

- [WordPress Hooks System](./02-hooks-system.md) - Understanding actions and filters
- [Database Operations](./03-database-operations.md) - When to use custom tables instead
- [Input Sanitization & Output Escaping](../03-security/03-data-validation.md) - Securing meta box data
- [WordPress CPT Documentation](https://developer.wordpress.org/plugins/post-types/) - Official reference
