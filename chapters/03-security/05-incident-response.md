# Incident Response

Your site got hacked. Your stomach drops. Now what?

The difference between a 2-hour recovery and a 2-week nightmare is having a plan before it happens. This guide covers what to do when you discover a compromise, how to clean it up, and how to prevent it from happening again.

## Signs of Compromise

### Obvious Signs

- Defaced pages or injected content (pharma spam, redirects)
- Google Search Console security warnings
- Hosting provider suspended your account
- Users reporting malware warnings from browsers
- Unexpected admin accounts
- Strange files in your web root

### Subtle Signs

| Indicator | Where to Check |
|-----------|---------------|
| Unusual outbound traffic | Server access logs, hosting bandwidth reports |
| New or modified PHP files | `find` command with recent modification times |
| Database entries with encoded content | `wp_options`, `wp_posts` post_content |
| Modified .htaccess or wp-config.php | File integrity monitoring |
| Cron jobs you didn't create | `wp cron event list`, system crontab |
| Unfamiliar user accounts | `wp user list --role=administrator` |
| Suspicious redirect rules | Browser network tab, `curl -I` checks |

## Immediate Response (First 30 Minutes)

### 1. Don't Panic, Don't Delete

Your first instinct will be to start deleting things. Resist it. You need to understand *how* the attacker got in before you clean up, or they'll get back in through the same hole.

### 2. Document Everything

Before touching anything:

```bash
# Capture current state
wp db export /tmp/compromised-db-$(date +%Y%m%d).sql
tar -czf /tmp/compromised-files-$(date +%Y%m%d).tar.gz /path/to/wordpress/

# List recently modified files (last 7 days)
find /path/to/wordpress/ -type f -mtime -7 -name '*.php' > /tmp/recent-changes.txt

# Check for suspicious files
find /path/to/wordpress/ -type f -name '*.php' -newer /path/to/wordpress/wp-includes/version.php

# List all admin users
wp user list --role=administrator --fields=ID,user_login,user_email,user_registered

# Check cron jobs
wp cron event list
crontab -l
```

Save all this evidence before making changes. If law enforcement or cyber insurance gets involved, they'll need unmodified evidence.

### 3. Limit the Damage

```bash
# Put site in maintenance mode
wp maintenance-mode activate

# Or manually create maintenance file
echo '<?php $upgrading = time(); ?>' > /path/to/wordpress/.maintenance
```

If you have access:
- Change all admin passwords immediately
- Revoke all active sessions: `wp user session destroy --all`
- Change database password and update `wp-config.php`
- Change WordPress secret keys (forces all logged-in users to re-authenticate)

```bash
# Generate new salts
wp config shuffle-salts
```

## Investigation

### Finding the Entry Point

Most WordPress hacks exploit one of:

1. **Outdated plugin with known vulnerability** — Check plugin versions against [WPScan Vulnerability Database](https://wpscan.com/plugins)
2. **Weak or compromised password** — Check failed login attempts in server logs
3. **File upload vulnerability** — Look for PHP files in `wp-content/uploads/`
4. **Compromised hosting account** — Other sites on the same server might be infected

### Scanning for Malware

```bash
# Find PHP files in uploads directory (shouldn't be there)
find wp-content/uploads/ -name '*.php' -type f

# Find files with base64_decode (common in obfuscated malware)
grep -rl 'base64_decode' wp-content/ --include='*.php'

# Find recently modified core files (should never change)
wp core verify-checksums

# Find modified plugin files
wp plugin verify-checksums --all
```

### Common Malware Patterns

| Pattern | What It Does |
|---------|-------------|
| Obfuscated code with `base64_decode` | Hides malicious payload in encoded strings |
| `@include` in theme headers | Loads malicious code from hidden file |
| PHP files in `uploads/` | Backdoor scripts accessible via URL |
| Modified `wp-blog-header.php` | Injects code on every page load |
| Entries in `wp_options` with encoded values | Stored malware that executes via hooks |
| `.ico` files that are actually PHP | Disguised backdoors |
| `.htaccess` redirect rules | Sends visitors to malicious sites |

### Server Log Analysis

```bash
# Find POST requests to unusual files (potential backdoor access)
grep 'POST' /var/log/nginx/access.log | grep -v 'wp-admin\|wp-login\|admin-ajax\|wp-cron' | tail -100

# Find requests to PHP files in uploads
grep 'uploads.*\.php' /var/log/nginx/access.log

# Find requests from the attacker's IP (once identified)
grep '123.45.67.89' /var/log/nginx/access.log
```

## Cleanup

### Option A: Clean Restore (Recommended)

If you have a known-good backup from before the compromise:

1. **Identify when the compromise began** (from logs and file timestamps)
2. **Restore the backup** from before that date
3. **Update everything** immediately after restore
4. **Change all credentials** (passwords, salts, API keys)
5. **Verify** the restored site is clean

```bash
# Restore database from backup
wp db import backup-clean.sql

# Restore files from backup
rsync -av --delete backup/ /path/to/wordpress/

# Update everything
wp core update
wp plugin update --all
wp theme update --all

# Reset salts
wp config shuffle-salts
```

### Option B: Manual Cleanup

When you don't have a clean backup:

**Step 1: Replace WordPress core**

```bash
# Download fresh WordPress core (overwrites all core files)
wp core download --force

# Verify core integrity
wp core verify-checksums
```

**Step 2: Replace plugins and themes**

```bash
# Reinstall all plugins from fresh copies
wp plugin install $(wp plugin list --field=name --status=active) --force

# Reinstall active theme
wp theme install $(wp theme list --field=name --status=active) --force
```

**Step 3: Clean the database**

```sql
-- Find suspicious content in posts
SELECT ID, post_title FROM wp_posts
WHERE post_content LIKE '%base64_decode%'
   OR post_content LIKE '%<script%src=%';

-- Find suspicious options
SELECT option_name, LEFT(option_value, 100)
FROM wp_options
WHERE option_value LIKE '%base64%'
   OR option_name LIKE 'wp_cd_%';

-- Remove unauthorized admin users
-- (verify IDs first!)
-- wp user delete 999 --reassign=1
```

**Step 4: Check wp-config.php**

Compare your `wp-config.php` against a clean version. Look for:
- Extra `include` or `require` statements
- Suspicious `define()` constants
- Code above the opening `<?php` tag

**Step 5: Clean uploads directory**

```bash
# Remove any PHP files from uploads
find wp-content/uploads/ -name '*.php' -delete

# Remove suspicious file types
find wp-content/uploads/ -name '*.suspected' -delete
find wp-content/uploads/ -name '.htaccess' -delete
```

## Post-Cleanup Hardening

After cleaning, prevent re-infection:

### Immediate Actions

- [ ] Update all passwords (WordPress, database, FTP, hosting panel)
- [ ] Regenerate WordPress salts
- [ ] Update all plugins and themes
- [ ] Remove unused plugins and themes (delete, not just deactivate)
- [ ] Enable two-factor authentication on all admin accounts
- [ ] Review and remove suspicious user accounts
- [ ] Request Google review if site was flagged (Search Console → Security Issues)

### Structural Changes

- [ ] Block PHP execution in uploads: add to `wp-content/uploads/.htaccess`:

```apache
<Files "*.php">
    Deny from all
</Files>
```

- [ ] Set correct file permissions:

```bash
# Directories: 755, Files: 644, wp-config: 600
find /path/to/wordpress/ -type d -exec chmod 755 {} \;
find /path/to/wordpress/ -type f -exec chmod 644 {} \;
chmod 600 wp-config.php
```

- [ ] Implement Cloudflare or WAF protection
- [ ] Set up file integrity monitoring
- [ ] Configure automated off-site backups

## Preventing Future Incidents

| Layer | Action | Tools |
|-------|--------|-------|
| Network | WAF, DDoS protection | Cloudflare, Sucuri |
| Server | Fail2ban, SSH keys, firewall | iptables, ufw |
| Application | Updates, minimal plugins, strong passwords | WP-CLI automation |
| Monitoring | Uptime, file integrity, log analysis | UptimeRobot, Wordfence (scan only) |
| Backups | Daily automated, off-site, tested | UpdraftPlus, host backups |

## Communication

### If User Data Was Compromised

GDPR requires notification within 72 hours:

1. **Assess the breach** — What data was accessed? How many users affected?
2. **Notify the supervisory authority** — Within 72 hours of discovery
3. **Notify affected users** — If breach poses high risk to their rights
4. **Document everything** — Nature of breach, effects, remedial actions

### Template for User Notification

> We are writing to inform you of a security incident affecting [site name]. On [date], we discovered unauthorized access to our website. The potentially affected data includes [list specific data types]. We have taken the following steps: [list actions]. We recommend you [change password / monitor accounts]. For questions, contact [email].

## Further Reading

- [Server-Level Hardening](./02-server-hardening.md) — Prevention measures
- [Cloudflare Hardening](./01-cloudflare-hardening.md) — WAF configuration
- [GDPR Implementation](./04-gdpr-implementation.md) — Breach notification requirements
- [Patchstack Security Advisory](https://patchstack.com/) — WordPress vulnerability database
