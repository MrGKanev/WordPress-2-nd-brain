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

## Common Pitfalls

- Not properly securing wp-cron.php when using system cron
- Setting cron schedules too infrequently for critical tasks
- Forgetting to update cron URL after domain changes
- Using non-optimized database queries in custom cron tasks
- Running too many concurrent cron jobs

## Resources

- [WP Crontrol Plugin](https://wordpress.org/plugins/wp-crontrol/)
- [WP-CLI Cron Commands](https://developer.wordpress.org/cli/commands/cron/)
- [WordPress Cron API Documentation](https://developer.wordpress.org/plugins/cron/)
