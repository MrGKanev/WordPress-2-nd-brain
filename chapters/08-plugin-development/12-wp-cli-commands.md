# Custom WP-CLI Commands

WP-CLI lets you manage WordPress from the terminal. Adding custom commands to your plugin makes maintenance tasks scriptable, automatable, and faster than clicking through admin screens. Import 10,000 products? Run it from CLI. Clear your plugin's cache? One command. Debug a customer's order? Query it directly.

## When to Add CLI Commands

| Use Case | Why CLI? |
|----------|---------|
| Data imports/exports | No timeout limits, can process millions of rows |
| Cache management | Faster than navigating admin pages |
| Debugging tools | Direct database inspection without UI overhead |
| Maintenance tasks | Scriptable for cron jobs and automation |
| Migration scripts | Run safely with progress output |
| Setup/configuration | Automate initial plugin setup |

## Basic Command Structure

```php
// Only register commands when WP-CLI is active
if ( defined( 'WP_CLI' ) && WP_CLI ) {
    WP_CLI::add_command( 'myplugin', 'MyPlugin_CLI' );
}

class MyPlugin_CLI {

    /**
     * Display plugin status information.
     *
     * ## EXAMPLES
     *
     *     wp myplugin status
     *
     * @when after_wp_load
     */
    public function status( $args, $assoc_args ) {
        $options = get_option( 'myplugin_options', array() );

        WP_CLI::log( 'Plugin version: ' . MYPLUGIN_VERSION );
        WP_CLI::log( 'DB version: ' . get_option( 'myplugin_db_version', 'none' ) );
        WP_CLI::log( 'Feature enabled: ' . ( $options['enable_feature'] ? 'yes' : 'no' ) );

        WP_CLI::success( 'Status check complete.' );
    }
}
```

The docblock matters—it generates the help text users see with `wp help myplugin status`.

## Command Arguments

WP-CLI passes two arrays to your command method:

| Parameter | Type | Example |
|-----------|------|---------|
| `$args` | Positional arguments | `wp myplugin import products.csv` → `$args[0] = 'products.csv'` |
| `$assoc_args` | Named flags | `wp myplugin import --format=json --dry-run` |

```php
/**
 * Import data from a file.
 *
 * ## OPTIONS
 *
 * <file>
 * : Path to the import file.
 *
 * [--format=<format>]
 * : File format.
 * ---
 * default: csv
 * options:
 *   - csv
 *   - json
 * ---
 *
 * [--dry-run]
 * : Preview changes without saving.
 *
 * ## EXAMPLES
 *
 *     wp myplugin import products.csv
 *     wp myplugin import data.json --format=json --dry-run
 *
 * @when after_wp_load
 */
public function import( $args, $assoc_args ) {
    $file    = $args[0];
    $format  = $assoc_args['format'] ?? 'csv';
    $dry_run = isset( $assoc_args['dry-run'] );

    if ( ! file_exists( $file ) ) {
        WP_CLI::error( "File not found: $file" );
        // WP_CLI::error() exits the script
    }

    if ( $dry_run ) {
        WP_CLI::warning( 'Dry run mode — no changes will be saved.' );
    }

    // Process the file...
}
```

## Output Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `WP_CLI::log()` | Regular output | Progress messages |
| `WP_CLI::success()` | Green success message | Task completed |
| `WP_CLI::warning()` | Yellow warning | Non-fatal issues |
| `WP_CLI::error()` | Red error + exit | Fatal problems |
| `WP_CLI::debug()` | Only with `--debug` flag | Verbose diagnostics |
| `WP_CLI::line()` | Raw output, no prefix | Custom formatting |

### Tables

```php
$items = array(
    array( 'id' => 1, 'name' => 'Widget', 'stock' => 42 ),
    array( 'id' => 2, 'name' => 'Gadget', 'stock' => 0 ),
);

// Formatted table
WP_CLI\Utils\format_items( 'table', $items, array( 'id', 'name', 'stock' ) );

// Output:
// +----+--------+-------+
// | id | name   | stock |
// +----+--------+-------+
// | 1  | Widget | 42    |
// | 2  | Gadget | 0     |
// +----+--------+-------+
```

The `--format` flag lets users choose output format (`table`, `csv`, `json`, `yaml`) automatically.

### Progress Bars

Essential for long-running commands:

```php
public function import( $args, $assoc_args ) {
    $rows = myplugin_parse_csv( $args[0] );
    $progress = \WP_CLI\Utils\make_progress_bar( 'Importing', count( $rows ) );

    $success = 0;
    $errors  = 0;

    foreach ( $rows as $row ) {
        try {
            myplugin_process_row( $row );
            $success++;
        } catch ( Exception $e ) {
            WP_CLI::warning( "Row failed: " . $e->getMessage() );
            $errors++;
        }
        $progress->tick();
    }

    $progress->finish();
    WP_CLI::success( "Done. $success imported, $errors errors." );
}
```

## Confirmation Prompts

For destructive operations, always ask:

```php
/**
 * Delete all plugin data.
 *
 * ## OPTIONS
 *
 * [--yes]
 * : Skip confirmation prompt.
 */
public function reset( $args, $assoc_args ) {
    WP_CLI::confirm( 'This will delete ALL plugin data. Continue?', $assoc_args );

    // Only reaches here if confirmed
    global $wpdb;
    $wpdb->query( "TRUNCATE TABLE {$wpdb->prefix}myplugin_logs" );
    delete_option( 'myplugin_options' );

    WP_CLI::success( 'All plugin data has been reset.' );
}
```

Users can pass `--yes` to skip the prompt in automated scripts.

## Practical Examples

### Cache Management

```php
/**
 * Manage plugin cache.
 *
 * ## EXAMPLES
 *
 *     wp myplugin cache flush
 *     wp myplugin cache stats
 */
public function cache( $args, $assoc_args ) {
    $subcommand = $args[0] ?? 'stats';

    if ( $subcommand === 'flush' ) {
        global $wpdb;
        $deleted = $wpdb->query(
            "DELETE FROM {$wpdb->options}
             WHERE option_name LIKE '_transient_myplugin_%'
             OR option_name LIKE '_transient_timeout_myplugin_%'"
        );
        WP_CLI::success( "Flushed $deleted cache entries." );
        return;
    }

    // Stats
    global $wpdb;
    $count = $wpdb->get_var(
        "SELECT COUNT(*) FROM {$wpdb->options}
         WHERE option_name LIKE '_transient_myplugin_%'
         AND option_name NOT LIKE '_transient_timeout_%'"
    );
    $size = $wpdb->get_var(
        "SELECT SUM(LENGTH(option_value)) / 1024
         FROM {$wpdb->options}
         WHERE option_name LIKE '_transient_myplugin_%'"
    );
    WP_CLI::log( "Cached entries: $count" );
    WP_CLI::log( "Cache size: " . round( $size, 2 ) . " KB" );
}
```

### Diagnostic Command

```php
/**
 * Run diagnostics to check plugin health.
 */
public function diagnose( $args, $assoc_args ) {
    $checks = array();

    // Check database table
    global $wpdb;
    $table_exists = $wpdb->get_var(
        $wpdb->prepare( "SHOW TABLES LIKE %s", $wpdb->prefix . 'myplugin_logs' )
    );
    $checks[] = array(
        'check'  => 'Database table',
        'status' => $table_exists ? 'OK' : 'MISSING',
    );

    // Check API connectivity
    $response = wp_remote_get( 'https://api.example.com/health' );
    $checks[] = array(
        'check'  => 'API connectivity',
        'status' => is_wp_error( $response ) ? 'FAILED: ' . $response->get_error_message() : 'OK',
    );

    // Check PHP extensions
    $checks[] = array(
        'check'  => 'PHP JSON extension',
        'status' => extension_loaded( 'json' ) ? 'OK' : 'MISSING',
    );

    // Check DB version
    $db_version = get_option( 'myplugin_db_version', '0' );
    $checks[] = array(
        'check'  => 'DB schema version',
        'status' => $db_version === MYPLUGIN_DB_VERSION ? 'OK (v' . $db_version . ')' : 'OUTDATED (v' . $db_version . ', need v' . MYPLUGIN_DB_VERSION . ')',
    );

    WP_CLI\Utils\format_items( 'table', $checks, array( 'check', 'status' ) );
}
```

## File Organization

Keep CLI commands in a separate file that's only loaded when WP-CLI is available:

```
myplugin/
├── myplugin.php           # Main plugin file
├── includes/
│   ├── class-settings.php
│   └── class-core.php
└── cli/
    └── class-cli.php      # CLI commands
```

```php
// In myplugin.php
if ( defined( 'WP_CLI' ) && WP_CLI ) {
    require_once __DIR__ . '/cli/class-cli.php';
}
```

## Testing CLI Commands

Test commands before shipping:

```bash
# Run with debug output
wp myplugin import test.csv --debug

# Check registered commands
wp help myplugin

# Test with specific site in multisite
wp myplugin status --url=subsite.example.com
```

## Further Reading

- [WP-CLI Essentials](../02-maintenance/03-wp-cli-essentials.md) — Using WP-CLI for site management
- [Background Processing](./10-background-processing.md) — Long tasks beyond CLI timeouts
- [WP-CLI Commands Cookbook](https://make.wordpress.org/cli/handbook/guides/commands-cookbook/) — Official guide
