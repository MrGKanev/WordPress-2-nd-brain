# Security

WordPress runs 43% of the web. That makes it the biggest target on the internet. But here's the thing: most WordPress hacks are boring. They exploit plugins that haven't been updated in months, passwords that are "admin123", or servers that expose their PHP version to the world. Automated bots scan millions of sites and exploit whatever they find—nobody's personally targeting your site.

The flip side: the solutions are equally boring. Keep everything updated, use strong passwords with 2FA, minimize your plugin surface area, and put a proper firewall in front. Defense in depth—multiple layers, each catching what the previous one missed.

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

### [Server-Level Hardening](./02-server-hardening.md)

Nginx security configurations, file permissions, PHP restrictions, and wp-config.php hardening. Server-level security stops attacks before they reach WordPress, making it far more efficient than plugin-based solutions.

### [Input Sanitization & Output Escaping](./03-data-validation.md)

The most critical security knowledge for writing custom code. Sanitization functions, escaping for different contexts, prepared statements with `$wpdb`, and real-world examples of secure form handling.

### [GDPR Implementation](./04-gdpr-implementation.md)

Practical GDPR compliance for WordPress sites. WordPress's built-in privacy tools, data export and erasure hooks, cookie consent strategies, WooCommerce-specific requirements, data retention policies, and a compliance checklist.

### [Incident Response](./05-incident-response.md)

What to do when your site is compromised. Signs of compromise, immediate containment steps, investigation techniques, cleanup procedures (clean restore vs. manual), post-incident hardening, and communication templates.

### [Content Security Policy (CSP)](./06-csp-headers.md)

Preventing XSS with proper CSP headers. Directives, source values, the WordPress CSP challenge, nonce-based implementation, phased rollout from report-only to enforced, and related security headers.

### [OWASP Threat Modeling](./07-owasp-threat-modeling.md)

Map common web-application risks to WordPress features and model abuse paths before implementation.

### [Secrets Management](./08-secrets-management.md)

Environment-based secret storage, key rotation and exposure response for WordPress and integrations.

### [Transactional Email Authentication](./09-email-authentication.md)

SPF, DKIM, DMARC, sender alignment and safe WordPress mail validation.

### [CORS & API Security](./10-cors-api-security.md)

Origin allowlists, credentialed requests, preflight and REST permission boundaries.

### [Identity & Access Management](../10-platform-architecture-governance/05-identity-access-management.md)

Roles, individual accounts, MFA, access reviews and offboarding across WordPress, hosting and vendor systems.

### [Privacy & Data Governance](../10-platform-architecture-governance/06-privacy-data-governance.md)

Data mapping, consent, retention and operational readiness for privacy requests or data exposure.

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

## Key Statistics

According to [Patchstack's 2024 report](https://patchstack.com/):

- **96% of vulnerabilities** were found in plugins
- **4% of vulnerabilities** were found in themes
- Only **7 vulnerabilities** were found in WordPress core itself
- **43%** of vulnerabilities don't require authentication to exploit
- **33%** of vulnerabilities were not patched before public disclosure

This reinforces why minimizing plugins and keeping everything updated is critical.

## User Access & Content Protection Plugins

Beyond WAFs and server hardening, managing who accesses your site and what they can do requires targeted tools.

### Spam & Malicious User Management

Open registration sites (forums, membership, WooCommerce stores) attract bot accounts. These fake users pollute your database, attempt credential stuffing, and sometimes inject spam content.

| Plugin | Purpose | Best For |
|--------|---------|----------|
| **CleanTalk** | Anti-spam service | Form submissions, registrations, comments (cloud-based) |
| **Akismet** | Comment spam | Built into WordPress, effective for comment-heavy sites |
| **WPBruiser** | Bot protection | No-CAPTCHA anti-spam, uses algorithmic detection |
| **Stop Spammers** | Multi-layered blocking | Combines multiple spam detection methods |
| [Spam User Detective](https://openwpclub.com/plugins/spam-user-detective-wp/) | Bulk user cleanup | Identify and remove existing suspicious accounts |

**Spam user red flags:**
- Accounts created in bulk within seconds
- Usernames matching patterns (random strings, email-like names)
- Accounts with no activity after registration
- Registration from known spam IP ranges

### File & Content Protection

| Plugin | Purpose | Best For |
|--------|---------|----------|
| **Members** by MemberPress | Role management | Fine-grained capability control per role |
| **Restrict Content** | Content gating | Restrict posts/pages to specific roles |
| **Download Monitor** | File downloads | Track and control file downloads |
| **Prevent Direct Access** | Media protection | Protect uploaded files from direct URL access |

### Staging Data Sanitization

When preparing staging environments from production data, you need to anonymize customer information while keeping realistic data structures. Options:

- **WP-CLI `search-replace`** — built-in, handles URL changes and basic data swapping
- **WP Migrate** — handles database migrations with find-and-replace
- **Fakerpress** — generates fake content for testing
- [WP Sanitize](https://openwpclub.com/plugins/wp-sanitize/) — sanitizes real data while protecting sensitive information

## Topics to Explore

Gaps in current coverage worth adding:

### Foundational
- [ ] **Life cycle of a hack** - How attacks progress from reconnaissance to exploitation to persistence
- [x] **OWASP Top 10** - [Covered](./07-owasp-threat-modeling.md)
- [ ] **OWASP ASVS** - Application Security Verification Standard as a security requirements checklist
- [ ] **Risk management** - Prioritizing security efforts based on threat likelihood and impact

### User Security
- [ ] **User roles deep dive** - Capabilities system, creating custom roles, role auditing
- [ ] **Single Sign-On (SSO)** - SAML, OAuth integration options for WordPress
- [ ] **User activity monitoring** - Tracking admin actions, login history, audit trails
- [ ] **Spam user management** - Detecting and removing fake/bot accounts

### Update Management
- [ ] **Software Bill of Materials (SBOM)** - Tracking dependencies and their versions
- [ ] **Auto-updates: pros and cons** - When to enable, testing strategies, rollback plans
- [ ] **Patching vs updating** - Emergency patches, version pinning, security-only updates

### Browser Security
- [x] **Content Security Policy (CSP)** - [Covered](./06-csp-headers.md)
- [x] **CORS configuration** - [Covered](./10-cors-api-security.md)

### Configuration
- [x] **SMTP email hardening** - [Covered](./09-email-authentication.md)
- [x] **Managing secrets** - [Covered](./08-secrets-management.md)
- [ ] **Database hardening** - User privileges, connection security, encryption at rest

### Compliance
- [x] **GDPR for WordPress** - [Covered](./04-gdpr-implementation.md)
- [ ] **PCI-DSS basics** - Requirements for sites handling payment data
- [ ] **EU Cyber Resilience Act** - Upcoming requirements for software providers

### Practical Guides
- [ ] **Security from scratch** - Step-by-step guide for new WordPress installations
- [x] **Incident response** - [Covered](./05-incident-response.md)

## Further Reading

- [Plugin Architecture](../08-plugin-development/README.md) - Writing secure plugin code
- [Hosting Selection](../02-maintenance/02-hosting-selection.md) - Choosing secure hosting
- [Tai Hoang's WordPress Security Guide](https://taihoang.com/articles/wordpress-security-in-good-hands/) - Comprehensive handbook on layered WordPress security
