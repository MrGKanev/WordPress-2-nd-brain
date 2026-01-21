# Hosting Selection and Optimization

Your hosting is the foundation of WordPress performance. No amount of optimization, caching, or plugin tuning can fix a slow server. If your server takes 500ms to respond before WordPress even starts processing, you've already lost half a second before any code runs.

This guide covers how to choose hosting, when to upgrade, and how to migrate without downtime.

## Hosting Types Comparison

### Shared Hosting

Multiple websites share one server's resources (CPU, RAM, disk).

**Pros:**
- Cheapest option ($3-15/month)
- No server management required
- Sufficient for small, low-traffic sites

**Cons:**
- Performance varies based on "noisy neighbors"
- Limited resources (typically 1-2GB RAM allocated)
- Often oversold (500+ sites per server)
- No root access or custom configurations

**Best for:** Personal blogs, hobby sites, small business brochures under 10K monthly visitors.

### Managed WordPress Hosting

WordPress-optimized environment with specialized support and features.

**Pros:**
- WordPress-specific optimizations pre-configured
- Automatic updates, backups, and security
- Expert WordPress support
- Staging environments included
- Better performance than shared hosting

**Cons:**
- Higher cost ($15-100+/month)
- May restrict certain plugins
- Less flexibility for non-WordPress needs

**Best for:** Business sites, agencies managing client sites, anyone who values time over cost.

### VPS (Virtual Private Server)

Dedicated virtual resources on a shared physical server.

**Pros:**
- Guaranteed resources (not affected by other sites)
- Root access for full customization
- Scalable resources
- Better price/performance than managed hosting

**Cons:**
- Requires server administration knowledge
- You handle security, updates, and backups
- No WordPress-specific support

**Best for:** Developers comfortable with server management, sites needing custom configurations.

### Dedicated Server

An entire physical server exclusively for your sites.

**Pros:**
- Maximum performance and resources
- Complete control over environment
- No shared resources or noisy neighbors

**Cons:**
- High cost ($100-500+/month)
- Full responsibility for management
- Overkill for most WordPress sites

**Best for:** High-traffic sites (1M+ monthly visitors), enterprise applications.

### Cloud Hosting (AWS, GCP, DigitalOcean)

Scalable infrastructure with pay-as-you-go pricing.

**Pros:**
- Instant scaling for traffic spikes
- Global infrastructure options
- Fine-grained resource control
- Enterprise-grade reliability

**Cons:**
- Complex pricing (can be expensive)
- Steep learning curve
- Requires significant DevOps knowledge

**Best for:** High-traffic sites, applications needing auto-scaling, teams with DevOps expertise.

---

## Provider Comparison Matrix

### Managed WordPress Hosting

| Provider | Starting Price | Strengths | Weaknesses | Best For |
|----------|---------------|-----------|------------|----------|
| **Kinsta** | $35/month | Google Cloud infrastructure, excellent support, dev tools | Expensive for small sites | Agencies, high-traffic sites |
| **WP Engine** | $20/month | Reliable, good staging, strong security | Can be slow to adopt new PHP | Enterprise, agencies |
| **Cloudways** | $11/month | Flexible (choose cloud provider), good performance | Less WordPress-specific than competitors | Developers wanting managed cloud |
| **Flywheel** | $13/month | Designer-focused, beautiful dashboard | Owned by WP Engine, limited plans | Designers, small agencies |
| **SiteGround** | $15/month | Good support, easy staging | Performance varies by plan | Small businesses, beginners |
| **Rocket.net** | $25/month | Cloudflare Enterprise included, fast | Newer provider, smaller track record | Performance-focused sites |

### VPS / Cloud Providers

| Provider | Starting Price | Strengths | Weaknesses | Best For |
|----------|---------------|-----------|------------|----------|
| **DigitalOcean** | $6/month | Simple, predictable pricing, good docs | Basic support | Developers, small projects |
| **Vultr** | $6/month | Many locations, high-frequency CPUs | Dashboard less polished | Performance-focused VPS |
| **Linode** | $5/month | Reliable, good support | Fewer features than competitors | Budget VPS |
| **Hetzner** | €4/month | Excellent price/performance | EU locations only (mostly) | European sites, budget |
| **AWS Lightsail** | $5/month | AWS integration, predictable pricing | Limited compared to full AWS | AWS ecosystem users |

### Budget Shared Hosting (Use with Caution)

| Provider | Verdict | Notes |
|----------|---------|-------|
| **GoDaddy** | ⚠️ Avoid | Oversells servers, aggressive upselling, poor support |
| **Bluehost** | ⚠️ Avoid | Owned by EIG, performance issues, misleading pricing |
| **HostGator** | ⚠️ Avoid | EIG-owned, same issues as Bluehost |
| **SiteGround** | ✅ Acceptable | One of the better shared options |
| **Namecheap** | ✅ Acceptable | Decent shared hosting, reasonable pricing |

**Note:** Many "top hosting" lists are affiliate-driven. Research actual user experiences on Reddit r/webhosting and WordPress forums.

---

## Key Selection Criteria

### 1. Server Technology Stack

**Web Server:**
| Server | Performance | Ease of Use | WordPress Compatibility |
|--------|-------------|-------------|------------------------|
| LiteSpeed | ★★★★★ | Easy (with LSCache plugin) | Excellent |
| NGINX | ★★★★☆ | Requires configuration | Excellent |
| Apache | ★★★☆☆ | Easy (.htaccess support) | Native |
| OpenLiteSpeed | ★★★★☆ | Free LiteSpeed alternative | Excellent |

**LiteSpeed** is generally the fastest for WordPress due to built-in cache and optimization. **NGINX** is second-best and more common. Avoid Apache for high-traffic sites unless necessary.

**PHP Version:**
Always use the latest stable PHP version your plugins support:
- PHP 8.3/8.4 — Current recommended
- PHP 8.2 — Minimum for new projects
- PHP 8.1 — End of security support December 2025

**Database:**
- MariaDB 10.6+ or MySQL 8.0+ recommended
- Ensure InnoDB engine (not MyISAM)
- Check for slow query logging availability

### 2. Performance Characteristics

**Minimum requirements for production:**

| Site Type | RAM | CPU | Storage |
|-----------|-----|-----|---------|
| Blog (< 50K visits/month) | 1GB | 1 core | 20GB SSD |
| Business site | 2GB | 2 cores | 40GB SSD |
| WooCommerce (< 1K orders/month) | 4GB | 2 cores | 60GB SSD |
| WooCommerce (1K+ orders/month) | 8GB+ | 4+ cores | 100GB+ NVMe |
| High-traffic (100K+ daily) | 16GB+ | 4+ cores | NVMe required |

**Storage type matters:**
- **NVMe SSD** — Fastest, 5-7x faster than SATA SSD
- **SATA SSD** — Good, standard for most hosts
- **HDD** — Avoid for WordPress (too slow for database operations)

### 3. Geographic Location

Server location affects latency:

| Audience | Recommended Server Location |
|----------|---------------------------|
| US East Coast | Virginia, New York |
| US West Coast | California, Oregon |
| Europe | Frankfurt, Amsterdam, London |
| Asia-Pacific | Singapore, Tokyo, Sydney |
| Global | Use CDN with edge locations |

**Rule of thumb:** Place your server within 100ms latency of your primary audience. Use tools like [Cloudping](https://cloudping.info/) to check latency to data centers.

### 4. Essential Features Checklist

**Must-have:**
- [ ] SSH access
- [ ] Free SSL certificates (Let's Encrypt)
- [ ] Automated daily backups
- [ ] Staging environment
- [ ] PHP version switching
- [ ] Object caching support (Redis/Memcached)

**Nice-to-have:**
- [ ] WP-CLI access
- [ ] Git deployment
- [ ] HTTP/2 and HTTP/3 support
- [ ] Built-in CDN
- [ ] Malware scanning
- [ ] DDoS protection

---

## Signs You Need to Upgrade

### Performance Indicators

| Metric | Warning Level | Critical Level |
|--------|--------------|----------------|
| TTFB | > 400ms | > 800ms |
| Server response time | > 500ms | > 1000ms |
| PHP memory usage | > 70% of limit | > 90% of limit |
| CPU usage | Sustained > 70% | Sustained > 90% |
| Database connections | > 80% of max | At max |

### Symptoms Checklist

**Upgrade if you experience:**
- [ ] 503/504 errors during traffic spikes
- [ ] "Allowed memory exhausted" errors in logs
- [ ] Database connection timeouts
- [ ] Slow admin panel (> 3s to load)
- [ ] Page caching not helping response time
- [ ] Host sending resource warning emails

### When NOT to Upgrade

Hosting isn't always the problem:
- Unoptimized database (clean up before upgrading)
- Too many plugins (audit before upgrading)
- Poorly coded theme (switch theme before upgrading)
- No caching implemented (add caching first)
- Missing object caching (enable Redis first)

**Test before upgrading:** Profile your site with [Query Monitor](https://wordpress.org/plugins/query-monitor/) to identify actual bottlenecks.

---

## Migration Guide

### Pre-Migration Checklist

1. **Full backup** — Files AND database
2. **Document current settings:**
   - PHP version
   - php.ini customizations
   - Cron jobs
   - Custom server configurations
3. **Export plugin/theme list**
4. **Note DNS settings** (especially if using email)
5. **Check SSL certificate** — Will you need a new one?
6. **Inform stakeholders** of potential downtime

### Migration Methods

#### Method 1: Plugin Migration (Easiest)

**Recommended plugins:**
- **All-in-One WP Migration** — Best for small sites (< 512MB free)
- **Duplicator** — Good for larger sites, more technical
- **UpdraftPlus** — Good if already using for backups
- **Migrate Guru** — Free for sites up to 200GB

**Process:**
1. Install migration plugin on source site
2. Create export package
3. Set up WordPress on new host
4. Install same plugin on new site
5. Import package
6. Update URLs if domain changed

#### Method 2: Manual Migration (Most Reliable)

```bash
# 1. Export database on old server
wp db export backup.sql --add-drop-table

# 2. Archive wp-content
tar -czf wp-content.tar.gz wp-content/

# 3. Transfer files to new server
rsync -avz --progress wp-content.tar.gz user@newserver:/path/to/site/

# 4. On new server, extract and import
tar -xzf wp-content.tar.gz
wp db import backup.sql

# 5. Update URLs if needed
wp search-replace 'old-domain.com' 'new-domain.com' --all-tables

# 6. Regenerate permalinks
wp rewrite flush
```

#### Method 3: Host-Provided Migration

Many managed hosts offer free migration:
- **Kinsta** — Free migration included
- **WP Engine** — Free automated migration
- **SiteGround** — Free manual migration by support
- **Cloudways** — Free migration plugin

**Advantage:** They handle the technical work and ensure compatibility.

### DNS Migration (Zero Downtime)

**Goal:** Switch DNS only after the new site is verified working.

1. **Set up new site completely** before touching DNS
2. **Test new site** using hosts file or temporary URL
3. **Lower TTL** on DNS records to 300 seconds (5 minutes), 24-48 hours before migration
4. **Sync database** one final time just before DNS switch
5. **Update DNS** to point to new server
6. **Monitor** both old and new servers during propagation
7. **Keep old server running** 48 hours after switch

```bash
# Test new site locally by adding to /etc/hosts (Mac/Linux)
# or C:\Windows\System32\drivers\etc\hosts (Windows)
123.456.789.0  yourdomain.com www.yourdomain.com
```

### Post-Migration Checklist

- [ ] All pages load correctly
- [ ] Forms submit successfully
- [ ] WooCommerce checkout works (test purchase)
- [ ] Email sending works
- [ ] Cron jobs running
- [ ] SSL certificate active (no mixed content)
- [ ] Caching working
- [ ] Performance improved (test TTFB)
- [ ] Backups configured on new host
- [ ] Monitoring set up

---

## Server Stack Configuration

### Recommended LEMP Stack

**Linux + NGINX + MariaDB + PHP** is the recommended stack for WordPress.

```nginx
# /etc/nginx/sites-available/wordpress.conf
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com www.example.com;
    root /var/www/example.com;
    index index.php;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript
               text/xml application/xml application/xml+rss text/javascript
               image/svg+xml;

    # Static file caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|webp|woff2|svg)$ {
        expires 365d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # WordPress permalinks
    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    # PHP processing
    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_buffer_size 128k;
        fastcgi_buffers 256 16k;
        fastcgi_busy_buffers_size 256k;
    }

    # Block access to sensitive files
    location ~ /\.(ht|git|svn) {
        deny all;
    }

    location = /wp-config.php {
        deny all;
    }
}
```

### FastCGI Cache (Page Caching at NGINX Level)

For sites without WP Rocket or similar plugins:

```nginx
# Add to http block in nginx.conf
fastcgi_cache_path /var/cache/nginx levels=1:2 keys_zone=wordpress:100m inactive=60m;
fastcgi_cache_key "$scheme$request_method$host$request_uri";

# Add to server block
set $skip_cache 0;

# Skip cache for logged-in users
if ($http_cookie ~* "wordpress_logged_in") {
    set $skip_cache 1;
}

# Skip cache for POST requests
if ($request_method = POST) {
    set $skip_cache 1;
}

# Skip cache for WooCommerce
if ($request_uri ~* "/cart/|/checkout/|/my-account/") {
    set $skip_cache 1;
}

location ~ \.php$ {
    fastcgi_cache wordpress;
    fastcgi_cache_valid 200 60m;
    fastcgi_cache_bypass $skip_cache;
    fastcgi_no_cache $skip_cache;
    add_header X-Cache-Status $upstream_cache_status;
    # ... rest of PHP config
}
```

---

## Staging Environments

### Why Staging Matters

Never test on production. A staging environment lets you:
- Test plugin updates before applying
- Develop new features safely
- Debug issues without affecting visitors
- Train clients without risk

### Staging Setup Options

**1. Host-provided staging** (easiest)
- One-click clone in Kinsta, WP Engine, SiteGround
- Automatic URL replacement
- Push changes to live

**2. Subdomain staging**
```
staging.yourdomain.com → separate WordPress install
```

**3. Local development**
- [LocalWP](https://localwp.com/) — Best for WordPress
- [DDEV](https://ddev.com/) — Docker-based, powerful
- [Lando](https://lando.dev/) — Flexible, multi-framework

### Staging Best Practices

- **Sync database regularly** from production to staging
- **Never push staging database to production** (overwrites orders, users)
- **Disable emails** on staging (use plugin like "Disable Emails")
- **Block search engines** (Settings → Reading → Discourage search engines)
- **Use .htpasswd protection** to prevent accidental access

---

## Red Flags to Avoid

### Host Warning Signs

| Red Flag | Why It's Bad |
|----------|--------------|
| "Unlimited" everything | Nothing is unlimited; they're overselling |
| No SSH access | Can't use WP-CLI, limited troubleshooting |
| Old PHP only (< 8.0) | Security risk, poor performance |
| No staging environment | Risky updates, unprofessional workflow |
| Aggressive upselling | Core product likely underpowered |
| Long-term contract required | They need lock-in because product is weak |
| No refund policy | Same reasoning |
| Support only by ticket (24+ hour response) | Problems become emergencies |

### Contract Gotchas

- **Renewal pricing** — Many hosts advertise $3/month but renew at $15/month
- **"Free domain" lock-in** — Domain transfer fees if you leave
- **Backup charges** — "Backups included" but restoration costs extra
- **Resource limits** — "Unlimited" hosting with hidden CPU/memory caps

**Always read the Terms of Service** for resource limits and acceptable use policies.

## Further Reading

- [PHP-FPM Optimization](../04-performance/03-php-fpm-optimization.md) — Server-side PHP configuration
- [Database Optimization](../04-performance/07-database-optimizations.md) — MySQL/MariaDB tuning
- [Server Hardening](../03-security/01-server-hardening.md) — Security configuration
- [WP-CLI Essentials](./03-wp-cli-essentials.md) — Command-line management
