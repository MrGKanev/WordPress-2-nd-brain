# Security Hardening with Cloudflare

Cloudflare sits between your visitors and your server, filtering malicious traffic before it reaches WordPress. This is fundamentally different from security plugins, which only act after the request has already reached your server and loaded PHP.

## Why Cloudflare Over Security Plugins?

| Security Plugin (Wordfence, etc.) | Cloudflare |
|-----------------------------------|------------|
| Request reaches your server | Request blocked at edge |
| PHP loads WordPress | Your server never sees attack |
| Plugin checks the request | Zero server load from attacks |
| Uses your server's CPU | Works even during DDoS |

**Use both together:** Cloudflare blocks bulk attacks at the edge; a security plugin handles application-level security (file scanning, login security for legitimate traffic, etc.).

---

## Initial Setup

### 1. Add Your Domain

1. Create a Cloudflare account at [cloudflare.com](https://cloudflare.com)
2. Click "Add a site" and enter your domain
3. Select a plan (Free tier is sufficient for most WordPress sites)
4. Cloudflare scans your existing DNS records

### 2. Update Nameservers

Cloudflare provides two nameservers. Update these at your domain registrar:

```
ns1.cloudflare.com → (your assigned nameserver)
ns2.cloudflare.com → (your assigned nameserver)
```

DNS propagation takes up to 48 hours but usually completes within an hour.

### 3. Verify Connection

After nameservers propagate:
- Your site should show Cloudflare's status as "Active"
- Run `dig yourdomain.com` — the IP should be Cloudflare's, not your server's

---

## SSL/TLS Configuration

### Encryption Mode

**Critical setting** — wrong configuration breaks your site or creates security holes.

| Mode | Description | When to Use |
|------|-------------|-------------|
| **Off** | No encryption | Never |
| **Flexible** | HTTPS to Cloudflare, HTTP to server | Emergency only (insecure) |
| **Full** | HTTPS everywhere, any certificate | If you have self-signed cert |
| **Full (Strict)** | HTTPS everywhere, valid certificate | **Recommended** |

**Always use Full (Strict)** if you have a valid SSL certificate on your origin server (Let's Encrypt is free and works perfectly).

```
Dashboard → SSL/TLS → Overview → Full (strict)
```

### Edge Certificates

Enable these in SSL/TLS → Edge Certificates:

- **Always Use HTTPS:** Redirects all HTTP to HTTPS
- **Minimum TLS Version:** TLS 1.2 (blocks outdated browsers)
- **Automatic HTTPS Rewrites:** Fixes mixed content issues
- **HTTP Strict Transport Security (HSTS):** Enable after confirming site works on HTTPS

```
HSTS Settings:
├── Enable: Yes
├── Max Age: 6 months (start smaller if unsure)
├── Include Subdomains: Only if all subdomains use HTTPS
└── Preload: Only after extensive testing
```

### Origin Server Certificate

Create a Cloudflare Origin Certificate for your server:

1. SSL/TLS → Origin Server → Create Certificate
2. Choose validity period (up to 15 years)
3. Install certificate on your origin server

This certificate is trusted by Cloudflare but not browsers — use only with Full (Strict) mode.

---

## WAF (Web Application Firewall)

### Enable Managed Rulesets

Go to Security → WAF → Managed rules:

1. **Cloudflare Managed Ruleset** — Enable (general protection)
2. **Cloudflare OWASP Core Ruleset** — Enable (OWASP Top 10)
3. Set paranoia level based on your needs (higher = more false positives)

### Custom WAF Rules for WordPress

Create rules at Security → WAF → Custom rules.

#### Rule 1: Protect Login Page

```
Name: WordPress Login Protection
Expression: (http.request.uri.path eq "/wp-login.php")
Action: Managed Challenge
```

#### Rule 2: Block XMLRPC (if not needed)

```
Name: Block XMLRPC
Expression: (http.request.uri.path eq "/xmlrpc.php")
Action: Block
```

If you need XMLRPC (for Jetpack, mobile apps, etc.):

```
Name: Challenge XMLRPC
Expression: (http.request.uri.path eq "/xmlrpc.php")
Action: Managed Challenge
```

#### Rule 3: Protect WP-Admin

```
Name: WP-Admin Challenge
Expression: (http.request.uri.path contains "/wp-admin/") and not (http.request.uri.path contains "/wp-admin/admin-ajax.php")
Action: Managed Challenge
```

**Note:** Allow `admin-ajax.php` — it handles legitimate frontend AJAX requests.

#### Rule 4: Block Direct Plugin/Theme Access

```
Name: Block Direct PHP Access
Expression: (http.request.uri.path contains "/wp-content/plugins/") and (http.request.uri.path contains ".php") and not (http.request.uri.path contains "index.php")
Action: Block
```

#### Rule 5: Protect wp-config.php

```
Name: Block wp-config.php
Expression: (http.request.uri.path contains "wp-config")
Action: Block
```

#### Rule 6: Country Blocking (if applicable)

If your business only serves certain countries:

```
Name: Block Non-Target Countries
Expression: (ip.geoip.country ne "US") and (ip.geoip.country ne "CA") and (ip.geoip.country ne "GB")
Action: Block
```

For admin area only:

```
Name: Admin Geo-Restrict
Expression: (http.request.uri.path contains "/wp-admin/") and (ip.geoip.country ne "US")
Action: Block
```

---

## Rate Limiting

Prevent brute force and abuse attacks. Go to Security → WAF → Rate limiting rules.

### Login Rate Limiting

```
Name: Login Rate Limit
Expression: (http.request.uri.path eq "/wp-login.php") and (http.request.method eq "POST")
Characteristics: IP
Period: 1 minute
Requests: 5
Action: Block for 1 hour
```

### API Rate Limiting

```
Name: REST API Rate Limit
Expression: (http.request.uri.path contains "/wp-json/")
Characteristics: IP
Period: 1 minute
Requests: 60
Action: Managed Challenge
```

### General Request Rate Limiting

```
Name: General Rate Limit
Expression: (http.request.uri.path contains "/wp-")
Characteristics: IP
Period: 10 seconds
Requests: 50
Action: Managed Challenge
```

---

## Bot Management

### Bot Fight Mode

Enable in Security → Bots → Bot Fight Mode.

This automatically challenges requests from known bad bots while allowing good bots (Googlebot, Bingbot, etc.).

### Super Bot Fight Mode (Pro+)

For more control:

- Challenge or block "definitely automated" requests
- Challenge "likely automated" requests
- Allow verified bots

### Allowing Specific Bots

If Bot Fight Mode blocks legitimate services:

```
Name: Allow Specific Bot
Expression: (cf.client.bot) and (http.user_agent contains "AllowedBotName")
Action: Skip
```

---

## DDoS Protection

Cloudflare automatically mitigates DDoS attacks. Additional settings:

### HTTP DDoS Attack Protection

Security → DDoS → HTTP DDoS attack protection:

- **Ruleset:** Enabled (default)
- **Sensitivity:** High (adjust if false positives)

### Network-layer DDoS

Enabled by default. For large attacks, Cloudflare absorbs traffic at their edge.

### Under Attack Mode

For active DDoS situations:

1. Quick Actions → Under Attack Mode → Enable
2. All visitors see a JavaScript challenge (5-second delay)
3. Disable after attack subsides

**Automate with API:**

```bash
# Enable Under Attack Mode
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{"value":"under_attack"}'
```

---

## Restoring Real Visitor IPs

When using Cloudflare, your server sees Cloudflare's IP instead of visitors' real IPs. This breaks:

- Analytics and logging
- Security plugins (all requests appear from same IP)
- Geo-restrictions
- Comment spam detection

### NGINX Configuration

```nginx
# /etc/nginx/conf.d/cloudflare.conf
# Cloudflare IP ranges (update periodically)
set_real_ip_from 173.245.48.0/20;
set_real_ip_from 103.21.244.0/22;
set_real_ip_from 103.22.200.0/22;
set_real_ip_from 103.31.4.0/22;
set_real_ip_from 141.101.64.0/18;
set_real_ip_from 108.162.192.0/18;
set_real_ip_from 190.93.240.0/20;
set_real_ip_from 188.114.96.0/20;
set_real_ip_from 197.234.240.0/22;
set_real_ip_from 198.41.128.0/17;
set_real_ip_from 162.158.0.0/15;
set_real_ip_from 104.16.0.0/13;
set_real_ip_from 104.24.0.0/14;
set_real_ip_from 172.64.0.0/13;
set_real_ip_from 131.0.72.0/22;

# IPv6
set_real_ip_from 2400:cb00::/32;
set_real_ip_from 2606:4700::/32;
set_real_ip_from 2803:f800::/32;
set_real_ip_from 2405:b500::/32;
set_real_ip_from 2405:8100::/32;
set_real_ip_from 2a06:98c0::/29;
set_real_ip_from 2c0f:f248::/32;

real_ip_header CF-Connecting-IP;
```

Get current IPs: https://www.cloudflare.com/ips/

### Apache Configuration

```apache
# /etc/apache2/conf-available/cloudflare.conf
RemoteIPHeader CF-Connecting-IP
RemoteIPTrustedProxy 173.245.48.0/20
RemoteIPTrustedProxy 103.21.244.0/22
# ... (add all Cloudflare IP ranges)
```

Enable: `a2enconf cloudflare && systemctl reload apache2`

### WordPress Plugin

If you can't modify server config, use the Cloudflare plugin:

```bash
wp plugin install cloudflare --activate
```

---

## Caching Configuration

Proper caching dramatically improves performance but can cause issues with dynamic WordPress content.

### Cache Rules

Go to Caching → Cache Rules.

#### Bypass Cache for WordPress Admin

```
Name: Bypass WP Admin
Expression: (http.request.uri.path contains "/wp-admin/") or (http.request.uri.path contains "/wp-login.php")
Cache eligibility: Bypass cache
```

#### Bypass Cache for WooCommerce

```
Name: Bypass WooCommerce Dynamic
Expression: (http.request.uri.path contains "/cart/") or (http.request.uri.path contains "/checkout/") or (http.request.uri.path contains "/my-account/") or (http.cookie contains "woocommerce_cart_hash") or (http.cookie contains "woocommerce_items_in_cart")
Cache eligibility: Bypass cache
```

#### Cache Static Assets

```
Name: Cache Static Assets
Expression: (http.request.uri.path.extension in {"css" "js" "jpg" "jpeg" "png" "gif" "webp" "svg" "woff2" "woff"})
Cache eligibility: Eligible for cache
Edge TTL: 1 month
Browser TTL: 1 week
```

### APO (Automatic Platform Optimization)

Cloudflare APO ($5/month) caches entire HTML pages for WordPress:

1. Speed → Optimization → Automatic Platform Optimization
2. Install Cloudflare plugin on WordPress
3. Connect with API token

**Benefits:**
- Full page caching at edge
- Automatic cache purging on content changes
- Works with WooCommerce (bypasses cart/checkout)

---

## Page Rules (Legacy)

Page Rules are being replaced by newer features, but still useful:

```
Rule 1: Always HTTPS
URL: *example.com/*
Setting: Always Use HTTPS → On

Rule 2: Cache Everything for Static Pages
URL: *example.com/sample-page/*
Settings:
- Cache Level: Cache Everything
- Edge Cache TTL: 1 month

Rule 3: Bypass Cache for Admin
URL: *example.com/wp-admin/*
Settings:
- Cache Level: Bypass
- Disable Performance Features: On
```

---

## Firewall Events & Monitoring

### Viewing Blocked Requests

Security → Events shows all firewall actions:

- Filter by rule, action, country, IP
- Identify false positives
- Spot attack patterns

### Creating Exceptions

If legitimate traffic is blocked:

1. Find the event in Security → Events
2. Note the rule that triggered
3. Create an exception rule:

```
Name: Allow Specific Service
Expression: (http.user_agent contains "LegitService") and (ip.src eq 1.2.3.4)
Action: Skip (select which rules to skip)
```

---

## Common Issues & Troubleshooting

### Issue: Redirect Loop (ERR_TOO_MANY_REDIRECTS)

**Cause:** Usually SSL mode mismatch.

**Fix:**
1. Set SSL/TLS to "Full" or "Full (Strict)"
2. Ensure origin server has valid SSL
3. Check WordPress URLs in database:

```php
// In wp-config.php temporarily
define('WP_HOME', 'https://example.com');
define('WP_SITEURL', 'https://example.com');
```

### Issue: 502 Bad Gateway

**Cause:** Cloudflare can't reach your origin server.

**Fix:**
1. Check origin server is online
2. Verify origin IP in Cloudflare DNS is correct
3. Check firewall isn't blocking Cloudflare IPs

### Issue: Broken Admin After Enabling Cloudflare

**Cause:** Cache serving stale HTML.

**Fix:**
1. Purge Cloudflare cache
2. Add Page Rule to bypass cache for `/wp-admin/*`
3. Check for plugin conflicts

### Issue: WooCommerce Cart Not Working

**Cause:** Cart pages being cached.

**Fix:**
```
Create Cache Rule:
Expression: (http.cookie contains "woocommerce_items_in_cart")
Action: Bypass cache
```

### Issue: Real IP Not Showing

**Cause:** Server not configured to read `CF-Connecting-IP` header.

**Fix:** See "Restoring Real Visitor IPs" section above.

---

## Security Checklist

### Essential (Do Immediately)

- [ ] SSL/TLS set to "Full (Strict)"
- [ ] Always Use HTTPS enabled
- [ ] WAF Managed Rulesets enabled
- [ ] Login page Managed Challenge rule
- [ ] XMLRPC blocked or challenged
- [ ] Rate limiting on login

### Recommended

- [ ] Bot Fight Mode enabled
- [ ] Real IP restoration configured on server
- [ ] Admin area geo-restricted (if applicable)
- [ ] HSTS enabled
- [ ] Cache bypass rules for dynamic content

### Advanced

- [ ] Origin Server Certificate installed
- [ ] Custom WAF rules for your use case
- [ ] APO enabled (paid feature)
- [ ] Monitoring/alerts configured

---

## API Automation

Automate Cloudflare management with the API.

### Purge Cache on Publish

```php
// In functions.php - purge Cloudflare cache when post is published
add_action( 'publish_post', function( $post_id ) {
    $post = get_post( $post_id );
    $url = get_permalink( $post_id );

    $api_token = defined('CLOUDFLARE_API_TOKEN') ? CLOUDFLARE_API_TOKEN : '';
    $zone_id = defined('CLOUDFLARE_ZONE_ID') ? CLOUDFLARE_ZONE_ID : '';

    if ( empty($api_token) || empty($zone_id) ) return;

    wp_remote_request(
        "https://api.cloudflare.com/client/v4/zones/{$zone_id}/purge_cache",
        [
            'method'  => 'POST',
            'headers' => [
                'Authorization' => 'Bearer ' . $api_token,
                'Content-Type'  => 'application/json',
            ],
            'body'    => json_encode([
                'files' => [ $url, home_url('/') ]
            ])
        ]
    );
});
```

### Toggle Under Attack Mode

```bash
#!/bin/bash
# under-attack.sh - Toggle Cloudflare Under Attack Mode

API_TOKEN="your_token"
ZONE_ID="your_zone_id"

ACTION="${1:-status}"

case $ACTION in
    on)
        LEVEL="under_attack"
        ;;
    off)
        LEVEL="medium"
        ;;
    *)
        echo "Usage: $0 [on|off]"
        exit 1
        ;;
esac

curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/security_level" \
    -H "Authorization: Bearer ${API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data "{\"value\":\"${LEVEL}\"}"
```

## Further Reading

- [Server Hardening](./02-server-hardening.md) — Origin server security
- [Data Validation](./03-data-validation.md) — Application-level security
- [Cloudflare WordPress Documentation](https://developers.cloudflare.com/support/third-party-software/content-management-system/wordpress/)
- [Cloudflare WAF Documentation](https://developers.cloudflare.com/waf/)
- [Cloudflare IP Ranges](https://www.cloudflare.com/ips/)
