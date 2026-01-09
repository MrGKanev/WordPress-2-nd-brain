# Server-Level Security Hardening

Security implemented at the server level stops attacks before they reach PHP, making it far more efficient than plugin-based solutions.

## Why Server-Level Security Matters

When an attack hits your WordPress site, it travels through multiple layers before reaching your content:

```
Attack → Server (Nginx) → PHP → WordPress → Plugin
         ↑                       ↑
      Block here            vs. Block here
      (efficient)              (resource-heavy)
```

**The problem with plugin-based security:** When you use a security plugin like Wordfence, every single request—legitimate or malicious—must travel all the way through Nginx, get processed by PHP-FPM, load the entire WordPress application, and only then does the security plugin check if the request is malicious. This process consumes CPU, memory, and database connections for every attack attempt.

**The advantage of server-level security:** When you block attacks at the Nginx level, malicious requests are rejected immediately. PHP never starts, WordPress never loads, and your server resources remain available for legitimate visitors. A server handling 1000 brute force attempts per minute barely notices them when blocked at Nginx, but would struggle significantly if each request reached WordPress.

**Server-level security also can't be bypassed by WordPress vulnerabilities.** If an attacker finds a zero-day exploit in WordPress core, your server-level protections still work because they operate independently. Plugin-based security depends on WordPress functioning correctly—if WordPress is compromised, the security plugin may be compromised too.

## Hide Version Information

### Why Hide Versions?

When attackers scan your site, one of the first things they look for is version numbers. Every piece of software has known vulnerabilities tied to specific versions. If an attacker sees you're running Nginx 1.18.0, they can immediately look up CVE-2021-23017 (a DNS resolver vulnerability) and check if you're vulnerable.

The same applies to PHP versions, WordPress versions, and plugin versions. Automated scanning tools like WPScan compile databases of vulnerabilities by version, making it trivial to identify attack vectors once versions are known.

**Security through obscurity isn't a complete defense**—a determined attacker can find other ways to identify versions. But hiding version information raises the bar for automated attacks and casual probing, which constitute the vast majority of attack traffic.

### Hide Nginx Version

By default, Nginx includes its version in HTTP response headers and error pages. Every response from your server broadcasts something like `Server: nginx/1.24.0`.

In `/etc/nginx/nginx.conf`, within the `http` block:

```nginx
http {
    server_tokens off;
}
```

This removes version information from:
- The `Server` HTTP header (changes from `nginx/1.24.0` to just `nginx`)
- Default error pages (404, 500, etc.)
- Any auto-generated directory listings

### Hide PHP Version

PHP exposes its version through the `X-Powered-By` header, which by default sends something like `X-Powered-By: PHP/8.2.0`. This tells attackers exactly which PHP vulnerabilities to try.

In `/etc/php/8.x/fpm/php.ini`:

```ini
expose_php = Off
```

This removes the `X-Powered-By` header entirely. There's no legitimate reason for visitors to know your PHP version, and many security scanners specifically look for this header.

After making these changes, reload the services:

```bash
sudo systemctl reload nginx
sudo systemctl reload php8.4-fpm
```

Verify the changes worked by checking your response headers:

```bash
curl -I https://yoursite.com
```

You should no longer see version numbers in the `Server` or `X-Powered-By` headers.

## File Permissions

### Understanding Unix Permissions

File permissions in Linux/Unix control who can read, write, and execute files. They're expressed as three-digit numbers like `644` or `755`, where each digit represents permissions for different user categories:

- **First digit**: Owner (the user who owns the file)
- **Second digit**: Group (users in the file's group)
- **Third digit**: Others (everyone else)

Each digit is the sum of: **4** (read) + **2** (write) + **1** (execute)

So `644` means:
- Owner: 6 = 4+2 = read + write
- Group: 4 = read only
- Others: 4 = read only

### Why Permissions Matter for WordPress

WordPress is a PHP application that runs under your web server's user account (typically `www-data` on Ubuntu/Debian). The web server needs to read PHP files to execute them, but it shouldn't be able to modify most files.

**The security risk:** If an attacker exploits a vulnerability (say, in a plugin), they gain the ability to execute code as the `www-data` user. If `www-data` can write to PHP files, the attacker can modify your site's code. If permissions are correctly set, even a successful exploit is limited in what it can do.

**The balance:** WordPress does need to write to certain directories—uploads for media files, possibly cache directories. But core files, plugin files, and theme files should be read-only in production.

### Standard Permission Setup

```bash
# Set ownership to web server user
# All files should be owned by www-data so the web server can read them
sudo chown -R www-data:www-data /var/www/wordpress

# Files: 644 (owner read/write, everyone else read-only)
# This allows www-data to read PHP files but prevents modification
# except through legitimate channels (FTP, SSH, deployment tools)
sudo find /var/www/wordpress -type f -exec chmod 644 {} \;

# Directories: 755 (owner full access, everyone else read/execute)
# Execute permission on directories means "can list contents and traverse"
# Without execute, you can't cd into a directory or list its files
sudo find /var/www/wordpress -type d -exec chmod 755 {} \;

# wp-config.php: 400 (owner read-only, no one else)
# This file contains database credentials and security keys
# It never needs to be written to during normal operation
# 400 is the most restrictive permission that still works
sudo chmod 400 /var/www/wordpress/wp-config.php
```

**Why 400 for wp-config.php?** This file contains your database password, authentication keys, and security salts. If an attacker can read this file, they have your database credentials. If they can write to it, they can add malicious code that executes on every page load. The `400` permission means only the file owner (www-data) can read it, and even the owner can't write to it without first changing permissions.

### Permission Reference

| Item | Permission | Meaning | Why |
|------|------------|---------|-----|
| Files | 644 | Owner read/write, others read | Web server can read PHP to execute, but can't modify |
| Directories | 755 | Owner all, others read/traverse | Web server can list and enter directories |
| wp-config.php | 400 | Owner read only | Maximum protection for credentials |
| .htaccess | 644 | Owner read/write, others read | Apache needs to read, shouldn't be modified |
| uploads/ | 755 | Owner all, others read/traverse | WordPress writes uploaded files here |

## wp-config.php Hardening

The `wp-config.php` file is WordPress's main configuration file. Beyond database credentials, it can contain constants that significantly improve security by disabling dangerous features.

### Security Constants Explained

```php
// DISALLOW_FILE_EDIT
// By default, WordPress allows administrators to edit plugin and theme files
// directly from the admin dashboard (Appearance > Theme Editor, Plugins > Editor)
// If an attacker gains admin access, they can inject malicious code immediately
// This constant removes those editors entirely
define( 'DISALLOW_FILE_EDIT', true );

// DISALLOW_FILE_MODS
// This is more aggressive than DISALLOW_FILE_EDIT
// It prevents ALL file modifications from WordPress admin, including:
// - Installing new plugins or themes
// - Updating existing plugins or themes
// - Editing any files
// Use this if you deploy via Git/CI and never need to update from admin
// Warning: You'll need to handle all updates via SSH/deployment
define( 'DISALLOW_FILE_MODS', true );

// FORCE_SSL_ADMIN
// Forces all admin pages and login to use HTTPS
// Even if someone accesses http://yoursite.com/wp-admin, they're redirected to HTTPS
// This prevents session hijacking on unsecured networks
// Should always be true if you have SSL (which you should)
define( 'FORCE_SSL_ADMIN', true );

// WP_POST_REVISIONS
// WordPress saves a revision every time you save a post
// On active sites, this can bloat the database significantly
// Security relevance: a bloated database is slower to backup and restore
// 5 revisions is usually enough to recover from mistakes
define( 'WP_POST_REVISIONS', 5 );

// Debug settings for production
// WP_DEBUG enables detailed error messages - useful for development,
// dangerous for production because errors may reveal file paths, database info
// WP_DEBUG_DISPLAY shows errors on screen - never in production
// WP_DEBUG_LOG writes errors to wp-content/debug.log - only if needed for troubleshooting
define( 'WP_DEBUG', false );
define( 'WP_DEBUG_LOG', false );
define( 'WP_DEBUG_DISPLAY', false );

// CONCATENATE_SCRIPTS
// WordPress combines multiple JS/CSS files into single requests in admin
// This can interfere with some security setups and debugging
// Setting to false loads scripts individually (slightly more requests, but cleaner)
define( 'CONCATENATE_SCRIPTS', false );
```

### Optional: Custom Content Directory

By default, everyone knows WordPress plugins live in `/wp-content/plugins/`. Attackers use this knowledge to probe for vulnerable plugins. You can change this:

```php
// Move wp-content to a custom location
// Attackers scanning for /wp-content/plugins/vulnerable-plugin/ won't find it
// Note: This must be set before WordPress is installed, or requires careful migration
define( 'WP_CONTENT_DIR', dirname(__FILE__) . '/content' );
define( 'WP_CONTENT_URL', 'https://example.com/content' );
```

**This is optional and adds complexity.** Some plugins assume the default structure and may break. Only implement if you're comfortable troubleshooting plugin issues.

## Nginx Security Rules

### Block Direct IP Access

Every server has an IP address (like `123.45.67.89`). If someone accesses your server directly via IP instead of your domain name, they might:
- Find hidden sites hosted on the same server
- Probe for vulnerabilities without triggering domain-based security rules
- Send spam from your IP while hiding behind the lack of domain association

This rule catches any request that doesn't match a configured domain and closes the connection without response:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;  # Underscore catches all unmatched server_name requests

    location / {
        return 444;  # Nginx-specific: close connection without sending any response
    }
}
```

**Why 444 instead of 403?** The `403 Forbidden` response tells attackers "yes, there's something here, but you can't access it." The `444` code is Nginx-specific—it immediately closes the connection without sending any response at all. The attacker's tool sees a connection timeout, giving them no information about what's running on the server.

### Block XML-RPC

XML-RPC (`/xmlrpc.php`) is a legacy API from before WordPress had the REST API. It allows remote publishing, pingbacks, and trackbacks. It's also one of the most attacked endpoints because:

1. **Brute force amplification**: A single XML-RPC request can test hundreds of password combinations using the `system.multicall` method
2. **Pingback DDoS**: Attackers use pingback requests to launch denial-of-service attacks against other sites, using your server as an amplifier
3. **Always enabled**: Unlike modern APIs, XML-RPC has no built-in rate limiting or authentication requirements

**When you might need XML-RPC:**
- Jetpack plugin (though newer versions use REST API)
- WordPress mobile app (older versions)
- Some IFTTT integrations
- Legacy content publishing tools

If you're not using any of these, block it entirely:

```nginx
location = /xmlrpc.php {
    deny all;
    access_log off;    # Don't fill logs with blocked attempts
    log_not_found off; # Don't log "file not found" errors
}
```

### Protect Sensitive Files

WordPress includes several files that reveal information or should never be accessed directly:

```nginx
# Block WordPress sensitive files
location ~* /(wp-config\.php|readme\.html|license\.txt|wp-settings\.php) {
    deny all;
    return 403;
}
```

**What each file reveals:**
- `wp-config.php`: Database credentials, secret keys, debug settings—should never be accessible
- `readme.html`: WordPress version number in plain text
- `license.txt`: Confirms WordPress installation, includes version
- `wp-settings.php`: Core WordPress file that should only be included by PHP, never accessed directly

```nginx
# Block plugin/theme readme files (reveal versions)
location ~* /(readme|changelog|license)\.(txt|md)$ {
    deny all;
    return 403;
}
```

Plugins often include readme files with exact version numbers. An attacker finding `/wp-content/plugins/contact-form-7/readme.txt` learns exactly which version you have and can check for known vulnerabilities.

```nginx
# Block configuration and log files
location ~* \.(ini|log|conf|env|sql|bak)$ {
    deny all;
}
```

Files with these extensions should never be web-accessible:
- `.ini`: PHP configuration files
- `.log`: Error logs may contain sensitive information
- `.conf`: Configuration files
- `.env`: Environment files often contain API keys and secrets
- `.sql`: Database dumps
- `.bak`: Backup files, possibly containing sensitive data

```nginx
# Block hidden files (except .well-known for SSL verification)
location ~ /\.(?!well-known) {
    deny all;
}
```

Hidden files (starting with `.`) include `.htaccess`, `.git` directories, `.env` files. The exception for `.well-known` allows Let's Encrypt SSL verification to work.

### Prevent PHP Execution in Uploads

This is one of the most critical rules. Here's the attack scenario:

1. Attacker finds a vulnerability in a file upload feature (maybe a form plugin)
2. They upload a file called `innocent-image.php` containing malicious code
3. They access `https://yoursite.com/wp-content/uploads/2024/01/innocent-image.php`
4. The malicious PHP code executes, giving them control of your server

By blocking PHP execution in the uploads directory, even if an attacker successfully uploads a PHP file, it won't execute—Nginx returns a 403 instead:

```nginx
location ~* /wp-content/uploads/.*\.php$ {
    deny all;
    return 403;
}
```

For even more protection, block PHP execution in the entire wp-content directory:

```nginx
# More aggressive: block all PHP in content directories
location ~* /wp-content/.*\.php$ {
    deny all;
    return 403;
}
```

**Why this works:** Legitimate PHP execution happens in the WordPress root and `/wp-admin/`. Plugins and themes should have their PHP files loaded by WordPress's include system, not accessed directly via URL. Any direct URL request to a PHP file in `/wp-content/` is suspicious.

### Block Security Scanners

Automated scanning tools like WPScan, Nikto, and Nmap identify themselves in their User-Agent string. While sophisticated attackers can change this, blocking known scanner signatures stops automated attacks and script kiddies:

```nginx
# Block known scanner user agents
if ($http_user_agent ~* "wpscan|nikto|fimap|sqlmap|acunetix|nmap|dirbuster|nessus|whatweb") {
    return 403;
}
```

**What these tools do:**
- `wpscan`: WordPress-specific vulnerability scanner
- `nikto`: Web server scanner looking for dangerous files
- `sqlmap`: Automated SQL injection tool
- `acunetix`: Commercial vulnerability scanner (often used illegally)
- `nmap`: Network scanner, often used for reconnaissance
- `dirbuster`: Brute-forces directory names to find hidden files
- `nessus`: Vulnerability scanner

```nginx
# Block empty user agents (common in bots)
if ($http_user_agent = "") {
    return 403;
}
```

Legitimate browsers always send a User-Agent. Empty User-Agent typically indicates automated tools or misconfigured bots.

### Block User Enumeration

WordPress has several ways attackers can discover valid usernames, which they then use for brute-force password attacks:

**Method 1: Author archives**
Visiting `/?author=1` redirects to `/author/admin/`, revealing that user ID 1's username is "admin".

```nginx
if ($args ~* "^author=([0-9]+)") {
    return 404;
}
```

**Method 2: Author sitemaps**
If you use an SEO plugin, `/author-sitemap.xml` might list all author usernames.

```nginx
location ~ ^/author-sitemap\.xml$ {
    return 404;
}
```

**Method 3: REST API users endpoint**
The endpoint `/wp-json/wp/v2/users` returns JSON with usernames of all users who have published posts.

```nginx
location ~ ^/wp-json/wp/v2/users {
    return 403;
}
```

**Why enumerate usernames?** Once an attacker knows valid usernames, they only need to guess passwords. If they don't know usernames, they're essentially guessing two things at once, making brute force attacks much less efficient.

### Security Headers

HTTP security headers instruct browsers on how to handle your content, preventing various attacks:

```nginx
# X-Frame-Options: Prevents your site from being embedded in iframes
# This stops "clickjacking" attacks where attackers overlay invisible iframes
# "SAMEORIGIN" allows your own site to use iframes but blocks others
add_header X-Frame-Options "SAMEORIGIN" always;

# X-Content-Type-Options: Prevents MIME type sniffing
# Without this, browsers might execute a file as JavaScript even if it's
# served as text/plain, enabling certain XSS attacks
add_header X-Content-Type-Options "nosniff" always;

# X-XSS-Protection: Legacy XSS filter (mostly for older browsers)
# Modern browsers have built-in XSS protection, but this doesn't hurt
add_header X-XSS-Protection "1; mode=block" always;

# Referrer-Policy: Controls what information is sent in the Referer header
# "strict-origin-when-cross-origin" means:
# - Full URL sent for same-origin requests
# - Only origin (domain) sent for cross-origin HTTPS requests
# - Nothing sent when going from HTTPS to HTTP
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## Firewall Configuration

A firewall controls which network traffic can reach your server. Even if services are running, if the firewall blocks their port, they're inaccessible from the internet.

### Understanding Ports

Network services listen on numbered ports:
- **Port 22**: SSH (remote server access)
- **Port 80**: HTTP (unencrypted web traffic)
- **Port 443**: HTTPS (encrypted web traffic)
- **Port 3306**: MySQL (database)

If MySQL is running but port 3306 is firewalled, attackers can't connect to your database from the internet—only local connections work.

### UFW (Uncomplicated Firewall)

UFW is Ubuntu/Debian's default firewall management tool. It's a frontend for the more complex `iptables`:

```bash
# Reset removes all existing rules (careful on production!)
sudo ufw reset

# Default policies:
# Deny incoming = block all inbound traffic unless explicitly allowed
# Allow outgoing = let the server make outbound connections (updates, APIs)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH - without this, you'll be locked out of your server!
# If you've moved SSH to a non-standard port (recommended), use that port
sudo ufw allow 22/tcp

# Allow HTTPS - this is what web visitors need
sudo ufw allow 443/tcp

# Enable the firewall - after this, rules are enforced
sudo ufw enable

# Check what's allowed
sudo ufw status verbose
```

### Why Not Allow Port 80?

Traditional setups open both port 80 (HTTP) and 443 (HTTPS), with server-side redirects from HTTP to HTTPS. But if you're using Cloudflare:

1. Visitors connect to Cloudflare, not your server directly
2. Cloudflare handles HTTP→HTTPS redirects
3. Cloudflare connects to your server over HTTPS only

With this setup, your server never needs to accept HTTP connections. Not opening port 80:
- Reduces attack surface (one less open port)
- Prevents SSL stripping attacks (where attackers intercept the HTTP→HTTPS redirect)
- Simplifies configuration

If you're not using Cloudflare, you do need port 80 for Let's Encrypt verification and HTTP→HTTPS redirects.

## PHP Security Settings

PHP itself has security-relevant configuration options. These go in `/etc/php/8.x/fpm/php.ini`:

### Disable Dangerous Functions

```ini
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source
```

**What these functions do and why they're dangerous:**

- `exec`, `system`, `shell_exec`, `passthru`: Execute system commands. If an attacker can call these, they can run any command on your server.
- `proc_open`, `popen`: Open processes for reading/writing. Used for complex command execution.
- `curl_exec`, `curl_multi_exec`: Make HTTP requests. Can be used for server-side request forgery (SSRF).
- `parse_ini_file`: Read INI files. Could expose configuration.
- `show_source`: Display PHP source code.

**Warning:** Some plugins legitimately need these functions:
- Image optimization plugins often use `exec` to run tools like ImageMagick
- Backup plugins may use `exec` for mysqldump
- Some caching plugins use process functions

Test thoroughly before applying in production. If something breaks, you can remove specific functions from the list.

### Session Security

```ini
; session.cookie_httponly: JavaScript can't access session cookies
; This prevents XSS attacks from stealing sessions
session.cookie_httponly = 1

; session.cookie_secure: Session cookies only sent over HTTPS
; Prevents session hijacking on unsecured networks
session.cookie_secure = 1

; session.use_strict_mode: Only use session IDs created by the server
; Prevents session fixation attacks where attackers set a known session ID
session.use_strict_mode = 1
```

## Recommended Security Plugins

Instead of heavy "all-in-one" security suites, use lightweight plugins that do specific things well:

| Plugin | What It Does | Why Use It |
|--------|--------------|------------|
| **Two-Factor** | Adds 2FA to WordPress login | Even if password is compromised, attacker needs second factor. Supports TOTP apps, email codes, backup codes, hardware keys. |
| **WPS Hide Login** | Changes `/wp-login.php` to custom URL | Automated scanners target `/wp-login.php`. Custom URL stops casual attacks. Use only with 2FA—obscurity alone isn't security. |
| **Admin and Site Enhancements (ASE)** | Collection of small tweaks | Hide WordPress version, disable author archives, limit login attempts. Many small features in one lightweight plugin. |
| **UpdraftPlus** | Automated backups | Not security, but essential for recovery. Backs up to cloud storage (S3, Google Drive, Dropbox). |

### Why Avoid Heavy Security Plugins Like Wordfence?

**Performance overhead**: Wordfence scans every request through PHP, checking against threat databases, analyzing patterns, logging activity. On a busy site, this adds measurable latency to every page load.

**False sense of security**: Wordfence and similar plugins operate at the WordPress layer. They can't protect against:
- Server vulnerabilities
- Attacks that crash PHP before WordPress loads
- Direct database access
- SSH/FTP compromises

They provide real protection, but users often think they're fully protected when they're not.

**Duplicate features**: If you implement server-level blocking (as described in this guide) and use Cloudflare, you're already doing what these plugins do—but more efficiently. Having both means:
- Double the processing per request
- Potential conflicts (one blocks something the other expects)
- Confusion about which layer caught an attack

**When to use them**: If you're on shared hosting with no server access, security plugins are your only option and better than nothing. On a VPS where you control the server, implement security at the server level instead.

## Monitoring

Security isn't set-and-forget. You need to know when attacks happen and catch compromises early.

### Log Monitoring

Your Nginx access log records every request. Watching it reveals attack patterns:

```bash
# Watch for login attempts in real-time
# This shows every request to wp-login.php or xmlrpc.php
tail -f /var/log/nginx/access.log | grep -E "(wp-login|xmlrpc)"

# Count login POST requests (actual login attempts, not page views)
grep "POST /wp-login.php" /var/log/nginx/access.log | wc -l

# Find which IPs are hitting xmlrpc.php most
# Useful for identifying attack sources to block
grep "xmlrpc.php" /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -20
```

**What to look for:**
- Sudden spikes in login attempts
- Requests to non-existent files (directory probing)
- Requests with suspicious user agents
- Repeated 403/404 errors from single IPs

### Recommended Monitoring Tools

| Tool | Purpose | How It Helps |
|------|---------|--------------|
| **Fail2ban** | Automatic IP blocking | Watches logs for failed logins, automatically blocks IPs that fail too many times. Essential for stopping brute force. |
| **BetterStack (formerly Logtail)** | Log aggregation and alerting | Collects logs from multiple sources, lets you search/filter, sends alerts for patterns you define. |
| **Pulsetic** | Uptime monitoring | Checks your site from multiple locations, alerts you immediately if it goes down. |
| **Netdata** | Real-time server metrics | Shows CPU, memory, disk, network in real-time. Helps identify attacks that consume resources. |

## Backup Strategy: 3-2-1 Rule

If despite all precautions your site is compromised, backups are your recovery path. The 3-2-1 rule ensures backups survive whatever destroyed your primary site:

- **3** copies of your data (primary + 2 backups)
- **2** different storage types (server disk + cloud storage, for example)
- **1** offsite location (survives if your datacenter burns down)

### Implementation

**Layer 1: WordPress-level backups**
Use UpdraftPlus to automatically backup to cloud storage:
- Database backup daily
- Files backup weekly (they change less often)
- Store in S3, Google Drive, or Dropbox
- Keep 30 days of backups

**Layer 2: Server-level snapshots**
Most hosting providers offer server snapshots:
- DigitalOcean, Vultr, Linode all have this
- Daily snapshots retained for 7 days
- Captures everything, including server configuration

**Layer 3: Offsite copy**
Periodically download a backup to local storage or separate cloud:
- Monthly full backup download
- Store separately from main cloud provider
- Test restore process

**Testing is critical.** A backup you can't restore is worthless. Quarterly:
1. Download a backup
2. Set up a test server
3. Restore the backup
4. Verify the site works

## Security Audit Checklist

Regular audits catch problems before attackers do. Schedule these reviews:

### Weekly (15 minutes)
- [ ] Check for WordPress, plugin, theme updates in dashboard
- [ ] Review user list for unexpected accounts
- [ ] Glance at error logs for unusual patterns
- [ ] Check Cloudflare security events dashboard

### Monthly (1 hour)
- [ ] Review all user accounts—remove anyone who no longer needs access
- [ ] Check `/wp-content/mu-plugins/` for unknown files (malware hides here)
- [ ] Verify backup is running: check cloud storage for recent files
- [ ] Test restore: download latest backup, verify it's valid
- [ ] Review which plugins have been updated, check changelogs for security fixes

### Quarterly (2-3 hours)
- [ ] Audit all installed plugins: Is each one still needed? Still maintained?
- [ ] Full restore test: spin up test server, restore backup, verify everything works
- [ ] Review server access logs for patterns: unusual IPs, strange URLs, repeated failures
- [ ] Update server packages: `apt update && apt upgrade`
- [ ] Review firewall rules: still appropriate for your current setup?
- [ ] Check SSL certificate expiration
- [ ] Verify monitoring is working: trigger a test alert

## Further Reading

- [Cloudflare Hardening](./01-cloudflare-hardening.md) - Network-level protection with WAF rules and DDoS mitigation
- [wp-config.php Optimization](../03-wordpress-optimization/01-wp-config-optimization.md) - Performance settings that also affect security
- [Hosting Selection](../05-maintenance/02-hosting-selection.md) - Choosing hosts with good security practices
- [Tai Hoang's WordPress Security Guide](https://taihoang.com/articles/wordpress-security-in-good-hands/) - Comprehensive handbook on layered WordPress security that informed this guide
