# Email Deliverability

## Overview

WordPress sends emails for everything—password resets, order confirmations, contact form submissions, user notifications. When these emails don't arrive, users assume your site is broken, orders get missed, and support tickets pile up.

The problem: WordPress's default email function (`wp_mail()`) uses PHP's `mail()` function, which sends emails directly from your server. Most hosting environments aren't configured for reliable email delivery, and spam filters increasingly distrust emails sent this way.

## Why WordPress Emails Fail

### The PHP mail() Problem

When WordPress sends email via PHP's `mail()` function:

1. **No authentication**: The email has no proof it came from a legitimate source
2. **Shared IP reputation**: Your emails share IP addresses with other sites on the same server—including spammers
3. **Missing headers**: Required email headers may be absent or incorrect
4. **No encryption**: Emails transit unencrypted, some providers reject them
5. **Blacklisting**: Hosting IPs often appear on spam blacklists

The result: emails land in spam folders, get silently dropped, or bounce entirely.

### How Spam Filters Decide

Email providers (Gmail, Outlook, Yahoo) evaluate incoming mail on multiple factors:

| Factor | What It Means |
|--------|---------------|
| **SPF** | Does the sending server have permission to send for your domain? |
| **DKIM** | Is the email cryptographically signed by your domain? |
| **DMARC** | What should happen if SPF/DKIM fail? |
| **IP reputation** | Has this IP sent spam before? |
| **Content** | Does the message look like spam? |
| **Engagement** | Do recipients open/click or mark as spam? |

PHP `mail()` fails on SPF, DKIM, and IP reputation by default. That's three strikes before content is even evaluated.

## The Solution: SMTP

SMTP (Simple Mail Transfer Protocol) is the standard for sending email. Instead of your server trying to deliver mail directly, it hands off to a dedicated email service that:

- Authenticates with proper credentials
- Signs messages with DKIM
- Uses IPs with good reputation
- Handles delivery, retries, and bounces
- Provides delivery logs and analytics

### How SMTP Changes the Flow

**Without SMTP (default WordPress):**
```
WordPress → PHP mail() → Your Server → Recipient's Server → Spam Folder
```

**With SMTP:**
```
WordPress → SMTP Plugin → Email Service → Recipient's Server → Inbox
```

The email service handles the hard part—maintaining sender reputation and navigating spam filters.

## SMTP Plugin Options

### FluentSMTP

**Best for**: Most WordPress sites. Free, well-maintained, supports multiple providers.

| Aspect | Details |
|--------|---------|
| Cost | Free |
| Providers | SendGrid, Mailgun, Amazon SES, Gmail, Outlook, custom SMTP |
| Features | Email logging, multiple connections, fallback routing |
| Installs | 500K+ |

FluentSMTP's email logging is particularly valuable—you can see exactly what WordPress sent and whether it succeeded.

### WP Mail SMTP

**Best for**: Sites wanting commercial support and more guided setup.

| Aspect | Details |
|--------|---------|
| Cost | Free core, Pro from $49/year |
| Providers | Similar to FluentSMTP plus dedicated integrations |
| Features | Email logs (Pro), tracking (Pro), weekly reports (Pro) |
| Installs | 3M+ |

The Pro version adds features like email open/click tracking and detailed reports.

### Post SMTP

**Best for**: Sites needing OAuth authentication for Gmail/Microsoft.

| Aspect | Details |
|--------|---------|
| Cost | Free core, extensions paid |
| Providers | All major providers |
| Features | Chrome extension for testing, detailed diagnostics |
| Installs | 400K+ |

## Email Service Providers

The plugin routes email; the service delivers it. Choose based on volume, budget, and requirements.

### Transactional Email Services

These specialize in application-generated email (password resets, order confirmations):

| Service | Free Tier | Paid Pricing | Best For |
|---------|-----------|--------------|----------|
| **SendGrid** | 100/day | From $15/month | Most sites |
| **Mailgun** | 5,000/month (3 months) | From $15/month | Developer-focused |
| **Amazon SES** | 62,000/month (from EC2) | $0.10/1000 | High volume, AWS users |
| **Postmark** | None | From $15/month | Deliverability-focused |
| **Brevo (Sendinblue)** | 300/day | From €25/month | Marketing + transactional |

**Recommendation for most sites**: SendGrid or Mailgun. Both have generous free tiers and excellent deliverability. Amazon SES offers the best pricing at scale but requires more setup.

### Using Gmail/Microsoft 365

You can route WordPress emails through your existing email account:

**Pros:**
- No additional service to manage
- Emails come "from" your real address
- Free if you already have the account

**Cons:**
- Daily sending limits (Gmail: 500/day, Google Workspace: 2000/day)
- OAuth setup can be complex
- Not designed for application email
- May affect personal email reputation

For low-volume sites (under 100 emails/day), this works. For anything larger, use a dedicated transactional service.

## Email Authentication: SPF, DKIM, DMARC

These three standards prove your emails are legitimate. Without them, spam filters assume the worst.

### SPF (Sender Policy Framework)

SPF lists which servers can send email for your domain. It's a DNS TXT record that looks like:

```
v=spf1 include:sendgrid.net ~all
```

This says: "SendGrid can send email for my domain. Treat others with suspicion."

**Setting up SPF:**
1. Get the SPF record from your email service (they all provide this)
2. Add it as a TXT record in your DNS
3. Test with a tool like MXToolbox

**Common mistake**: Multiple SPF records. You can only have one. If you use multiple services, combine them:

```
v=spf1 include:sendgrid.net include:_spf.google.com ~all
```

### DKIM (DomainKeys Identified Mail)

DKIM cryptographically signs your emails. The recipient can verify the signature against a public key in your DNS, proving the email wasn't forged or modified.

**Setting up DKIM:**
1. Your email service generates a key pair
2. You add the public key to your DNS as a TXT record
3. The service signs outgoing emails with the private key

The DNS record looks like:
```
s1._domainkey.yourdomain.com TXT "v=DKIM1; k=rsa; p=MIIBIjANBg..."
```

Most email services provide exact instructions. Follow them precisely—DKIM is unforgiving of errors.

### DMARC (Domain-based Message Authentication, Reporting, and Conformance)

DMARC tells receiving servers what to do when SPF/DKIM fail, and requests reports about your domain's email activity.

A basic DMARC record:
```
_dmarc.yourdomain.com TXT "v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com"
```

**DMARC policies:**
- `p=none`: Monitor only, don't take action (start here)
- `p=quarantine`: Send failures to spam
- `p=reject`: Block failures entirely

**Start with `p=none`** to receive reports without affecting delivery. Once you're confident your legitimate email passes SPF/DKIM, move to `quarantine` then `reject`.

### Authentication Checklist

| Record | Purpose | Priority |
|--------|---------|----------|
| SPF | Authorize sending servers | Required |
| DKIM | Sign emails cryptographically | Required |
| DMARC | Policy enforcement and reporting | Recommended |

Without SPF and DKIM, expect deliverability problems. With all three properly configured, you've done everything reasonable to prove legitimacy.

## Testing Email Deliverability

Before assuming email works, verify it.

### Send Test Emails

1. Configure your SMTP plugin
2. Use the plugin's "Send Test Email" feature
3. Send to addresses on different providers (Gmail, Outlook, Yahoo)
4. Check inbox (not just spam) on each

### Check Authentication

Use [Mail Tester](https://www.mail-tester.com/):
1. Get a test address from the site
2. Send an email from WordPress to that address
3. Review the detailed report

A score of 9/10 or higher indicates good configuration. Lower scores explain what's wrong.

### Verify DNS Records

Use [MXToolbox](https://mxtoolbox.com/):
- SPF Record Lookup
- DKIM Lookup
- DMARC Lookup

These tools show exactly what receiving servers see when they check your authentication.

## Common Email Types in WordPress

Different emails have different requirements:

### Transactional Emails (Critical)

- Password resets
- Order confirmations
- Account notifications
- Form submissions

These must arrive immediately and reliably. Use SMTP with a reputable provider.

### Notification Emails (Important)

- Comment notifications
- Plugin update notices
- Admin alerts

Important but not urgent. Same infrastructure as transactional, but delays are acceptable.

### Marketing Emails (Different System)

- Newsletters
- Promotional campaigns
- Drip sequences

**Don't send these through WordPress transactional email.** Marketing email has different requirements:
- Unsubscribe handling
- Bounce management
- Engagement tracking
- List management

Use dedicated newsletter tools: Mailchimp, ConvertKit, MailerLite, or self-hosted options like FluentCRM.

Mixing marketing and transactional email on the same infrastructure risks damaging your sender reputation.

## WooCommerce Email Considerations

WooCommerce sends many automated emails:
- New order (to admin)
- Order confirmation (to customer)
- Processing, completed, refunded notifications
- Low stock alerts
- Customer invoices

These are critical business communications. Customers expect order confirmations within seconds.

**WooCommerce-specific setup:**
1. Configure SMTP as described above
2. Test each email type from WooCommerce → Settings → Emails
3. Verify emails render correctly (WooCommerce templates can be complex)
4. Monitor delivery—a failed order confirmation costs trust

Consider [WooCommerce email customizers](https://wordpress.org/plugins/decorator-woocommerce-email-customizer/) if default templates don't match your brand, but test thoroughly after changes.

## Troubleshooting Common Issues

### Emails Not Sending

1. Check SMTP plugin logs—is WordPress even trying to send?
2. Verify SMTP credentials are correct
3. Test connection to SMTP server
4. Check if your host blocks outbound SMTP (port 587)

### Emails Going to Spam

1. Verify SPF, DKIM, DMARC are configured
2. Check Mail Tester score
3. Review email content for spam triggers
4. Ensure "From" address matches your domain
5. Check IP reputation (if using shared hosting)

### Emails Delayed

1. Check email service status page
2. Review sending limits—are you hitting quotas?
3. Check WordPress cron—are scheduled emails processing?
4. Verify no queue buildup in SMTP plugin

### Bouncing Emails

1. Review bounce reasons in email service dashboard
2. Hard bounces (invalid addresses): Remove from lists
3. Soft bounces (full inbox, temporary issues): Will retry
4. Authentication failures: Check SPF/DKIM

## Recommended Setup

For most WordPress sites:

1. **Install FluentSMTP** (free, full-featured)
2. **Sign up for SendGrid** (100 emails/day free)
3. **Configure SPF record** in DNS
4. **Configure DKIM** via SendGrid dashboard and DNS
5. **Add basic DMARC** record (`p=none` to start)
6. **Test** with Mail Tester
7. **Monitor** logs in FluentSMTP

Total cost: Free for low-volume sites. Time investment: 30-60 minutes for setup.

## Further Reading

- [WooCommerce Fundamentals](../06-e-commerce/01-woocommerce-fundamentals.md) - E-commerce email workflows
- [Server Hardening](../03-security/02-server-hardening.md) - Securing outbound connections
- [SendGrid Documentation](https://docs.sendgrid.com/) - Detailed provider setup
- [DMARC.org](https://dmarc.org/) - Understanding email authentication
