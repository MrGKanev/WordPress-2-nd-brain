# Background Processing

Some tasks don't belong in a page request. Importing 10,000 products, sending 500 emails, processing image thumbnails—these take minutes, not milliseconds. Running them during a web request means timeouts, white screens, and angry users.

Background processing moves heavy work out of the request cycle. The user clicks a button, the task gets queued, and processing happens in the background while the user continues browsing.

## When You Need Background Processing

| Scenario | Why Background? |
|----------|-----------------|
| Bulk imports (CSV, API sync) | Thousands of records can't process in 30 seconds |
| Email campaigns | Sending hundreds of emails serially would timeout |
| Image processing | Generating thumbnails for bulk uploads |
| Data migration | Moving data between tables or formats |
| API sync | Syncing inventory with external ERP |
| Report generation | Aggregating large datasets |
| Cleanup tasks | Purging old logs, expired sessions |

## WordPress Cron (WP-Cron)

The simplest background processing: schedule a function to run later.

### How WP-Cron Works

WordPress doesn't have real cron. Instead, on every page load, WordPress checks if any scheduled events are overdue and runs them. This means:

- Events only fire when someone visits the site
- Low-traffic sites may miss schedules
- High-traffic sites waste resources checking on every request

**Fix: Use system cron instead.**

```php
// wp-config.php — disable WP-Cron's page-load trigger
define( 'DISABLE_WP_CRON', true );
```

```bash
# System cron — runs every minute reliably
* * * * * cd /path/to/wordpress && wp cron event run --due-now --quiet
```

### Scheduling Events

```php
// Schedule a single event (runs once)
if ( ! wp_next_scheduled( 'myplugin_cleanup' ) ) {
    wp_schedule_single_event( time() + 3600, 'myplugin_cleanup' );
}

// Schedule a recurring event
if ( ! wp_next_scheduled( 'myplugin_daily_sync' ) ) {
    wp_schedule_event( time(), 'daily', 'myplugin_daily_sync' );
}

// Hook the callback
add_action( 'myplugin_cleanup', 'myplugin_run_cleanup' );
add_action( 'myplugin_daily_sync', 'myplugin_run_sync' );
```

### Custom Intervals

```php
add_filter( 'cron_schedules', function( $schedules ) {
    $schedules['every_five_minutes'] = array(
        'interval' => 300,
        'display'  => 'Every 5 Minutes',
    );
    return $schedules;
} );
```

### Cleanup on Deactivation

Always remove scheduled events when your plugin is deactivated:

```php
register_deactivation_hook( __FILE__, function() {
    wp_clear_scheduled_hook( 'myplugin_daily_sync' );
    wp_clear_scheduled_hook( 'myplugin_cleanup' );
} );
```

### WP-Cron Limitations

| Limitation | Impact |
|-----------|--------|
| Single-threaded | Only one cron batch runs at a time |
| 30-second timeout | Long tasks get killed mid-execution |
| No retry logic | Failed tasks just fail silently |
| No progress tracking | Can't show users how far along a task is |
| No prioritization | All events are equal |

For anything beyond simple scheduled tasks, you need Action Scheduler.

## Action Scheduler

Action Scheduler is WooCommerce's battle-tested job queue. It's a library, not a plugin—bundle it with your plugin or rely on WooCommerce providing it.

### Why Action Scheduler

- Handles millions of queued actions
- Built-in retry on failure
- Admin UI for monitoring (Tools → Scheduled Actions)
- Supports groups for organization
- Parallel processing with multiple runners
- Claimed actions prevent duplicate processing

### Installation

If WooCommerce is active, Action Scheduler is already available. Otherwise, bundle it:

```bash
composer require woocommerce/action-scheduler
```

```php
// In your plugin's main file
require_once __DIR__ . '/vendor/woocommerce/action-scheduler/action-scheduler.php';
```

Action Scheduler uses version checking—if multiple plugins bundle it, the newest version loads.

### Basic Usage

```php
// Schedule a single action (runs once, as soon as possible)
as_enqueue_async_action( 'myplugin_process_item', array( $item_id ), 'myplugin' );

// Schedule for a specific time
as_schedule_single_action( strtotime( '+1 hour' ), 'myplugin_send_report', array(), 'myplugin' );

// Schedule recurring
as_schedule_recurring_action( time(), 3600, 'myplugin_hourly_check', array(), 'myplugin' );

// Hook the callback
add_action( 'myplugin_process_item', function( $item_id ) {
    // Process the item
    $item = get_post( $item_id );
    // ... do heavy work ...
} );
```

### Batch Processing Pattern

The most common pattern: break a large job into many small actions.

```php
// User clicks "Import Products" button
function myplugin_start_import( $csv_file ) {
    $rows = myplugin_parse_csv( $csv_file );

    foreach ( $rows as $index => $row ) {
        as_enqueue_async_action(
            'myplugin_import_single_product',
            array( $row ),
            'myplugin-import'
        );
    }

    // Schedule a completion check
    as_schedule_single_action(
        time() + 60,
        'myplugin_check_import_complete',
        array( count( $rows ) ),
        'myplugin-import'
    );
}

add_action( 'myplugin_import_single_product', function( $row ) {
    $product = new WC_Product_Simple();
    $product->set_name( sanitize_text_field( $row['name'] ) );
    $product->set_regular_price( floatval( $row['price'] ) );
    $product->set_sku( sanitize_text_field( $row['sku'] ) );
    $product->save();
} );
```

**Why per-item actions?** If one product fails to import, only that action fails and gets retried. The rest continue normally. With a single bulk action, one failure kills the entire batch.

### Chunked Processing

When you can't create one action per item (too many items would flood the queue):

```php
function myplugin_start_large_export() {
    // Schedule the first chunk
    as_enqueue_async_action(
        'myplugin_export_chunk',
        array( 'offset' => 0 ),
        'myplugin-export'
    );
}

add_action( 'myplugin_export_chunk', function( $args ) {
    $offset    = $args['offset'];
    $per_chunk = 100;

    $products = wc_get_products( array(
        'limit'  => $per_chunk,
        'offset' => $offset,
        'return' => 'ids',
    ) );

    if ( empty( $products ) ) {
        // Done — no more products
        myplugin_finalize_export();
        return;
    }

    // Process this chunk
    foreach ( $products as $product_id ) {
        myplugin_export_product( $product_id );
    }

    // Schedule next chunk
    as_enqueue_async_action(
        'myplugin_export_chunk',
        array( 'offset' => $offset + $per_chunk ),
        'myplugin-export'
    );
} );
```

This is self-chaining: each chunk schedules the next. If the process crashes, only the current chunk is lost—previous chunks are already done.

### Progress Tracking

Users want to know "how far along is this?"

```php
// When starting the job
update_option( 'myplugin_import_progress', array(
    'total'     => count( $rows ),
    'completed' => 0,
    'status'    => 'running',
    'started'   => time(),
) );

// In each action callback
add_action( 'myplugin_import_single_product', function( $row ) {
    // ... process product ...

    // Update progress
    $progress = get_option( 'myplugin_import_progress' );
    $progress['completed']++;
    update_option( 'myplugin_import_progress', $progress );
} );

// AJAX endpoint for the admin to poll
add_action( 'wp_ajax_myplugin_import_status', function() {
    $progress = get_option( 'myplugin_import_progress', array() );
    wp_send_json_success( $progress );
} );
```

### Monitoring and Debugging

Action Scheduler provides an admin screen at **Tools → Scheduled Actions** showing:

| Column | Meaning |
|--------|---------|
| Hook | The action name |
| Status | Pending, Complete, Failed, Canceled |
| Group | Your plugin's group identifier |
| Scheduled | When it should run |
| Log | Execution details and errors |

**Programmatic monitoring:**

```php
// Count pending actions in a group
$pending = as_get_scheduled_actions( array(
    'group'    => 'myplugin-import',
    'status'   => ActionScheduler_Store::STATUS_PENDING,
    'per_page' => 0,
), 'ARRAY_A' );
$count = count( $pending );

// Check if any actions are running
$running = as_has_scheduled_action( 'myplugin_import_single_product' );
```

## Error Handling and Retries

### Action Scheduler Retries

Action Scheduler automatically retries failed actions up to 5 times with exponential backoff. To control this:

```php
add_action( 'myplugin_process_item', function( $item_id ) {
    try {
        $result = myplugin_call_external_api( $item_id );

        if ( is_wp_error( $result ) ) {
            // Throwing an exception triggers Action Scheduler's retry
            throw new Exception( $result->get_error_message() );
        }
    } catch ( Exception $e ) {
        // Log the error
        error_log( 'MyPlugin: Failed to process item ' . $item_id . ': ' . $e->getMessage() );

        // Re-throw to trigger retry
        throw $e;
    }
} );
```

### Manual Retry Logic

For WP-Cron tasks without Action Scheduler:

```php
add_action( 'myplugin_sync_data', function() {
    $result = myplugin_call_api();

    if ( is_wp_error( $result ) ) {
        $retry_count = get_transient( 'myplugin_sync_retries' ) ?: 0;

        if ( $retry_count < 3 ) {
            set_transient( 'myplugin_sync_retries', $retry_count + 1, HOUR_IN_SECONDS );
            // Retry in 5 minutes
            wp_schedule_single_event( time() + 300, 'myplugin_sync_data' );
        } else {
            // Give up, notify admin
            delete_transient( 'myplugin_sync_retries' );
            myplugin_notify_admin( 'Sync failed after 3 retries' );
        }
        return;
    }

    delete_transient( 'myplugin_sync_retries' );
} );
```

## Performance Considerations

### Memory Management

Background tasks run in the same PHP process. Long-running tasks accumulate memory:

```php
add_action( 'myplugin_process_batch', function( $batch ) {
    foreach ( $batch as $item_id ) {
        myplugin_process_item( $item_id );

        // Clear WordPress object cache periodically
        // Prevents memory from growing indefinitely
        if ( $item_id % 50 === 0 ) {
            wp_cache_flush();
        }
    }
} );
```

### Avoiding Lock Contention

Multiple background processes hitting the same database rows causes deadlocks:

```php
// BAD: All workers update the same option
update_option( 'myplugin_last_processed', $item_id );

// BETTER: Use transients with unique keys
set_transient( 'myplugin_processed_' . $item_id, true, DAY_IN_SECONDS );
```

### Time Limits

PHP's `max_execution_time` applies to background tasks too. For chunked processing, check remaining time:

```php
function myplugin_process_chunk() {
    $start = time();
    $items = myplugin_get_pending_items( 100 );

    foreach ( $items as $item ) {
        // Stop if we've been running for more than 20 seconds
        if ( ( time() - $start ) > 20 ) {
            // Schedule remaining items
            as_enqueue_async_action( 'myplugin_process_chunk', array(), 'myplugin' );
            return;
        }

        myplugin_process_item( $item );
    }
}
```

## Decision Matrix

| Need | Solution |
|------|----------|
| Run something once in 1 hour | `wp_schedule_single_event()` |
| Run something daily | `wp_schedule_event()` with system cron |
| Process 100 items in background | Action Scheduler with per-item actions |
| Process 100,000 items | Action Scheduler with chunked self-chaining |
| Real-time background task with progress | Action Scheduler + AJAX polling |
| External webhook processing | Action Scheduler async action from webhook handler |

## Further Reading

- [Cron Management](../04-performance/04-cron-management.md) — WP-Cron optimization and system cron setup
- [Database Operations](./03-database-operations.md) — Transients for progress tracking
- [AJAX Patterns](./05-ajax-patterns.md) — Progress polling from admin UI
- [Action Scheduler Documentation](https://actionscheduler.org/) — Official reference
