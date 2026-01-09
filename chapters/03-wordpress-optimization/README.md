# WordPress Optimization

## Overview

A fast WordPress site isn't a luxury - it's a requirement. Speed affects user experience, search rankings, conversion rates, and server costs. This chapter covers optimization from the server level up to the browser, with practical techniques you can apply immediately.

## The Optimization Mindset

Before diving into techniques, understand these principles:

**Measure first.** Don't optimize blindly. Use tools like Query Monitor, New Relic, or browser DevTools to identify actual bottlenecks. The slowest part of your site might not be what you expect.

**Server before code.** The best-optimized WordPress code can't overcome a slow server. Proper hosting, PHP configuration, and caching infrastructure make more difference than any plugin.

**Diminishing returns are real.** Going from 5 seconds to 2 seconds is life-changing. Going from 200ms to 150ms probably isn't worth the complexity. Know when to stop.

**Don't break functionality.** Aggressive optimization can break features. Test thoroughly, especially with caching and JavaScript deferral.

## What This Chapter Covers

### Server-Level Optimization

**[wp-config.php Optimization](./01-wp-config-optimization.md)**

WordPress configuration constants that affect performance, debugging, and resource usage. Small changes here can have site-wide impact.

**[PHP Optimization](./02-php-optimization.md)**

PHP version selection, OPcache configuration, and memory settings. Often the biggest single performance improvement comes from proper PHP configuration.

**[PHP-FPM Optimization](./03-php-fpm-optimization.md)**

Process manager tuning for different server sizes. Critical for VPS and dedicated servers where you control the stack.

### WordPress-Level Optimization

**[Cron Management](./04-cron-management.md)**

WordPress's pseudo-cron system and its impact on performance. How to move to system cron and manage scheduled tasks efficiently.

**[Development Workflow](./05-development-workflow.md)**

Balancing development best practices with practical deployment needs. When to use staging, when direct production changes are acceptable.

**[Image Optimization](./06-image-optimizations.md)**

Images are typically the largest files on any page. Formats, compression, lazy loading, and responsive images.

**[Database Optimization](./07-database-optimizations.md)**

Query optimization, table maintenance, and dealing with bloat from revisions, transients, and plugin data.

### User Experience Optimization

**[Core Web Vitals](./08-core-web-vitals-optimizations.md)**

Google's performance metrics that affect search rankings. LCP, INP, CLS - what they measure and how to improve them.

## The Optimization Stack

Performance improvements compound. A well-optimized stack looks like:

```
┌─────────────────────────────────────┐
│  Browser: Caching, compression      │
├─────────────────────────────────────┤
│  CDN: Edge caching, asset delivery  │
├─────────────────────────────────────┤
│  Page Cache: Full HTML caching      │
├─────────────────────────────────────┤
│  Object Cache: Redis/Memcached      │
├─────────────────────────────────────┤
│  Application: WordPress + plugins   │
├─────────────────────────────────────┤
│  PHP: OPcache, FPM tuning           │
├─────────────────────────────────────┤
│  Database: Query cache, indexes     │
├─────────────────────────────────────┤
│  Server: SSD, adequate RAM, CPU     │
└─────────────────────────────────────┘
```

Each layer reduces load on the layers below it. A page served from browser cache never hits your server. A page served from page cache never executes PHP.

## Quick Wins

If you're starting from scratch, these typically give the best return on effort:

1. **Enable OPcache** - Often doubles PHP performance
2. **Use PHP 8.x** - Significant speed improvements over PHP 7
3. **Add page caching** - Serves static HTML instead of executing WordPress
4. **Optimize images** - Convert to WebP, use proper sizing
5. **Use object caching** - Redis or Memcached for database query caching

## Common Mistakes

**Installing every optimization plugin.** Multiple caching plugins conflict. One comprehensive solution beats five overlapping ones.

**Caching logged-in users.** Serving cached pages to logged-in users breaks personalization and can leak private data.

**Over-aggressive JavaScript deferral.** Deferring critical scripts breaks functionality. Test thoroughly.

**Ignoring mobile.** Mobile performance often lags desktop. Test on real devices, not just throttled Chrome.

**Optimizing the wrong thing.** A site slow due to a bad database query won't be fixed by image optimization. Diagnose before treating.

## Further Reading

- [Performance Optimization for SEO](../02-wordpress-seo-optimization/04-performance-optimization-for-seo.md) - How performance affects search rankings
- [Plugin Architecture](../01-wordpress-plugin-architecture/README.md) - Writing performant plugin code
