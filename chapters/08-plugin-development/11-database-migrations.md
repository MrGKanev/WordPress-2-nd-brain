# Database Migrations

Your plugin's first version stores data one way. Version 2 needs a new column. Version 3 renames a table. Version 4 moves data from post meta to a custom table. Each of these requires a migration—code that transforms the database schema or data from one version to the next.

Get this wrong and you corrupt user data. Get it right and upgrades are seamless.

## When You Need Migrations

| Change | Migration Needed? | Approach |
|--------|------------------|----------|
| Adding a new option | No | `get_option()` with default handles it |
| Adding a column to custom table | Yes | `dbDelta()` |
| Renaming a column | Yes | `ALTER TABLE` + data copy |
| Moving data between tables | Yes | Custom migration function |
| Changing option structure | Yes | Transform on upgrade |
| Adding a new custom table | Yes | `dbDelta()` |

If you only use the Options API and post meta, you rarely need migrations. Custom tables are where migration discipline becomes essential.

## Schema Versioning

Track your schema version in the database. On every admin load, compare it to the current plugin version and run any pending migrations.

```php
define( 'MYPLUGIN_DB_VERSION', '3' );

add_action( 'plugins_loaded', 'myplugin_check_db_version' );

function myplugin_check_db_version() {
    $installed_version = get_option( 'myplugin_db_version', '0' );

    if ( version_compare( $installed_version, MYPLUGIN_DB_VERSION, '<' ) ) {
        myplugin_run_migrations( $installed_version );
    }
}
```

**Why `plugins_loaded` and not `init`?** It runs earlier, before most of WordPress loads. Migrations should happen before your plugin tries to use the updated schema.

## Creating Tables with dbDelta()

`dbDelta()` is WordPress's schema management function. It compares the desired schema against the existing table and applies only the necessary changes (add columns, add indexes). It will **not** rename or remove columns.

```php
function myplugin_create_tables() {
    global $wpdb;

    $table_name      = $wpdb->prefix . 'myplugin_logs';
    $charset_collate = $wpdb->get_charset_collate();

    // dbDelta is VERY picky about formatting:
    // - Two spaces after PRIMARY KEY
    // - Column definitions on separate lines
    // - No trailing commas
    // - Must use $charset_collate
    $sql = "CREATE TABLE $table_name (
        id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
        user_id bigint(20) unsigned NOT NULL DEFAULT 0,
        action varchar(50) NOT NULL DEFAULT '',
        message text NOT NULL,
        created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY  (id),
        KEY user_id (user_id),
        KEY action (action),
        KEY created_at (created_at)
    ) $charset_collate;";

    require_once ABSPATH . 'wp-admin/includes/upgrade.php';
    dbDelta( $sql );
}
```

### dbDelta Quirks

`dbDelta()` is powerful but unforgiving. These formatting rules are not optional:

| Rule | Wrong | Right |
|------|-------|-------|
| PRIMARY KEY spacing | `PRIMARY KEY (id)` | `PRIMARY KEY  (id)` (two spaces) |
| Key syntax | `KEY (column)` | `KEY key_name (column)` |
| Line endings | Mixed | Each column on its own line |
| Trailing commas | `created_at datetime,)` | No trailing comma before `)` |

### What dbDelta Can and Cannot Do

| Operation | Supported? |
|-----------|-----------|
| Create new table | Yes |
| Add new column | Yes |
| Add new index | Yes |
| Change column type | Partial (may not work reliably) |
| Rename column | No |
| Remove column | No |
| Remove index | No |
| Rename table | No |

For operations `dbDelta()` can't handle, use direct SQL via `$wpdb->query()`.

## Migration Runner

A structured approach to running migrations sequentially:

```php
function myplugin_run_migrations( $from_version ) {
    $migrations = array(
        '1' => 'myplugin_migrate_v1',  // Initial table creation
        '2' => 'myplugin_migrate_v2',  // Add status column
        '3' => 'myplugin_migrate_v3',  // Move data from post meta
    );

    foreach ( $migrations as $version => $callback ) {
        if ( version_compare( $from_version, $version, '<' ) ) {
            call_user_func( $callback );
            update_option( 'myplugin_db_version', $version );
        }
    }
}

function myplugin_migrate_v1() {
    myplugin_create_tables();
}

function myplugin_migrate_v2() {
    global $wpdb;
    $table = $wpdb->prefix . 'myplugin_logs';

    // Add column if it doesn't exist
    $column_exists = $wpdb->get_results(
        $wpdb->prepare(
            "SHOW COLUMNS FROM $table LIKE %s",
            'status'
        )
    );

    if ( empty( $column_exists ) ) {
        $wpdb->query( "ALTER TABLE $table ADD COLUMN status varchar(20) NOT NULL DEFAULT 'active' AFTER message" );
        $wpdb->query( "ALTER TABLE $table ADD KEY status (status)" );
    }
}

function myplugin_migrate_v3() {
    global $wpdb;
    $table = $wpdb->prefix . 'myplugin_logs';

    // Move data from post meta to custom table
    $rows = $wpdb->get_results(
        "SELECT post_id, meta_value FROM {$wpdb->postmeta}
         WHERE meta_key = '_myplugin_log_data'"
    );

    foreach ( $rows as $row ) {
        $data = maybe_unserialize( $row->meta_value );
        $wpdb->insert( $table, array(
            'user_id' => $data['user_id'] ?? 0,
            'action'  => $data['action'] ?? '',
            'message' => $data['message'] ?? '',
        ), array( '%d', '%s', '%s' ) );
    }

    // Clean up old meta (optional, could keep for rollback)
    // $wpdb->delete( $wpdb->postmeta, array( 'meta_key' => '_myplugin_log_data' ) );
}
```

**Update the version after each migration, not at the end.** If migration v2 succeeds but v3 crashes, you don't want to re-run v2 next time.

## Safe Migration Practices

### Always Check Before Altering

```php
// Check if table exists
function myplugin_table_exists( $table_name ) {
    global $wpdb;
    return $wpdb->get_var(
        $wpdb->prepare( "SHOW TABLES LIKE %s", $table_name )
    ) === $table_name;
}

// Check if column exists
function myplugin_column_exists( $table_name, $column_name ) {
    global $wpdb;
    return ! empty( $wpdb->get_results(
        $wpdb->prepare(
            "SHOW COLUMNS FROM $table_name LIKE %s",
            $column_name
        )
    ) );
}
```

### Large Data Migrations

Moving thousands of rows in one request will timeout. Use batched processing:

```php
function myplugin_migrate_v3() {
    $batch_size = 500;
    $offset     = 0;

    do {
        global $wpdb;
        $rows = $wpdb->get_results( $wpdb->prepare(
            "SELECT post_id, meta_value FROM {$wpdb->postmeta}
             WHERE meta_key = '_myplugin_log_data'
             LIMIT %d OFFSET %d",
            $batch_size,
            $offset
        ) );

        foreach ( $rows as $row ) {
            // Process each row...
        }

        $offset += $batch_size;

        // Free memory
        wp_cache_flush();

    } while ( count( $rows ) === $batch_size );
}
```

For very large datasets (100,000+ rows), consider using [Action Scheduler](./10-background-processing.md) to run migrations in the background.

### Transaction Safety

Wrap multi-step changes in transactions when possible:

```php
function myplugin_migrate_with_transaction() {
    global $wpdb;

    $wpdb->query( 'START TRANSACTION' );

    try {
        $wpdb->query( "ALTER TABLE {$wpdb->prefix}myplugin_data ADD COLUMN new_col varchar(255)" );
        $wpdb->query( "UPDATE {$wpdb->prefix}myplugin_data SET new_col = old_col" );
        $wpdb->query( "ALTER TABLE {$wpdb->prefix}myplugin_data DROP COLUMN old_col" );

        $wpdb->query( 'COMMIT' );
    } catch ( Exception $e ) {
        $wpdb->query( 'ROLLBACK' );
        error_log( 'Migration failed: ' . $e->getMessage() );
    }
}
```

**Note:** `ALTER TABLE` causes an implicit commit in MySQL. Transactions are most useful for data transformations (INSERT, UPDATE, DELETE), not schema changes.

## Activation and Uninstall

### On Activation

Run the initial migration when the plugin is first activated:

```php
register_activation_hook( __FILE__, 'myplugin_activate' );

function myplugin_activate() {
    myplugin_check_db_version();
}
```

### On Uninstall

Clean up everything when the plugin is deleted (not just deactivated):

```php
// uninstall.php (in plugin root)
if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
    exit;
}

global $wpdb;

// Remove custom tables
$wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}myplugin_logs" );

// Remove options
delete_option( 'myplugin_db_version' );
delete_option( 'myplugin_options' );

// Remove post meta
$wpdb->delete( $wpdb->postmeta, array( 'meta_key' => '_myplugin_data' ) );

// Remove user meta
$wpdb->delete( $wpdb->usermeta, array( 'meta_key' => '_myplugin_preference' ) );

// Remove transients
$wpdb->query(
    "DELETE FROM {$wpdb->options}
     WHERE option_name LIKE '_transient_myplugin_%'
     OR option_name LIKE '_transient_timeout_myplugin_%'"
);
```

## Multisite Considerations

On multisite, each site has its own tables. Migrations must run per-site:

```php
function myplugin_network_migrate() {
    if ( is_multisite() ) {
        $sites = get_sites( array( 'number' => 0 ) );
        foreach ( $sites as $site ) {
            switch_to_blog( $site->blog_id );
            myplugin_check_db_version();
            restore_current_blog();
        }
    } else {
        myplugin_check_db_version();
    }
}
```

## Further Reading

- [Database Operations](./03-database-operations.md) — Options API, meta tables, custom tables
- [Background Processing](./10-background-processing.md) — Async migrations for large datasets
- [Plugin Structure](./01-plugin-structure.md) — Activation/deactivation lifecycle
- [WordPress dbDelta Documentation](https://developer.wordpress.org/reference/functions/dbdelta/)
