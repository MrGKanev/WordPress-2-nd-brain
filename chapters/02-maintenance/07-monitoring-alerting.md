# Monitoring & Alerting

You can't fix what you don't know is broken. Monitoring tells you when something goes wrong — ideally before users notice. The goal isn't dashboards for their own sake; it's getting the right alert to the right person at the right time.

## What to Monitor

### The Four Golden Signals

| Signal | What It Measures | WordPress Context |
|--------|-----------------|-------------------|
| **Latency** | How long requests take | TTFB, page load time |
| **Traffic** | Volume of requests | Page views, API calls |
| **Errors** | Rate of failed requests | 500 errors, PHP fatals |
| **Saturation** | How full the system is | CPU, memory, disk, PHP-FPM workers |

If you only monitor four things, monitor these.

## Uptime Monitoring

The most basic and most critical monitor. Is the site responding?

### Services

| Service | Free Tier | Check Interval | Features |
|---------|-----------|---------------|----------|
| **UptimeRobot** | 50 monitors, 5-min | 5 min (free), 1 min (paid) | HTTP, keyword, port, heartbeat |
| **Better Uptime** (Better Stack) | 10 monitors | 3 min | Incident management, status pages |
| **Uptime Kuma** | Self-hosted (free) | 1 min+ | Open-source, full control |
| **Hetrixtools** | 15 monitors | 1 min | Blacklist monitoring, SSL checks |
| **Pingdom** | No free tier | 1 min | RUM, transaction monitoring |
| **Oh Dear** | No free tier | Custom | Broken links, mixed content, certificate checks |

### What to Check

| Check | URL/Method | Why |
|-------|-----------|-----|
| Homepage | `GET /` | Basic availability |
| wp-admin login | `GET /wp-login.php` | Admin functionality |
| Keyword check | Look for "specific text" on page | Confirms real content, not error page |
| SSL certificate | Certificate expiry | 14-day warning before expiry |
| DNS resolution | DNS lookup | Catch DNS misconfigurations |

### Setting Up UptimeRobot

1. Create monitor: HTTP(S), URL, 5-minute interval
2. Add keyword check: verify a word that only appears on the real page
3. Set alert contacts: email + Telegram/Slack/SMS
4. Create status page (optional): share with clients

### Self-Hosted: Uptime Kuma

For those who prefer controlling their monitoring infrastructure:

```bash
# Docker setup
docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma
```

Supports HTTP, TCP, DNS, Docker, push, and more. Notifications via Slack, Telegram, Discord, email, webhooks.

## Performance Monitoring

### Server-Level Metrics

| Metric | Warning Threshold | Critical Threshold | Tool |
|--------|-------------------|-------------------|------|
| CPU usage | >70% sustained | >90% | Netdata, htop |
| Memory usage | >80% | >95% | Netdata, free -m |
| Disk usage | >80% | >90% | df -h, alerts |
| PHP-FPM workers busy | >80% pool | All workers busy | pm.status_path |
| MySQL connections | >80% max | At max_connections | mysqladmin status |

### Netdata (Free Server Monitoring)

Netdata provides real-time server metrics with zero configuration:

```bash
# Install
curl https://get.netdata.cloud/kickstart.sh > /tmp/netdata-kickstart.sh && sh /tmp/netdata-kickstart.sh
```

Key dashboards for WordPress servers:
- **System Overview**: CPU, RAM, disk I/O
- **PHP-FPM**: Active processes, request duration
- **MySQL/MariaDB**: Queries, connections, slow queries
- **Nginx**: Requests per second, connections, response codes

### Application Performance Monitoring (APM)

APM tools trace individual requests through your application, showing exactly where time is spent:

| Service | Cost | WordPress Integration |
|---------|------|----------------------|
| **New Relic** | Free tier (100GB/month) | PHP agent + WordPress plugin |
| **Query Monitor** | Free plugin | Development only (not production) |
| **Perfmatters** | $24.95/year | Built-in performance tracking |

New Relic's PHP agent is the most thorough — it shows time spent in each function, database query timing, and external HTTP call latency. The free tier is generous for single-site monitoring.

## Error Tracking

### PHP Error Logging

```php
// wp-config.php — production error logging
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );     // Log to wp-content/debug.log
define( 'WP_DEBUG_DISPLAY', false ); // Don't show errors to visitors
```

### Log Management

The `debug.log` file grows unbounded. Manage it:

```bash
# Rotate debug.log weekly, keep 4 copies
# /etc/logrotate.d/wordpress
/var/www/html/wp-content/debug.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
    create 640 www-data www-data
}
```

### Centralized Error Tracking

For sites where you need more than log files:

| Service | Cost | Features |
|---------|------|----------|
| **Sentry** | Free (5K errors/month) | Stack traces, context, release tracking |
| **Bugsnag** | Free (7.5K events/month) | Error grouping, breadcrumbs |
| **Rollbar** | Free (5K events/month) | Real-time alerts, deploy tracking |

### WP-CLI Log Monitoring

```bash
# Watch for PHP errors in real-time
wp eval 'error_log("test");' && tail -f /var/www/html/wp-content/debug.log

# Check for recent fatal errors
grep -i "fatal\|critical" /var/www/html/wp-content/debug.log | tail -20

# Monitor WordPress cron errors
grep "cron" /var/log/syslog | tail -20
```

## Security Monitoring

### File Integrity Monitoring

Detect unauthorized file changes:

| Tool | How It Works |
|------|-------------|
| **Wordfence** | Compares core/plugin/theme files against originals |
| **OSSEC** | Host-based intrusion detection, file integrity |
| **inotifywait** | Linux kernel-level file change monitoring |

### Login Monitoring

| What to Track | Alert When |
|--------------|------------|
| Failed login attempts | >10 in 5 minutes (brute force) |
| Successful admin login | New IP address |
| Password resets | Any admin password reset |
| User role changes | User promoted to admin |

### Plugins for Security Monitoring

| Plugin | Focus |
|--------|-------|
| **WP Activity Log** | Complete audit trail of all WordPress actions |
| **Wordfence** | Security scanning + firewall + login security |
| **Sucuri Security** | File integrity + security hardening |

## Alerting Strategy

### Alert Channels

| Channel | Response Time | Best For |
|---------|-------------|----------|
| **SMS/Phone call** | Immediate | Site down, security breach |
| **Slack/Telegram** | Minutes | Warnings, non-critical alerts |
| **Email** | Hours | Reports, summaries, low-priority |
| **Dashboard** | When checked | Trends, historical data |

### Alert Fatigue Prevention

| Rule | Why |
|------|-----|
| Only alert on actionable events | If you can't do anything about it, don't alert |
| Group related alerts | 50 "page slow" alerts = 1 "site performance degraded" |
| Set appropriate thresholds | CPU at 60% for 10 seconds isn't worth waking up for |
| Differentiate warning vs critical | Yellow = investigate soon. Red = investigate now |
| Review and tune monthly | Remove alerts nobody acts on |

## WordPress Health Check

WordPress 5.1+ includes a built-in Site Health tool:

```
Dashboard → Tools → Site Health
```

It checks:
- PHP version, MySQL version
- HTTPS status
- Plugin/theme update status
- REST API availability
- Scheduled events (cron)
- Debug mode status
- File permissions

### Monitoring Site Health Programmatically

```php
// Get site health status via WP-CLI
// wp eval 'var_dump( get_transient( "health-check-site-status-result" ) );'

// Or hook into health check results
add_filter( 'site_status_tests', function( $tests ) {
    $tests['direct']['custom_check'] = array(
        'label' => __( 'Custom Health Check' ),
        'test'  => function() {
            // Your custom check logic
            return array(
                'label'       => 'Custom check passed',
                'status'      => 'good', // good, recommended, critical
                'badge'       => array( 'label' => 'Performance', 'color' => 'blue' ),
                'description' => 'Everything looks fine.',
                'test'        => 'custom_check',
            );
        },
    );
    return $tests;
} );
```

## Monitoring Checklist

- [ ] Uptime monitoring configured (5-minute or better interval)
- [ ] SSL certificate expiry alerts (14+ days before expiry)
- [ ] Server resource alerts (CPU, memory, disk)
- [ ] PHP error logging enabled (not displayed to visitors)
- [ ] Log rotation configured for debug.log
- [ ] Alert channels set up (at least email + one instant channel)
- [ ] File integrity monitoring active
- [ ] Login attempt monitoring enabled
- [ ] Site Health showing no critical issues
- [ ] Monitoring tested (verify alerts actually arrive)

## Further Reading

- [Debugging & Profiling Tools](../04-performance/10-debugging-profiling.md) — Development-time debugging
- [Server-Level Hardening](../03-security/02-server-hardening.md) — Server security configuration
- [Incident Response](../03-security/05-incident-response.md) — When monitoring catches something bad
- [Email Deliverability](./06-email-deliverability.md) — Ensuring alert emails arrive
