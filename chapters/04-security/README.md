# Security

## Overview

WordPress powers over 40% of the web, making it a prime target for attacks. The good news: most attacks exploit known vulnerabilities with known solutions. A properly secured WordPress site is remarkably resilient.

## The Security Reality

**Most hacks are automated.** Attackers don't personally target your site. Bots scan millions of sites for known vulnerabilities - outdated plugins, weak passwords, exposed files. They exploit whatever they find.

**Defense in depth works.** No single measure stops all attacks. Layers of security mean that when one layer fails, others still protect you.

**Security is ongoing.** It's not a one-time setup. Updates, monitoring, and good practices must continue indefinitely.

## Attack Vectors

Understanding how sites get compromised helps prioritize defenses:

| Vector | Frequency | Prevention |
|--------|-----------|------------|
| **Outdated plugins/themes** | Very common | Regular updates, minimal plugins |
| **Weak passwords** | Very common | Strong passwords, 2FA |
| **Brute force attacks** | Common | Login limiting, 2FA, hide wp-login |
| **SQL injection** | Moderate | Prepared statements, WAF |
| **XSS (Cross-site scripting)** | Moderate | Output escaping, CSP headers |
| **File upload exploits** | Moderate | Restrict uploads, scan files |
| **Server vulnerabilities** | Less common | Keep server software updated |

## What This Chapter Covers

### [Cloudflare Hardening](./01-cloudflare-hardening.md)

Using Cloudflare as a security layer - WAF rules, bot protection, rate limiting, and DDoS mitigation. Cloudflare's free tier provides significant protection that would otherwise require expensive solutions.

## Security Layers

A properly secured WordPress site has multiple layers:

### Network Level
- **Firewall** - Blocks malicious traffic before it reaches WordPress
- **DDoS protection** - Absorbs volumetric attacks
- **CDN** - Hides origin server, caches content at edge

### Server Level
- **SSH key authentication** - No password-based SSH access
- **Firewall rules** - Only necessary ports open
- **File permissions** - Correct ownership and permissions
- **PHP restrictions** - Disable dangerous functions

### Application Level
- **Updates** - Core, plugins, themes always current
- **Authentication** - Strong passwords, 2FA, limited attempts
- **User roles** - Minimum necessary permissions
- **Input validation** - Sanitize all user input

### Monitoring Level
- **File integrity monitoring** - Detect unauthorized changes
- **Login monitoring** - Alert on suspicious activity
- **Uptime monitoring** - Know immediately when something's wrong

## Essential Security Practices

### Keep Everything Updated

This is the single most important security practice. Most WordPress hacks exploit vulnerabilities that were patched months or years ago. Enable automatic updates for minor releases at minimum.

### Use Strong, Unique Passwords

Every account should have a unique, complex password. Password managers make this practical. Consider requiring 2FA for all admin accounts.

### Minimize Attack Surface

Every plugin is potential vulnerability. Remove unused plugins and themes - don't just deactivate them. Use reputable plugins with active development.

### Principle of Least Privilege

Users should have only the permissions they need. A content editor doesn't need administrator access. Create appropriate roles for different team members.

### Regular Backups

Backups aren't prevention, but they're essential for recovery. Test restores periodically. Keep backups off the WordPress server.

## What NOT to Do

**Don't rely on security through obscurity.** Changing the admin URL or hiding WordPress version provides minimal protection. Attackers don't need these details to exploit vulnerabilities.

**Don't install multiple security plugins.** They conflict, create duplicate rules, and can actually reduce security. Choose one comprehensive solution.

**Don't disable updates "for stability."** Unpatched vulnerabilities are far more destabilizing than updates.

**Don't ignore security warnings.** Browser warnings, plugin notifications, and host alerts exist for reasons.

## Server-Level vs. Plugin-Level Security

Where you implement security matters:

| Approach | Pros | Cons |
|----------|------|------|
| **Server-level (Cloudflare, server firewall)** | Blocks attacks before PHP runs, lower overhead | Requires server access, more complex |
| **Plugin-level (Wordfence, etc.)** | Easy to set up, works on shared hosting | Uses PHP resources, attacks reach server |

For performance-critical sites, implement security as far from WordPress as possible. For simplicity on shared hosting, security plugins are acceptable.

## Security Checklist

Minimum security baseline:

- [ ] WordPress core on latest version
- [ ] All plugins updated and minimal
- [ ] All themes updated, unused removed
- [ ] Strong passwords on all accounts
- [ ] 2FA on administrator accounts
- [ ] Reliable backup system tested
- [ ] SSL/HTTPS properly configured
- [ ] File permissions correct (644 files, 755 directories)
- [ ] wp-config.php secured (400 or 440)
- [ ] Debug mode disabled in production
- [ ] Login attempts limited

## Further Reading

- [Plugin Architecture](../01-wordpress-plugin-architecture/README.md) - Writing secure plugin code
- [Hosting Selection](../05-maintenance/02-hosting-selection.md) - Choosing secure hosting
