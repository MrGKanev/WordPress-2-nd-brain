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

## When Things Go Wrong

Despite best practices, problems happen. Be prepared:

1. **Have a rollback plan** - Know how to restore from backup
2. **Keep staging available** - Test fixes before applying to production
3. **Document the fix** - Record what went wrong and how you fixed it
4. **Learn from incidents** - Update processes to prevent recurrence

## Further Reading

- [WordPress Optimization](../03-wordpress-optimization/README.md) - Performance tuning
- [Security](../04-security/README.md) - Protecting your site
