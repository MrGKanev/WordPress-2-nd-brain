# Security Hardening with Cloudflare

## Overview

Security is a critical aspect of any WordPress installation. Implementing Cloudflare's security features drastically reduced these attacks and improved overall performance.

**Why Cloudflare instead of a WordPress security plugin?** When a security plugin like Wordfence blocks an attack, the malicious request has already reached your server, PHP has already loaded WordPress, and the plugin runs its checks. This happens on every single request. With Cloudflare, attacks are blocked at the edge—your server never sees them. This means less CPU usage, faster responses for legitimate visitors, and protection even during DDoS attacks that would overwhelm your server.

## Cloudflare WAF Setup

### Basic WAF Configuration

Cloudflare Web Application Firewall (WAF) provides protection against common attacks while reducing server load.

1. **Sign up for Cloudflare** and add your domain
2. **Update nameservers** to point to Cloudflare
3. **Enable WAF** in the Security section of Cloudflare dashboard

### WordPress-Specific WAF Rules

Based on the Reddit case study, focus on these critical endpoints:

```
http.request.uri.path eq "/wp-login.php" or http.request.uri.path eq "/xmlrpc.php" or http.request.uri.path eq "/custom-login-path"
```

Where `/custom-login-path` is your custom login URL if you've changed it.

### Challenge Types

Choose appropriate challenge methods:

| Challenge Type | Description | Best For |
|----------------|-------------|----------|
| **JS Challenge** | Requires JavaScript execution | General protection, less intrusive |
| **Managed Challenge** | Smart detection system | Best option for WP login areas |
| **CAPTCHA** | Human verification | Highest security but more friction |

> **Real-world impact**: In the Reddit case study, adding Managed Challenge for `/wp-login.php`, `/xmlrpc.php`, and a custom login path significantly reduced brute force attacks.

## WordPress-Specific Protections

### Login Page Protection

Configure Cloudflare to protect your login page with Managed Challenge:

1. Go to **Security** > **WAF** > **Custom Rules**
2. Create a new rule:
   - Name: `WordPress Login Protection`
   - Expression: `http.request.uri.path eq "/wp-login.php"`
   - Action: `Managed Challenge`

### XMLRPC Protection

XMLRPC (`xmlrpc.php`) is a legacy API that allows external applications to communicate with WordPress. It's a massive security problem because:

1. **Amplification attacks**: A single XMLRPC request can try hundreds of username/password combinations at once (via `system.multicall`)
2. **No rate limiting**: WordPress doesn't limit XMLRPC attempts like it does for wp-login.php
3. **Pingback abuse**: Can be used for DDoS attacks against other sites
4. **Largely obsolete**: The REST API has replaced most XMLRPC use cases

XMLRPC may still be needed for some functionality:

1. If you don't use XMLRPC:
   - Expression: `http.request.uri.path eq "/xmlrpc.php"`
   - Action: `Block`

2. If you need XMLRPC for Jetpack or other services:
   - Expression: `http.request.uri.path eq "/xmlrpc.php"`
   - Action: `Managed Challenge`

### Custom Login URL Protection

If you've changed your login URL with a security plugin:

1. Create a rule with your custom path:
   - Expression: `http.request.uri.path eq "/your-custom-login"`
   - Action: `Managed Challenge`

## Rate Limiting

Implement rate limiting to prevent abuse:

1. Go to **Security** > **WAF** > **Rate limiting rules**
2. Create rules for sensitive endpoints:

```
# Login attempt rate limiting
(http.request.uri.path eq "/wp-login.php") and (http.request.method eq "POST")
- Threshold: 5 requests per minute
- Action: Block

# API and admin rate limiting
(http.request.uri.path contains "/wp-json/") or (http.request.uri.path contains "/wp-admin/")
- Threshold: 60 requests per minute
- Action: Managed Challenge
```

## WordPress + Cloudflare Integration

For optimal protection, integrate WordPress with Cloudflare:

1. Install the official Cloudflare plugin or Cloudflare APO plugin
2. Configure it with your Cloudflare Global API Key
3. Enable Automatic Platform Optimization (APO) for improved performance

## Advanced Cloudflare Configurations

### Bot Management

For sites experiencing heavy bot traffic:

1. Enable **Bot Fight Mode** in Security settings
2. Consider upgrading to **Bot Management** for more granular control

### Page Rules

Create page rules to optimize WordPress admin areas:

```
# Bypass cache for admin
URL: example.com/wp-admin*
Settings:
- Cache Level: Bypass

# High security for login
URL: example.com/wp-login.php*
Settings:
- Security Level: High
- Browser Integrity Check: On
```

## Real-World Implementation

### Step 1: Analyze Attack Patterns

Before implementing solutions, analyze your server logs to identify attack patterns:

```bash
# Check for login attempts
grep "POST /wp-login.php" /var/log/nginx/access.log | wc -l

# Check for XMLRPC attacks
grep "POST /xmlrpc.php" /var/log/nginx/access.log | wc -l
```

### Step 2: Implement Custom Rules

Create specific rules based on attack patterns:

1. Login protection with managed challenge
2. XMLRPC protection (block or challenge)
3. Rate limits for POST requests to sensitive endpoints

### Step 3: Monitor and Adjust

After implementing Cloudflare protection:

1. Monitor attack attempts in Cloudflare dashboard
2. Track server load to confirm improvement
3. Adjust WAF rules based on observations

### Step 4: Integrate with WordPress Security

Complement Cloudflare with WordPress security plugins:

- Solid Security (formerly iThemes Security, used in the case study)
- Wordfence
- Sucuri

## Case Study Results

In the Reddit case study, implementing these Cloudflare protections led to:

1. Significant reduction in server load (from 515% → 117%)
2. Elimination of lockout notifications from security plugins
3. Improved backend responsiveness
4. Better PageSpeed scores

## Resources

- [Cloudflare WordPress Documentation](https://developers.cloudflare.com/support/third-party-software/content-management-system/wordpress-specific-troubleshooting/)
- [Cloudflare WAF Rules Documentation](https://developers.cloudflare.com/waf/custom-rules)
- [Solid Security Plugin](https://wordpress.org/plugins/better-wp-security/)
