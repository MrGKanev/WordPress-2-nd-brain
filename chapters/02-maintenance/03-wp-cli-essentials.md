# WP-CLI Essentials

## Overview

WP-CLI is the command-line interface for WordPress. Tasks that take minutes clicking through the admin can be done in seconds via terminal. It's essential for professional WordPress maintenance.

**Why is it faster?** When you use the admin panel, WordPress has to:
1. Load the entire PHP framework
2. Authenticate your session
3. Render the full HTML admin interface
4. Load all CSS and JavaScript assets
5. Wait for you to click through multiple screens
6. Process each action with full page reloads

WP-CLI bypasses all of this. It runs PHP directly, skips the visual interface entirely, and executes commands immediately. Updating 20 plugins through admin means 20+ page loads and clicks. With WP-CLI, it's one command that completes in seconds.

```bash
# Instead of: Admin → Plugins → Update Available → Select All → Update
# (which involves 4+ page loads and multiple clicks)
wp plugin update --all

# Instead of: Manually checking 50 sites for updates
# (which would take hours through the browser)
for site in site1.com site2.com site3.com; do
    ssh $site "cd /var/www/html && wp core check-update"
done
```

## Installation

Most managed WordPress hosts include WP-CLI. For self-managed servers:

```bash
# Download WP-CLI
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar

# Make it executable
chmod +x wp-cli.phar

# Move to PATH
sudo mv wp-cli.phar /usr/local/bin/wp

# Verify installation
wp --info
```

**Requirements:**
- PHP 5.6+ (7.4+ recommended)
- WordPress 3.7+
- Unix-like environment (Linux, macOS, WSL)

## Core Commands

### WordPress Core Management

```bash
# Check current version
wp core version

# Check for available updates
wp core check-update

# Update WordPress core
wp core update

# Update database after major version upgrade
wp core update-db

# Download WordPress (fresh install)
wp core download

# Install WordPress
wp core install --url="example.com" --title="Site Title" \
    --admin_user="admin" --admin_password="password" \
    --admin_email="admin@example.com"

# Verify core file integrity (detect hacked files)
wp core verify-checksums
```

### Plugin Management

```bash
# List all plugins
wp plugin list

# List only active plugins
wp plugin list --status=active

# Install a plugin
wp plugin install wordpress-seo

# Install and activate
wp plugin install wordpress-seo --activate

# Install specific version
wp plugin install wordpress-seo --version=20.0

# Activate/deactivate
wp plugin activate wordpress-seo
wp plugin deactivate wordpress-seo

# Update single plugin
wp plugin update wordpress-seo

# Update all plugins
wp plugin update --all

# Delete plugin (must be deactivated first)
wp plugin deactivate akismet && wp plugin delete akismet

# Check for plugin vulnerabilities (requires WPVulnDB token)
wp plugin list --fields=name,version,update_version

# Verify plugin checksums (detect tampering)
wp plugin verify-checksums --all
```

### Theme Management

```bash
# List themes
wp theme list

# Install and activate theme
wp theme install flavor --activate

# Update all themes
wp theme update --all

# Delete unused themes (keep one default)
wp theme delete flavor flavor-developer flavor-developer

# Get active theme
wp theme list --status=active --field=name
```

### User Management

```bash
# List all users
wp user list

# Create new user
wp user create bob bob@example.com --role=editor

# Create admin user (useful for recovery)
wp user create emergency admin@example.com --role=administrator --user_pass=temp123

# Update user password
wp user update admin --user_pass=newpassword

# Change user role
wp user set-role bob administrator

# Delete user (reassign content to user ID 1)
wp user delete bob --reassign=1

# List users with specific role
wp user list --role=administrator

# Generate new password for user
wp user reset-password admin --show-password
```

## Database Operations

### Search and Replace

The most powerful WP-CLI feature for migrations. Why is this so important?

WordPress stores URLs throughout the database—in post content, widget settings, theme options, and plugin configurations. Many of these are stored in **serialized PHP arrays**, where a simple find-replace would break the data. For example:

```
a:1:{s:3:"url";s:24:"http://old-domain.com/img";}
```

The `s:24` means "string of 24 characters". If you change the domain with a text editor, the character count becomes wrong and PHP can't unserialize the data. WP-CLI's search-replace is smart enough to update the string length too.

```bash
# Preview changes (dry run) - ALWAYS do this first
wp search-replace 'old-domain.com' 'new-domain.com' --dry-run

# Execute replacement
wp search-replace 'old-domain.com' 'new-domain.com'

# Replace with protocol (http to https migration)
wp search-replace 'http://example.com' 'https://example.com' --dry-run

# Limit to specific tables
wp search-replace 'old' 'new' wp_posts wp_postmeta

# Skip specific tables
wp search-replace 'old' 'new' --skip-tables=wp_users

# Handle serialized data (default, but explicit)
wp search-replace 'old' 'new' --precise

# Export SQL with replacements (for staging → production)
wp search-replace 'staging.example.com' 'example.com' --export=migrated.sql
```

### Database Export/Import

```bash
# Export database
wp db export backup.sql

# Export with specific name pattern
wp db export backup-$(date +%Y%m%d).sql

# Export only specific tables
wp db export --tables=wp_posts,wp_postmeta

# Import database
wp db import backup.sql

# Execute raw SQL
wp db query "SELECT COUNT(*) FROM wp_posts WHERE post_status='publish'"

# Check database size
wp db size --tables

# Optimize tables
wp db optimize

# Repair tables
wp db repair
```

### Useful Database Queries

```bash
# Count published posts
wp db query "SELECT COUNT(*) as total FROM wp_posts WHERE post_status='publish' AND post_type='post'"

# Find largest autoloaded options (performance issue)
wp db query "SELECT option_name, LENGTH(option_value) as size FROM wp_options WHERE autoload='yes' ORDER BY size DESC LIMIT 10"

# Count transients
wp db query "SELECT COUNT(*) FROM wp_options WHERE option_name LIKE '%_transient_%'"

# Delete expired transients
wp transient delete --expired

# Delete all transients
wp transient delete --all
```

## Cache Operations

```bash
# Clear object cache
wp cache flush

# Clear transients (stored in database)
wp transient delete --expired
wp transient delete --all

# Clear rewrite rules (fixes permalink issues)
wp rewrite flush

# Regenerate rewrite rules
wp rewrite flush --hard
```

## Options Management

```bash
# Get option value
wp option get siteurl
wp option get blogname

# Set option value
wp option update blogname "New Site Name"

# Get all autoloaded options
wp option list --autoload=yes

# Disable autoload for problematic option
wp option update option_name --autoload=no

# Delete option
wp option delete unused_plugin_option

# Get option as JSON (useful for complex values)
wp option get sidebars_widgets --format=json
```

## Post and Content Operations

```bash
# List recent posts
wp post list --post_type=post --posts_per_page=10

# Create a post
wp post create --post_title="Test Post" --post_status=publish

# Create post from file
wp post create ./content.txt --post_title="My Post" --post_status=draft

# Delete post (to trash)
wp post delete 123

# Delete post permanently
wp post delete 123 --force

# Update post
wp post update 123 --post_title="Updated Title"

# Generate test posts (for development)
wp post generate --count=50

# Get post meta
wp post meta get 123 _thumbnail_id

# Update post meta
wp post meta update 123 custom_field "new value"

# Delete all posts of a type (careful!)
wp post delete $(wp post list --post_type=revision --format=ids) --force

# Delete all spam comments
wp comment delete $(wp comment list --status=spam --format=ids) --force

# Delete all trashed posts
wp post delete $(wp post list --post_status=trash --format=ids) --force
```

## Cron Management

WP-CLI is ideal for managing WordPress scheduled tasks:

```bash
# List scheduled events
wp cron event list

# Run all due cron events
wp cron event run --due-now

# Run specific cron event
wp cron event run wp_update_plugins

# Schedule a new event
wp cron event schedule my_custom_hook "now + 1 hour"

# Delete scheduled event
wp cron event delete my_custom_hook

# Test if cron is working
wp cron test
```

### Replace wp-cron.php with System Cron

WordPress's built-in cron isn't a real cron system. It only runs when someone visits your site. This means:

- **Low-traffic sites:** Scheduled tasks might run hours late (or not at all if nobody visits)
- **High-traffic sites:** Every visitor triggers a cron check, adding overhead to every page load
- **Unreliable timing:** You can't guarantee when tasks will actually execute

The solution is to disable WordPress's pseudo-cron and use your server's real cron system, which runs on schedule regardless of site traffic.

```php
// In wp-config.php
define( 'DISABLE_WP_CRON', true );
```

```bash
# Add to crontab (crontab -e)
# Run WordPress cron every 5 minutes
*/5 * * * * cd /var/www/html && wp cron event run --due-now > /dev/null 2>&1

# Or for specific user
*/5 * * * * sudo -u www-data /usr/local/bin/wp --path=/var/www/html cron event run --due-now
```

## Maintenance Scripts

### Daily Maintenance Script

```bash
#!/bin/bash
# daily-maintenance.sh

SITE_PATH="/var/www/html"
cd $SITE_PATH

echo "=== WordPress Daily Maintenance ==="
echo "Date: $(date)"

# Verify core files
echo -e "\n--- Verifying core files ---"
wp core verify-checksums

# Check for updates
echo -e "\n--- Checking for updates ---"
wp core check-update
wp plugin list --update=available
wp theme list --update=available

# Clean up database
echo -e "\n--- Database cleanup ---"
wp transient delete --expired
wp db optimize

# Report sizes
echo -e "\n--- Database size ---"
wp db size --tables --format=table | head -20

echo -e "\n=== Maintenance complete ==="
```

### Bulk Update Script

```bash
#!/bin/bash
# update-all.sh

SITE_PATH="/var/www/html"
cd $SITE_PATH

# Create backup first
echo "Creating backup..."
wp db export "backup-$(date +%Y%m%d-%H%M%S).sql"

# Update everything
echo "Updating WordPress core..."
wp core update

echo "Updating database..."
wp core update-db

echo "Updating plugins..."
wp plugin update --all

echo "Updating themes..."
wp theme update --all

# Flush caches
echo "Flushing caches..."
wp cache flush
wp rewrite flush

echo "Updates complete!"
```

### Security Audit Script

```bash
#!/bin/bash
# security-audit.sh

SITE_PATH="/var/www/html"
cd $SITE_PATH

echo "=== Security Audit ==="

# Verify checksums
echo -e "\n--- Core file integrity ---"
wp core verify-checksums
wp plugin verify-checksums --all 2>/dev/null

# List admin users
echo -e "\n--- Administrator accounts ---"
wp user list --role=administrator --fields=ID,user_login,user_email

# Check for default admin username
if wp user get admin --field=ID 2>/dev/null; then
    echo "WARNING: Default 'admin' username exists!"
fi

# List active plugins (potential vulnerabilities)
echo -e "\n--- Active plugins ---"
wp plugin list --status=active --fields=name,version,update_version

# Check file permissions on wp-config.php
echo -e "\n--- wp-config.php permissions ---"
ls -la wp-config.php

echo -e "\n=== Audit complete ==="
```

## Multisite Commands

For WordPress multisite installations:

```bash
# List all sites
wp site list

# Run command on specific site
wp --url=site1.example.com plugin list

# Run command on all sites
wp site list --field=url | xargs -I {} wp --url={} plugin update --all

# Create new site
wp site create --slug=newsite --title="New Site" --email=admin@example.com

# Delete site
wp site delete 2 --yes

# Network activate plugin
wp plugin activate wordpress-seo --network
```

## Custom Commands

You can create custom WP-CLI commands for repetitive tasks:

```php
// In plugin or mu-plugin file
if ( defined( 'WP_CLI' ) && WP_CLI ) {

    /**
     * Cleans up old revisions and optimizes database.
     *
     * ## EXAMPLES
     *
     *     wp maintenance cleanup
     *
     * @when after_wp_load
     */
    WP_CLI::add_command( 'maintenance cleanup', function() {
        global $wpdb;

        // Delete old revisions (keep 5 per post)
        WP_CLI::log( 'Cleaning up revisions...' );

        $deleted = $wpdb->query( "
            DELETE FROM {$wpdb->posts}
            WHERE post_type = 'revision'
            AND ID NOT IN (
                SELECT * FROM (
                    SELECT ID FROM {$wpdb->posts}
                    WHERE post_type = 'revision'
                    ORDER BY post_date DESC
                    LIMIT 99999999
                ) tmp
            )
        " );

        WP_CLI::success( "Deleted $deleted old revisions" );

        // Delete expired transients
        WP_CLI::log( 'Deleting expired transients...' );
        WP_CLI::runcommand( 'transient delete --expired' );

        // Optimize tables
        WP_CLI::log( 'Optimizing database...' );
        WP_CLI::runcommand( 'db optimize' );

        WP_CLI::success( 'Maintenance complete!' );
    });
}
```

## Useful Aliases

Add to `~/.bash_aliases` or `~/.bashrc`:

```bash
# Quick WordPress shortcuts
alias wpp="wp plugin"
alias wpt="wp theme"
alias wpu="wp user"
alias wpc="wp core"

# Common operations
alias wp-update="wp core update && wp plugin update --all && wp theme update --all"
alias wp-backup="wp db export backup-$(date +%Y%m%d).sql"
alias wp-flush="wp cache flush && wp rewrite flush"
alias wp-cleanup="wp transient delete --expired && wp db optimize"

# Safety: always dry-run search-replace first
alias wp-replace="wp search-replace --dry-run"
```

## Command Reference

| Task | Command |
|------|---------|
| Check WP version | `wp core version` |
| Update everything | `wp core update && wp plugin update --all && wp theme update --all` |
| Export database | `wp db export backup.sql` |
| Import database | `wp db import backup.sql` |
| Search/replace | `wp search-replace 'old' 'new' --dry-run` |
| Clear all caches | `wp cache flush && wp transient delete --all` |
| Create admin user | `wp user create admin admin@example.com --role=administrator` |
| Reset password | `wp user update admin --user_pass=newpass` |
| List plugins needing updates | `wp plugin list --update=available` |
| Verify file integrity | `wp core verify-checksums` |
| Flush permalinks | `wp rewrite flush` |
| Run cron | `wp cron event run --due-now` |
| Delete spam comments | `wp comment delete $(wp comment list --status=spam --format=ids)` |
| Delete revisions | `wp post delete $(wp post list --post_type=revision --format=ids) --force` |

## Further Reading

- [Plugin Recommendations](./01-plugin-recommendations.md) - Tools that complement WP-CLI
- [Hosting Selection](./02-hosting-selection.md) - Hosts with WP-CLI support
- [WP-CLI Official Handbook](https://make.wordpress.org/cli/handbook/) - Complete documentation
- [WP-CLI Commands Reference](https://developer.wordpress.org/cli/commands/) - All available commands
