# WordPress Cron Management

## Overview

WordPress's default cron system (WP-Cron) can be a significant resource drain on any environments, especially on limited hardware. The default implementation triggers on page loads, leading to inconsistent execution and potential CPU spikes. This chapter explores optimizations for cron jobs and background task management.

**Why is page-load triggered cron bad?** Imagine a visitor loads your homepage. WordPress checks "are any scheduled tasks due?" If yes, it runs them *before* sending the page to the visitor. That visitor's page load now includes the time to process email queues, backup tasks, or whatever else is scheduled. They experience a slow page through no fault of their own.

Even worse: on low-traffic sites, scheduled tasks might not run for hours because nobody visited. And on high-traffic sites, every visitor triggers the cron check—adding overhead to every request even when nothing is due.

## Disabling WP-Cron

### Step 1: Disable in wp-config.php

Add this line to your `wp-config.php` file:

```php
define('DISABLE_WP_CRON', true);
```

### Step 2: Set Up System Cron

Create a system cron job that runs the WordPress cron at regular intervals:

```bash
# Run WordPress cron every 15 minutes
*/15 * * * * wget -q -O - https://example.com/wp-cron.php?doing_wp_cron >/dev/null 2>&1

# OR using curl
*/15 * * * * curl -s https://example.com/wp-cron.php?doing_wp_cron >/dev/null 2>&1

# OR using WP-CLI (if installed)
*/15 * * * * cd /var/www/html && wp cron event run --due-now >/dev/null 2>&1
```

For multiple WordPress sites on a single VPS, stagger the cron schedules to avoid simultaneous execution:

```bash
# Site 1: On minute 0, 15, 30, 45
0,15,30,45 * * * * wget -q -O - https://site1.com/wp-cron.php?doing_wp_cron >/dev/null 2>&1

# Site 2: On minute 5, 20, 35, 50
5,20,35,50 * * * * wget -q -O - https://site2.com/wp-cron.php?doing_wp_cron >/dev/null 2>&1
```

## Analyzing Cron Tasks with WP Crontrol

The WP Crontrol plugin provides visibility into scheduled tasks and allows for management of problematic cron jobs.

### Key Functions

1. **View all scheduled events**: Identify frequency and timing
2. **Add/edit/delete cron events**: Modify schedules for better distribution
3. **Run cron events manually**: Test impact without waiting
4. **Debug cron-related issues**: Identify resource-intensive tasks

### Common Resource-Heavy Tasks

- Post revisions cleanup
- Database optimization routines
- Full-site backups
- Site health checks
- SEO reindexing processes
- Analytics processing

### Case Study Example

In the Reddit post, WP Crontrol revealed that Lasso (an affiliate plugin) had 10+ high-frequency jobs causing CPU spikes. By analyzing and adjusting these tasks, server load was significantly reduced.

## Throttling Plugin Resource Usage

### Plugin-Specific Settings

Some plugins offer built-in options to limit resource usage:

```
Lasso: CPU usage limit set to 50% (found in plugin settings)
```

### Plugin Schedule Adjustments

For plugins without direct resource controls:

1. Use WP Crontrol to identify frequent cron jobs
2. Modify schedules for resource-intensive tasks:
   - Change `hourly` tasks to `twicedaily`
   - Change `twicedaily` tasks to `daily`
   - Move heavy processing to off-peak hours

## WordPress Heartbeat API

The WordPress Heartbeat API can cause unnecessary server load:

```javascript
// Add to theme's functions.php to control Heartbeat frequency
function reduce_heartbeat_frequency( $settings ) {
    // Set to 60 seconds
    $settings['interval'] = 60;
    return $settings;
}
add_filter( 'heartbeat_settings', 'reduce_heartbeat_frequency' );

// Disable Heartbeat completely in specific areas
function disable_heartbeat_selectively() {
    global $pagenow;
    // Disable on post edit screens
    if ( 'post.php' === $pagenow || 'post-new.php' === $pagenow ) {
        wp_deregister_script('heartbeat');
    }
}
add_action( 'init', 'disable_heartbeat_selectively', 1 );
```

## Implementation Steps

1. Analyze current cron tasks:
   - Install WP Crontrol
   - Identify high-frequency and resource-intensive tasks

2. Disable WP-Cron and implement system cron:
   - Add `DISABLE_WP_CRON` constant
   - Set up appropriate system cron job

3. Optimize plugin schedules:
   - Reduce frequency of non-critical tasks
   - Stagger tasks to prevent concurrent execution

4. Configure resource limits for plugins where available

5. Monitor server load to verify improvements

## Monitoring Tools

```bash
# Monitor cron jobs
crontab -l

# Check for currently running cron processes
ps aux | grep cron

# View cron log (if logging enabled)
grep CRON /var/log/syslog

# Monitor system load during cron execution
top -b -n 1
```

## WP-CLI Cron Commands

WP-CLI provides the most reliable way to manage cron:

```bash
# List all scheduled events
wp cron event list

# Run all due events
wp cron event run --due-now

# Run a specific event
wp cron event run wp_update_themes

# Delete a scheduled event
wp cron event delete wp_update_themes

# List all registered cron schedules
wp cron schedule list

# Test if cron is working
wp cron test
```

### Recommended System Cron with WP-CLI

```bash
# Every minute — most reliable approach
* * * * * cd /var/www/html && nice -n 15 wp cron event run --due-now --quiet 2>&1 | logger -t wp-cron

# nice -n 15: Lower priority so cron doesn't compete with web requests
# --quiet: No output unless errors
# logger: Send output to syslog instead of email
```

## Action Scheduler

WooCommerce and many modern plugins use Action Scheduler instead of WP-Cron for background tasks. It's a more robust job queue that stores actions in custom database tables.

### Why Action Scheduler is Better Than WP-Cron

| Feature | WP-Cron | Action Scheduler |
|---------|---------|-----------------|
| Storage | `wp_options` (single serialized array) | Dedicated database tables |
| Failure handling | Silent failure | Logged with retry |
| Concurrency | Single-threaded | Multiple runners |
| Monitoring | Requires plugin (WP Crontrol) | Built-in admin UI |
| Scalability | Degrades with many events | Handles millions of actions |
| Debugging | Minimal logging | Full execution logs |

### Running Action Scheduler via CLI

For WooCommerce stores, running Action Scheduler through WP-CLI prevents it from consuming web request resources:

```bash
# Disable the default HTTP-based runner
# Install: https://github.com/woocommerce/action-scheduler-disable-default-runner

# Run via system cron instead
* * * * * cd /var/www/html && nice -n 15 wp action-scheduler run --quiet 2>&1 | logger -t action-scheduler
```

### Monitoring Action Scheduler

```
Tools → Scheduled Actions
```

Watch for:
- **Pending actions piling up** → Cron not running fast enough, increase batch size
- **Failed actions** → Plugin bugs or API timeouts, check logs
- **Long-running actions** → May need chunking (see [Background Processing](../08-plugin-development/10-background-processing.md))

```bash
# Check pending action count via CLI
wp action-scheduler list --status=pending --per-page=0 | wc -l

# Find failed actions
wp action-scheduler list --status=failed --per-page=20
```

## Custom Cron Schedules

WordPress only provides `hourly`, `twicedaily`, and `daily` by default. Add custom intervals:

```php
add_filter( 'cron_schedules', function( $schedules ) {
    $schedules['every_five_minutes'] = array(
        'interval' => 300,
        'display'  => 'Every 5 Minutes',
    );
    $schedules['weekly'] = array(
        'interval' => 604800,
        'display'  => 'Once Weekly',
    );
    return $schedules;
} );
```

### Scheduling Best Practices

| Task Type | Recommended Interval | Why |
|-----------|---------------------|-----|
| Email queue processing | Every 5 minutes | Users expect fast delivery |
| Inventory sync | Every 15-30 minutes | Balance freshness vs API limits |
| Sitemap regeneration | Daily | Content doesn't change that fast |
| Database cleanup | Weekly | No urgency, reduce load |
| Full backup | Daily (off-peak) | Schedule for 2-4 AM |
| Analytics processing | Hourly | Reasonable data freshness |

## Large Task Chunking

Long-running cron tasks risk timeout. Break them into smaller pieces:

```php
add_action( 'myplugin_process_queue', function() {
    $start_time = time();
    $max_runtime = 25; // seconds, leave buffer before PHP timeout
    $batch_size = 50;

    $items = myplugin_get_pending_items( $batch_size );

    foreach ( $items as $item ) {
        if ( ( time() - $start_time ) > $max_runtime ) {
            // Schedule continuation
            wp_schedule_single_event( time(), 'myplugin_process_queue' );
            return;
        }

        myplugin_process_item( $item );
    }
} );
```

This pattern:
1. Processes items until time runs out
2. Schedules itself again for remaining items
3. Prevents PHP timeout regardless of queue size

## Securing wp-cron.php

When using system cron, block direct HTTP access to `wp-cron.php`:

**Nginx:**
```nginx
# Block external access to wp-cron.php
location = /wp-cron.php {
    allow 127.0.0.1;
    allow ::1;
    deny all;
}
```

This only works if your system cron uses WP-CLI (runs locally) rather than HTTP requests.

## Debugging Cron Issues

### Common Problems

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Scheduled events never fire | `DISABLE_WP_CRON` set but no system cron | Add system cron job |
| Events fire late | System cron interval too long | Reduce to 1-minute interval |
| Events fire multiple times | Race condition with multiple cron runners | Use `wp_using_ext_object_cache()` lock or single runner |
| Server load spikes at cron time | Too many heavy tasks scheduled together | Stagger schedules |
| "Missed schedule" warnings | Cron not running reliably | Check system cron is working: `wp cron test` |

### Logging Cron Execution

```php
// Add to wp-config.php for debugging (remove in production)
define( 'WP_CRON_LOCK_TIMEOUT', 120 ); // Increase lock timeout
```

```bash
# Watch cron execution in real-time
tail -f /var/log/syslog | grep -i cron

# Check if wp-cron.php is accessible
curl -I https://example.com/wp-cron.php
```

## Common Pitfalls

- Not properly securing wp-cron.php when using system cron
- Setting cron schedules too infrequently for critical tasks
- Forgetting to update cron URL after domain changes
- Using non-optimized database queries in custom cron tasks
- Running too many concurrent cron jobs
- Scheduling heavy tasks (backups, imports) at the same time
- Not cleaning up scheduled events when deactivating plugins

## Further Reading

- [Background Processing](../08-plugin-development/10-background-processing.md) — Action Scheduler patterns for plugins
- [PHP-FPM Optimization](./03-php-fpm-optimization.md) — Worker pool sizing for cron load
- [WP Crontrol Plugin](https://wordpress.org/plugins/wp-crontrol/) — Visual cron management
- [WP-CLI Cron Commands](https://developer.wordpress.org/cli/commands/cron/) — CLI reference
- [Action Scheduler Documentation](https://actionscheduler.org/) — WooCommerce's job queue
