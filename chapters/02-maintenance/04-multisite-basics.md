# WordPress Multisite Considerations

## Overview

WordPress Multisite allows running multiple sites from a single WordPress installation. Each site shares the same codebase and database but has its own content, users, and settings. Understanding Multisite is essential when managing large WordPress networks or deploying plugins that need to work across multiple sites.

## When Multisite Makes Sense

**Good use cases:**
- University with department sites
- Company with regional microsites
- Franchise businesses with location pages
- Development agency managing client sites
- Membership with user-created blogs

**Not ideal for:**
- Completely unrelated sites (separate installations better)
- Sites needing different PHP versions or server configs
- When sites need independent scaling
- One-off WordPress projects

## Multisite Architecture

### Database Structure

Multisite uses a single database with multiple tables per site:

```
wp_options           (Main site - ID 1)
wp_posts
wp_postmeta
wp_users             (Shared across all sites)
wp_usermeta          (Shared across all sites)

wp_2_options         (Site ID 2)
wp_2_posts
wp_2_postmeta

wp_3_options         (Site ID 3)
wp_3_posts
wp_3_postmeta

wp_blogs             (Network table - lists all sites)
wp_site              (Network table - network info)
wp_sitemeta          (Network-wide options)
```

### URL Structures

**Subdirectory (path-based):**
```
example.com/site1/
example.com/site2/
example.com/site3/
```

**Subdomain:**
```
site1.example.com
site2.example.com
site3.example.com
```

**Domain mapping:**
```
site1.com → maps to network site
site2.org → maps to network site
```

## Admin Levels

| Role | Scope | Can Do |
|------|-------|--------|
| **Super Admin** | Network | Manage all sites, themes, plugins, network settings |
| **Administrator** | Single site | Manage one site's content, users, settings |
| **Editor/Author/etc.** | Single site | Standard WordPress roles per site |

```php
// Check for Super Admin
if ( is_super_admin() ) {
    // Network-level admin
}

// Check for site admin (on current site)
if ( current_user_can( 'manage_options' ) ) {
    // Site-level admin
}
```

## Plugin Activation

### Network vs. Site Activation

```
Network Activation: Plugin active on ALL sites
Site Activation:    Plugin active only on one site
```

**Network activate:**
- Plugins → Network Activate
- Plugin code runs on every site

**Site activate:**
- Visit specific site's dashboard
- Activate normally
- Only runs on that site

### Detecting Activation Context

```php
// Check if network activated
if ( is_plugin_active_for_network( plugin_basename( __FILE__ ) ) ) {
    // Running network-wide
}

// Different activation hooks
register_activation_hook( __FILE__, 'my_plugin_activate' );

function my_plugin_activate( $network_wide ) {
    if ( $network_wide ) {
        // Network activation - run for all sites
        $sites = get_sites();
        foreach ( $sites as $site ) {
            switch_to_blog( $site->blog_id );
            my_plugin_setup_site();
            restore_current_blog();
        }
    } else {
        // Single site activation
        my_plugin_setup_site();
    }
}

// Handle new sites created after network activation
add_action( 'wp_initialize_site', 'my_plugin_new_site', 10, 2 );

function my_plugin_new_site( $new_site, $args ) {
    if ( is_plugin_active_for_network( plugin_basename( __FILE__ ) ) ) {
        switch_to_blog( $new_site->blog_id );
        my_plugin_setup_site();
        restore_current_blog();
    }
}
```

## Working with Multiple Sites

### Switching Between Sites

```php
// Get all sites
$sites = get_sites( array(
    'number' => 100,
    'public' => 1,
) );

// Loop through sites
foreach ( $sites as $site ) {
    switch_to_blog( $site->blog_id );

    // Now operating in context of $site
    $posts = get_posts();
    $options = get_option( 'my_option' );

    restore_current_blog();
}

// IMPORTANT: Always call restore_current_blog()
// Or use wp_reset_postdata() equivalent for sites
```

### Site-Specific vs. Network-Wide Data

```php
// Site-specific (stored in wp_X_options)
update_option( 'my_setting', $value );
$value = get_option( 'my_setting' );

// Network-wide (stored in wp_sitemeta)
update_site_option( 'my_network_setting', $value );
$value = get_site_option( 'my_network_setting' );

// User meta is always network-wide
update_user_meta( $user_id, 'preference', $value );
```

### Getting Site Information

```php
// Current site
$current_blog_id = get_current_blog_id();
$site = get_site( $current_blog_id );

// Site details
echo $site->blogname;    // Doesn't exist! Use:
echo get_blog_option( $site->blog_id, 'blogname' );
echo $site->domain;
echo $site->path;
echo $site->blog_id;

// Main site
$main_site_id = get_main_site_id();
$is_main = is_main_site();

// All sites
$sites = get_sites( array(
    'orderby' => 'domain',
    'order'   => 'ASC',
) );
```

## Network Admin Menus

```php
// Add menu to Network Admin (Super Admin only)
add_action( 'network_admin_menu', 'my_network_admin_menu' );

function my_network_admin_menu() {
    add_menu_page(
        __( 'Network Settings', 'my-plugin' ),
        __( 'Network Settings', 'my-plugin' ),
        'manage_network_options',  // Network admin capability
        'my-network-settings',
        'my_network_settings_page',
        'dashicons-admin-network'
    );
}

// Different settings for network vs. site
function my_network_settings_page() {
    if ( ! is_super_admin() ) {
        wp_die( __( 'Access denied', 'my-plugin' ) );
    }

    // Handle form submission
    if ( isset( $_POST['my_network_setting'] ) ) {
        check_admin_referer( 'my_network_settings' );
        update_site_option( 'my_setting', sanitize_text_field( $_POST['my_network_setting'] ) );
    }

    $value = get_site_option( 'my_setting', '' );
    // Render form...
}
```

## Plugin Compatibility

### Making Plugins Multisite-Compatible

```php
/**
 * Plugin Name: My Plugin
 * Network: true  // Shows "Network Activate" option
 */

// Check if Multisite is active
if ( is_multisite() ) {
    // Multisite-specific code
}

// Get correct table prefix for current site
global $wpdb;
$table = $wpdb->prefix . 'my_table';  // wp_2_my_table on site 2

// Use base prefix for network-wide tables
$network_table = $wpdb->base_prefix . 'my_network_table';  // wp_my_network_table
```

### Common Compatibility Issues

**1. Hardcoded table prefixes:**
```php
// WRONG
$wpdb->query( "SELECT * FROM wp_posts" );

// RIGHT
$wpdb->query( "SELECT * FROM {$wpdb->posts}" );
```

**2. Assuming single site:**
```php
// WRONG
$upload_dir = wp_upload_dir();
// On site 2: /wp-content/uploads/sites/2/

// RIGHT - still works, but be aware of structure
$upload_dir = wp_upload_dir();
// Returns correct path for current site
```

**3. Shared user tables:**
```php
// Users are network-wide, but roles are per-site
$user = get_user_by( 'id', $user_id );  // Same user network-wide
$roles = $user->roles;  // Roles on CURRENT site only

// Check role on specific site
switch_to_blog( $site_id );
$roles = get_user_by( 'id', $user_id )->roles;
restore_current_blog();
```

**4. Cron jobs:**
```php
// Cron runs per-site
// If you need network-wide cron, schedule on main site only
if ( is_main_site() ) {
    if ( ! wp_next_scheduled( 'my_network_cron' ) ) {
        wp_schedule_event( time(), 'daily', 'my_network_cron' );
    }
}

add_action( 'my_network_cron', 'run_on_all_sites' );

function run_on_all_sites() {
    $sites = get_sites();
    foreach ( $sites as $site ) {
        switch_to_blog( $site->blog_id );
        do_site_specific_task();
        restore_current_blog();
    }
}
```

## Multisite WP-CLI

```bash
# List all sites
wp site list

# Run command on specific site
wp --url=site2.example.com option get blogname

# Run command on all sites
wp site list --field=url | xargs -I {} wp --url={} plugin update --all

# Create new site
wp site create --slug=newsite --title="New Site" --email=admin@example.com

# Delete site
wp site delete 3 --yes

# Network activate plugin
wp plugin activate my-plugin --network

# Get network option
wp network meta get 1 my_network_option
```

## Performance Considerations

### Query Efficiency

```php
// Avoid this pattern when possible
$sites = get_sites();
foreach ( $sites as $site ) {
    switch_to_blog( $site->blog_id );
    // Query runs on each site - slow with many sites
    $posts = get_posts();
    restore_current_blog();
}

// Better: Direct database query when appropriate
global $wpdb;
$results = $wpdb->get_results( "
    SELECT blog_id, option_value
    FROM {$wpdb->base_prefix}blogs b
    JOIN {$wpdb->base_prefix}%d_options o ON 1=1
    WHERE o.option_name = 'my_option'
" );
```

### Object Cache Key Collisions

```php
// Object cache keys should include blog ID
$cache_key = 'my_data_' . get_current_blog_id();
wp_cache_set( $cache_key, $data, 'my_group' );

// Or use blog-aware group
wp_cache_set( 'my_data', $data, 'my_group_blog_' . get_current_blog_id() );
```

### Shared Resources

```php
// Themes/plugins are shared (one copy serves all sites)
// This is a performance advantage - less disk usage

// But be careful with paths
$plugin_path = plugin_dir_path( __FILE__ );  // Same for all sites
$upload_path = wp_upload_dir()['basedir'];   // Different per site
```

## Database Maintenance

```bash
# Optimize all site tables
wp site list --field=url | xargs -I {} wp --url={} db optimize

# Check database sizes
wp db query "SELECT table_name,
    round(((data_length + index_length) / 1024 / 1024), 2) as 'Size (MB)'
    FROM information_schema.TABLES
    WHERE table_schema = 'wordpress'
    ORDER BY (data_length + index_length) DESC
    LIMIT 20;"
```

## Migration Considerations

### Moving to Multisite

1. Back up everything
2. Convert to Multisite (edit wp-config.php, .htaccess)
3. Test thoroughly
4. Migrate additional sites as needed

### Moving from Multisite

More complex - each site needs:
1. Export content
2. Export database tables (with prefix changes)
3. Move uploads (from sites/X folder)
4. Reconfigure plugins and themes

## Multisite Checklist

When deploying plugins on Multisite:

- [ ] Test with both site and network activation
- [ ] Handle `wp_initialize_site` for new sites
- [ ] Use `$wpdb->prefix` not hardcoded prefixes
- [ ] Store network data in `wp_sitemeta` with `*_site_option()`
- [ ] Store site data in `wp_X_options` with `*_option()`
- [ ] Include blog ID in cache keys
- [ ] Test `switch_to_blog()` / `restore_current_blog()` patterns
- [ ] Check permissions with `is_super_admin()` for network features
- [ ] Test with subdomain AND subdirectory configurations

## Further Reading

- [WP-CLI Essentials](./03-wp-cli-essentials.md) - Command-line Multisite management
- [Database Operations](../08-plugin-development/03-database-operations.md) - Table prefixes and queries
- [WordPress Multisite Documentation](https://developer.wordpress.org/advanced-administration/multisite/) - Official guide
