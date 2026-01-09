# Maintenance

## Overview

Building a WordPress site is the beginning, not the end. Long-term success requires ongoing maintenance - updates, monitoring, backups, and informed decisions about hosting and plugins. This chapter covers the operational side of WordPress.

## The Maintenance Mindset

**Prevention beats recovery.** Regular maintenance prevents most emergencies. An hour of updates per month beats a weekend of disaster recovery.

**Document everything.** Future you (or the next developer) will thank present you. Keep records of customizations, plugin choices, and server configurations.

**Automate what you can.** Automated backups, update notifications, and uptime monitoring reduce manual overhead and catch problems early.

## What This Chapter Covers

### [Plugin Recommendations](./01-plugin-recommendations.md)

Curated plugin selections by category, based on performance testing and real-world use. Not every popular plugin is a good plugin. Covers:

- Performance optimization plugins
- SEO solutions
- Security approaches
- Plugins to avoid

### [Hosting Selection](./02-hosting-selection.md)

Choosing and optimizing hosting for WordPress. Hosting is the foundation everything else builds on. Covers:

- Evaluation criteria
- Server stack recommendations
- VPS optimization
- When to upgrade

### [WP-CLI Essentials](./03-wp-cli-essentials.md)

Command-line WordPress management. Tasks that take minutes in the admin take seconds via terminal. Covers:

- Core, plugin, and theme management
- Database operations and search-replace
- User management and security audits
- Maintenance automation scripts

### [Multisite Considerations](./04-multisite-basics.md)

Running multiple sites from one WordPress installation. Different rules apply for plugins, data storage, and administration. Covers:

- Network vs. site activation
- Database structure and table prefixes
- Super Admin vs. Site Admin
- Plugin compatibility requirements

## Core Maintenance Tasks

### Updates

The most important maintenance task. Update regularly:

| Component | Frequency | Approach |
|-----------|-----------|----------|
| WordPress core (minor) | Immediately | Enable auto-updates |
| WordPress core (major) | Within 1-2 weeks | Test on staging first |
| Plugins | Weekly | Review changelog, test |
| Themes | Weekly | Test after updating |
| PHP version | When available | Test thoroughly first |

### Backups

Backups are worthless if they don't work. Your backup strategy should include:

- **Automatic scheduling** - Daily minimum, hourly for active sites
- **Off-site storage** - Not on the same server as WordPress
- **Database + files** - Both are necessary for full restore
- **Tested restores** - Periodically verify backups actually work

### Database Maintenance

WordPress databases accumulate bloat:

- Post revisions (can grow indefinitely)
- Expired transients
- Orphaned metadata
- Spam comments
- Trashed posts

Regular cleanup keeps the database lean. Most optimization plugins handle this, or use WP-CLI for manual control.

### Monitoring

Know when something's wrong before users tell you:

- **Uptime monitoring** - Get alerts when site goes down
- **Performance monitoring** - Track load times over time
- **Error logging** - Review PHP errors periodically
- **Security scanning** - Check for malware and vulnerabilities

## The Plugin Dilemma

Every plugin is a tradeoff:

**Benefits:**
- Adds functionality quickly
- Maintained by specialists
- Community-tested

**Costs:**
- Performance overhead
- Security attack surface
- Update maintenance
- Potential conflicts
- Dependency on developer

The goal isn't zero plugins - it's the right plugins. Choose plugins that are:

- Actively maintained (check last update date)
- Well-reviewed (but read the reviews, not just stars)
- Focused (does one thing well vs. bloated "all-in-one")
- Reputable (established developers, security track record)

## Hosting Realities

Hosting tiers exist for reasons:

| Tier | Best For | Typical Cost |
|------|----------|--------------|
| Shared | Low-traffic blogs, testing | $3-15/month |
| Managed WordPress | Business sites, hands-off | $25-100/month |
| VPS | High traffic, custom needs | $20-100/month |
| Dedicated | Very high traffic, compliance | $100+/month |

Cheap hosting isn't always false economy - a simple blog doesn't need a dedicated server. But undersized hosting for a business site costs more in lost sales than the hosting savings.

## Maintenance Schedule

A practical maintenance routine:

**Weekly:**
- Review and apply updates
- Check uptime/error logs
- Verify recent backups exist

**Monthly:**
- Database optimization
- Security scan
- Performance check
- Review analytics for issues

**Quarterly:**
- Audit installed plugins (remove unused)
- Review user accounts (remove old)
- Test backup restoration
- Check hosting resource usage

**Annually:**
- Review hosting needs
- Evaluate plugin alternatives
- Update PHP version if available
- Review and update documentation

## Maintenance Checklists

Detailed checklists for each maintenance cycle. Print these or adapt them to your workflow.

### Weekly Checklist

- [ ] **Apply pending updates** - Check for WordPress core, plugin, and theme updates
- [ ] **Review error logs** - Check PHP error logs and server logs for issues
- [ ] **Verify backup ran** - Confirm automated backups completed successfully
- [ ] **Check uptime reports** - Review any downtime incidents from monitoring
- [ ] **Moderate comments** - Delete spam, approve legitimate comments
- [ ] **Test critical forms** - Submit test entries through contact/order forms
- [ ] **Check Search Console** - Review any new crawl errors or security issues

### Monthly Checklist

- [ ] **Run database optimization** - Clean revisions, transients, spam, and orphaned data
- [ ] **Check broken links** - Scan for 404s and fix or redirect dead links
- [ ] **Security scan** - Run malware and vulnerability checks
- [ ] **Performance test** - Check page speed, compare to previous month
- [ ] **Review analytics** - Look for unusual traffic patterns or errors
- [ ] **Verify analytics tracking** - Confirm tracking code still works after updates
- [ ] **Clean media library** - Remove unused uploads taking up space
- [ ] **Review user sessions** - Log out stale sessions, check for suspicious activity

### Quarterly Checklist

- [ ] **Audit installed plugins** - Remove unused plugins completely (not just deactivated)
- [ ] **Audit installed themes** - Keep only active theme and one default theme
- [ ] **Review user accounts** - Remove inactive accounts, verify admin access list
- [ ] **Test backup restoration** - Actually restore a backup to staging to verify it works
- [ ] **Check hosting resources** - Review disk space, bandwidth, CPU usage trends
- [ ] **Update staging environment** - Sync staging with production for accurate testing
- [ ] **Review redirect rules** - Clean up temporary redirects, verify permanent ones work
- [ ] **Check SSL certificate** - Verify certificate expiry date, ensure auto-renewal is configured

### Annual Checklist

- [ ] **Review hosting provider** - Evaluate if current hosting still meets needs
- [ ] **Evaluate plugin alternatives** - Check if better options exist for key plugins
- [ ] **Update PHP version** - Upgrade to latest supported version (test thoroughly first)
- [ ] **Update MySQL/MariaDB** - Upgrade database if newer version available
- [ ] **Review security practices** - Audit login URL, admin usernames, 2FA adoption
- [ ] **Documentation review** - Update internal docs, login credentials, emergency contacts
- [ ] **Performance baseline** - Establish new benchmarks for the year
- [ ] **Review caching strategy** - Verify cache rules are still optimal

### One-Time Setup Tasks

These should be done once and verified periodically:

- [ ] **SSL certificate installed** - Site loads over HTTPS only
- [ ] **Automated backups configured** - Daily minimum, hourly for eCommerce
- [ ] **Off-site backup storage** - Backups stored separately from web server
- [ ] **Uptime monitoring active** - External service watching for downtime
- [ ] **Security plugin installed** - Firewall, login protection, file monitoring
- [ ] **Custom login URL** - Changed from default `/wp-admin` path
- [ ] **Admin username changed** - No accounts using "admin" username
- [ ] **Two-factor authentication** - Enabled for all admin accounts
- [ ] **Child theme in use** - Customizations won't be lost on theme updates
- [ ] **Google Search Console connected** - Site verified and monitored
- [ ] **Sitemap submitted** - XML sitemap registered with search engines
- [ ] **Staging environment ready** - Clone site available for testing updates
- [ ] **Email delivery configured** - Using SMTP plugin, transactional emails work

### Post-Update Checklist

Run through this after any significant update:

- [ ] **Site loads correctly** - Check homepage, key pages
- [ ] **Forms work** - Test contact forms, checkout if applicable
- [ ] **Admin area accessible** - Can log in and access all areas
- [ ] **No PHP errors** - Check error log for new warnings/errors
- [ ] **Analytics still tracking** - Verify tag didn't get removed
- [ ] **Critical functionality works** - Test site-specific features
- [ ] **Mobile layout intact** - Check responsive design

## When Things Go Wrong

Despite best practices, problems happen. Be prepared:

1. **Have a rollback plan** - Know how to restore from backup
2. **Keep staging available** - Test fixes before applying to production
3. **Document the fix** - Record what went wrong and how you fixed it
4. **Learn from incidents** - Update processes to prevent recurrence

## Further Reading

- [WordPress Optimization](../04-performance/README.md) - Performance tuning
- [Security](../03-security/README.md) - Protecting your site
