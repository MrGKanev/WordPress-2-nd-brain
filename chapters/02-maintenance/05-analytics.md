# Analytics for WordPress

## Overview

Every website needs to understand its visitors. The question isn't whether to use analytics, but which approach balances insight with privacy, performance, and compliance requirements.

Google Analytics dominates the market, but it's not the only option—and for many sites, it's not the best one. Privacy regulations (GDPR, CCPA), performance concerns, and user trust have driven interest in alternatives that respect visitor privacy while still providing actionable data.

## The Privacy Problem with Traditional Analytics

### What Google Analytics Collects

Google Analytics tracks far more than pageviews. It collects:
- IP addresses (even when anonymized, patterns remain)
- Device fingerprints (screen size, browser, plugins)
- Cross-site behavior (via Google's advertising network)
- Demographic data inferred from browsing history
- Location data
- Session recordings in GA4's enhanced measurement

This data feeds Google's advertising business. Your visitors' behavior on your site contributes to profiles used across the web.

### Legal Implications

Several EU data protection authorities have ruled Google Analytics illegal without explicit consent:
- **Austria** (2022): DSB ruled GA transfers to US violate GDPR
- **France** (2022): CNIL issued similar ruling
- **Italy** (2022): Garante followed suit
- **Denmark, Finland, Norway**: Similar guidance

While enforcement varies, the trend is clear: using Google Analytics requires either explicit consent (which most visitors decline) or accepting legal risk.

### The Consent Problem

Cookie consent banners that require opt-in before loading analytics typically see 20-40% acceptance rates. This means:
- You lose data on 60-80% of visitors
- Your analytics become unreliable for decision-making
- You still bear the compliance burden

Privacy-focused analytics that don't require consent provide complete data without the legal complexity.

## Self-Hosted Analytics Options

Self-hosted solutions keep all data on your server. No third-party access, no data transfers, no consent requirements for basic analytics.

### Koko Analytics

**Best for**: Sites wanting simple, lightweight tracking with zero configuration.

Koko Analytics is WordPress-native—it stores data in your WordPress database and adds minimal overhead. No external services, no cookies, no consent required.

| Aspect | Details |
|--------|---------|
| Data stored | Pageviews, referrers, basic device info |
| Performance impact | Minimal (~1KB JavaScript) |
| Privacy | No cookies, no personal data, GDPR-compliant |
| Cost | Free |
| Limitations | Basic metrics only, no user flows or goals |

**What you get**: Pageviews, visitors, referrers, popular pages. What you don't get: user journeys, conversion tracking, detailed demographics.

For most content sites, blogs, and portfolios, this is enough. You learn what content resonates and where traffic comes from.

### Independent Analytics

**Best for**: Sites wanting more features than Koko while staying self-hosted.

Independent Analytics provides richer data while maintaining privacy:

| Aspect | Details |
|--------|---------|
| Data stored | Pageviews, events, UTM parameters, device/browser stats |
| Performance impact | Light JavaScript, minimal database load |
| Privacy | No cookies, anonymized data |
| Cost | Free core, Pro for advanced features |
| Limitations | Self-hosted means your server handles all tracking |

The Pro version adds real-time stats, email reports, and WooCommerce integration—useful for stores tracking conversions without external services.

### Matomo (Self-Hosted)

**Best for**: Organizations needing Google Analytics-level features with data ownership.

Matomo (formerly Piwik) is the most feature-complete self-hosted option. It can do almost everything Google Analytics does, but data stays on your server.

| Aspect | Details |
|--------|---------|
| Data stored | Everything GA collects, plus more |
| Performance impact | Heavier than lightweight alternatives |
| Privacy | Configurable—can be fully anonymous or detailed |
| Cost | Free self-hosted, paid cloud option |
| Limitations | Requires dedicated resources, more complex setup |

Matomo requires either a separate database or careful configuration to avoid impacting WordPress performance. For high-traffic sites, consider running Matomo on a separate server.

**When Matomo makes sense**: Enterprises, sites with compliance requirements demanding specific analytics capabilities, organizations migrating from GA who need feature parity.

## External Privacy-Focused Services

These services handle tracking infrastructure but prioritize privacy:

### Plausible Analytics

**Best for**: Sites wanting simple, beautiful analytics without self-hosting.

Plausible is a paid service that provides clean, focused analytics:
- No cookies, no consent required
- ~1KB script (vs GA's ~45KB)
- EU-hosted option available
- Simple dashboard focused on actionable metrics

Cost: From €9/month. Worth it if you value simplicity and don't want to manage infrastructure.

### Fathom Analytics

**Best for**: Similar to Plausible, slightly different feature set.

Fathom emphasizes privacy and simplicity:
- No cookies, GDPR/CCPA compliant
- EU isolation available
- Uptime monitoring included
- Event tracking for goals

Cost: From $14/month.

### Comparison Table

| Solution | Self-Hosted | Cost | Complexity | Features | Privacy |
|----------|-------------|------|------------|----------|---------|
| **Koko Analytics** | Yes | Free | Very low | Basic | Excellent |
| **Independent Analytics** | Yes | Free/Pro | Low | Moderate | Excellent |
| **Matomo** | Yes/Cloud | Free/Paid | High | Full | Configurable |
| **Plausible** | No | Paid | Very low | Moderate | Excellent |
| **Fathom** | No | Paid | Very low | Moderate | Excellent |
| **Google Analytics** | No | Free | Medium | Full | Poor |

## What Metrics Actually Matter

More data isn't better data. Most sites obsess over metrics that don't drive decisions.

### Metrics Worth Tracking

**Traffic trends**: Is your audience growing? Are your marketing efforts working? Week-over-week and month-over-month comparisons matter more than absolute numbers.

**Traffic sources**: Where do visitors come from? This tells you where to focus marketing efforts. Organic search growth indicates SEO progress. Referral traffic shows which relationships matter.

**Popular content**: What resonates with your audience? Double down on topics that perform. Update or improve underperforming content.

**Bounce rate by page** (if available): High bounce on landing pages suggests mismatch between expectations and content. High bounce on blog posts might be fine—they got the answer and left.

### Metrics That Rarely Matter

**Real-time visitors**: Exciting to watch, rarely actionable. Unless you're monitoring a live event or launch, this is vanity.

**Time on page**: Notoriously inaccurate. Someone reading your entire article in one tab while browsing elsewhere shows as a bounce with zero time.

**Detailed demographics**: Unless you're doing sophisticated audience targeting, knowing 23% of visitors are 25-34 doesn't change your content strategy.

**Page depth**: How many pages per session matters for some sites (e-commerce, publishers). For most, it's noise.

## Implementation Recommendations

### For Simple Sites (Blogs, Portfolios, Small Business)

Install **Koko Analytics** and check it monthly:

1. Install from WordPress plugin repository
2. No configuration needed
3. View dashboard at Dashboard → Analytics

You'll know what content works and where traffic comes from. That's enough for most decisions.

### For Content-Focused Sites (Publishers, Content Marketing)

**Independent Analytics** provides more insight without complexity:

1. Install and activate
2. Optionally configure UTM tracking for campaigns
3. Set up email reports for weekly summaries

Track which content drives engagement, which sources deliver quality traffic, and how campaigns perform.

### For E-commerce Sites

**Independent Analytics Pro** or **Matomo** for conversion tracking:

1. Track product views, add-to-cart, and purchases
2. Monitor traffic sources that convert (not just visit)
3. Identify where users drop off in the funnel

WooCommerce integration matters here. Verify the solution tracks e-commerce events properly.

### For Enterprise/Compliance Requirements

**Matomo self-hosted** with proper infrastructure:

1. Deploy Matomo on separate server
2. Configure data retention policies
3. Enable privacy features (IP anonymization, consent if needed)
4. Document compliance posture

This matches GA capabilities while maintaining data ownership.

## Google Analytics: When It Still Makes Sense

Despite privacy concerns, GA remains appropriate for some situations:

**When you're already invested**: If your organization uses Google Ads, Search Console integration, and Looker Studio dashboards extensively, switching has real costs.

**When you need specific features**: Cross-domain tracking, advanced attribution modeling, BigQuery export—some capabilities have no privacy-focused equivalent.

**When consent rates are acceptable**: If your audience accepts cookies (some regions, some demographics), you still get useful data.

**When compliance isn't your concern**: US-only sites with no EU visitors face less regulatory pressure.

If you use GA, at least:
- Enable IP anonymization
- Disable data sharing with Google
- Set appropriate data retention
- Implement proper consent management
- Consider GA4's consent mode for partial data

## Transitioning from Google Analytics

If you're moving away from GA:

**Keep historical data**: Export key reports before disabling. You'll want baselines for comparison.

**Run parallel tracking**: Install privacy-focused analytics alongside GA for 3-6 months. Compare data to understand differences.

**Adjust expectations**: Privacy-focused tools show fewer "users" because they don't track across sessions as aggressively. Your traffic didn't drop—measurement changed.

**Update dashboards and reports**: If stakeholders expect GA reports, prepare them for different metrics and interfaces.

## Performance Considerations

Analytics scripts affect page load:

| Solution | Script Size | Requests | Impact |
|----------|-------------|----------|--------|
| Koko Analytics | ~1KB | 1 | Negligible |
| Independent Analytics | ~3KB | 1 | Minimal |
| Plausible | ~1KB | 1 | Negligible |
| Matomo | ~20KB | 2-3 | Light |
| Google Analytics 4 | ~45KB | 3-5 | Moderate |

For performance-critical sites, self-hosted lightweight options add virtually no overhead. GA4's impact, while not huge, compounds with other third-party scripts.

## Further Reading

- [Performance Optimization for SEO](../05-seo/04-performance-optimization-for-seo.md) - How analytics affects Core Web Vitals
- [Plugin Recommendations](./01-plugin-recommendations.md) - Choosing analytics plugins
- [GDPR Compliance](https://gdpr.eu/) - Understanding consent requirements
