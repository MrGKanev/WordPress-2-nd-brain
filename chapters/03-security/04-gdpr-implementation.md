# GDPR Implementation

GDPR isn't optional if you have EU visitors. It's not even optional if you *might* have EU visitors. And since WordPress sites are globally accessible, that means you. The good news: WordPress has built-in tools for the basics. The bad news: most plugins ignore them, leaving gaps you need to fill.

## What GDPR Requires (Simplified)

| Requirement | What It Means for WordPress |
|-------------|---------------------------|
| **Lawful basis** | You need a reason to collect data (consent, legitimate interest, contract) |
| **Transparency** | Tell users what data you collect and why (privacy policy) |
| **Data minimization** | Only collect what you actually need |
| **Right of access** | Users can request a copy of their data |
| **Right to erasure** | Users can request deletion of their data |
| **Data portability** | Users can export their data in a machine-readable format |
| **Breach notification** | Report breaches within 72 hours |
| **Privacy by design** | Build privacy into systems from the start |

GDPR applies to all personal data: names, emails, IP addresses, cookies, order histories, form submissions, comments.

## WordPress Built-in Privacy Tools

WordPress 4.9.6+ includes privacy tools most site owners don't know about.

### Privacy Policy Page

```
Settings → Privacy → Select or create a privacy policy page
```

WordPress provides a privacy policy template with sections for common data collection scenarios. Each plugin can add its own suggested text to this template.

**For plugin developers:**

```php
add_action( 'admin_init', function() {
    if ( ! function_exists( 'wp_add_privacy_policy_content' ) ) {
        return;
    }

    wp_add_privacy_policy_content(
        'My Plugin',
        '<h2>My Plugin</h2>
        <p>This plugin collects the following data:</p>
        <ul>
            <li>User email addresses for notification purposes</li>
            <li>Usage statistics (anonymized)</li>
        </ul>
        <p>Data is stored in the site database and retained for 12 months.</p>'
    );
} );
```

### Data Export

```
Tools → Export Personal Data
```

Lets admins export all data WordPress knows about an email address. Plugins should register their data via the export hook:

```php
add_filter( 'wp_privacy_personal_data_exporters', function( $exporters ) {
    $exporters['myplugin'] = array(
        'exporter_friendly_name' => 'My Plugin Data',
        'callback'               => 'myplugin_privacy_exporter',
    );
    return $exporters;
} );

function myplugin_privacy_exporter( $email_address, $page = 1 ) {
    $user = get_user_by( 'email', $email_address );
    $data = array();

    if ( $user ) {
        $plugin_data = get_user_meta( $user->ID, '_myplugin_preferences', true );

        if ( $plugin_data ) {
            $data[] = array(
                'group_id'    => 'myplugin',
                'group_label' => 'My Plugin Preferences',
                'item_id'     => 'myplugin-prefs-' . $user->ID,
                'data'        => array(
                    array( 'name' => 'Notification Preference', 'value' => $plugin_data['notifications'] ?? 'none' ),
                    array( 'name' => 'Last Activity',          'value' => $plugin_data['last_active'] ?? 'unknown' ),
                ),
            );
        }
    }

    return array(
        'data' => $data,
        'done' => true,  // Set false if you need pagination
    );
}
```

### Data Erasure

```
Tools → Erase Personal Data
```

Same concept—plugins register erasure callbacks:

```php
add_filter( 'wp_privacy_personal_data_erasers', function( $erasers ) {
    $erasers['myplugin'] = array(
        'eraser_friendly_name' => 'My Plugin Data',
        'callback'             => 'myplugin_privacy_eraser',
    );
    return $erasers;
} );

function myplugin_privacy_eraser( $email_address, $page = 1 ) {
    $user = get_user_by( 'email', $email_address );
    $items_removed = 0;

    if ( $user ) {
        // Delete user-specific plugin data
        if ( delete_user_meta( $user->ID, '_myplugin_preferences' ) ) {
            $items_removed++;
        }

        // Delete from custom tables
        global $wpdb;
        $deleted = $wpdb->delete(
            $wpdb->prefix . 'myplugin_logs',
            array( 'user_id' => $user->ID ),
            array( '%d' )
        );
        $items_removed += $deleted;
    }

    return array(
        'items_removed'  => $items_removed,
        'items_retained' => 0,
        'messages'       => array(),
        'done'           => true,
    );
}
```

## Cookie Consent

If your site sets cookies (and it almost certainly does), you need consent before setting non-essential cookies for EU visitors.

### What Counts as a Cookie

| Type | Examples | Consent Needed? |
|------|----------|-----------------|
| **Strictly necessary** | Session cookies, CSRF tokens, cart cookies | No |
| **Functional** | Language preference, dark mode | Depends on jurisdiction |
| **Analytics** | Google Analytics, Matomo | Yes (EU) |
| **Marketing** | Facebook Pixel, Google Ads | Yes |
| **Third-party** | Embedded videos, social widgets | Yes |

### Cookie Consent Plugins

| Plugin | Approach | Best For |
|--------|----------|----------|
| **Complianz** | Auto-scans cookies, blocks scripts | Sites needing comprehensive compliance |
| **CookieYes** | Template-based, geo-targeting | Simple setup with regional controls |
| **Real Cookie Banner** | German-law focused | Sites targeting DACH region |
| **Cookie Notice for GDPR** | Lightweight notice | Basic compliance |

### Implementation Approach

The consent flow:

```
1. User visits site
2. Consent banner appears (no cookies set yet)
3. User chooses: Accept All / Reject All / Customize
4. Based on choice:
   - Essential cookies: always set
   - Analytics: only if consented
   - Marketing: only if consented
5. Store consent as a cookie (ironic but necessary)
6. On subsequent visits, check stored consent
```

**Script blocking pattern:**

```html
<!-- Before consent: script blocked -->
<script type="text/plain" data-cookiecategory="analytics">
    // Google Analytics code here
    // Won't execute until consent given
</script>

<!-- After consent: plugin changes type to text/javascript -->
```

Most consent plugins handle this automatically for known scripts. Custom scripts need the `data-cookiecategory` attribute.

## WooCommerce GDPR

WooCommerce stores significant personal data. Key considerations:

### What WooCommerce Collects

- Billing/shipping addresses
- Email addresses
- Phone numbers
- Order history
- Payment method details (tokenized)
- IP addresses (for fraud detection)
- Browser data (for analytics)

### Built-in WooCommerce Privacy

WooCommerce includes:
- Privacy policy content suggestions
- Account erasure and data export integration
- Configurable data retention periods

```
WooCommerce → Settings → Accounts & Privacy
```

| Setting | Recommendation |
|---------|---------------|
| Account erasure requests | Enable, with order anonymization |
| Personal data retention | Set to 6-12 months for inactive accounts |
| Trash pending orders | After 30 days |
| Trash failed orders | After 15 days |
| Trash cancelled orders | After 30 days |

### Checkout Consent

Add a GDPR consent checkbox to checkout:

```php
add_action( 'woocommerce_review_order_before_submit', function() {
    woocommerce_form_field( 'privacy_consent', array(
        'type'     => 'checkbox',
        'label'    => sprintf(
            'I have read and agree to the <a href="%s" target="_blank">Privacy Policy</a>',
            get_privacy_policy_url()
        ),
        'required' => true,
    ) );
} );

add_action( 'woocommerce_checkout_process', function() {
    if ( empty( $_POST['privacy_consent'] ) ) {
        wc_add_notice( 'Please accept the privacy policy to continue.', 'error' );
    }
} );
```

## Data Retention

Don't keep data forever. Define retention periods and enforce them:

```php
// Schedule daily cleanup
if ( ! wp_next_scheduled( 'myplugin_cleanup_old_data' ) ) {
    wp_schedule_event( time(), 'daily', 'myplugin_cleanup_old_data' );
}

add_action( 'myplugin_cleanup_old_data', function() {
    global $wpdb;

    // Delete logs older than 90 days
    $wpdb->query( $wpdb->prepare(
        "DELETE FROM {$wpdb->prefix}myplugin_logs
         WHERE created_at < %s",
        date( 'Y-m-d H:i:s', strtotime( '-90 days' ) )
    ) );

    // Anonymize old analytics (keep aggregates, remove personal data)
    $wpdb->query( $wpdb->prepare(
        "UPDATE {$wpdb->prefix}myplugin_analytics
         SET ip_address = '0.0.0.0', user_agent = 'anonymized'
         WHERE recorded_at < %s",
        date( 'Y-m-d H:i:s', strtotime( '-30 days' ) )
    ) );
} );
```

## GDPR Compliance Checklist

- [ ] Privacy policy page published and linked in footer
- [ ] Cookie consent banner implemented (blocks non-essential cookies until consent)
- [ ] Data export works (Tools → Export Personal Data)
- [ ] Data erasure works (Tools → Erase Personal Data)
- [ ] All plugins registered with export/erasure hooks
- [ ] Data retention periods defined and automated
- [ ] Contact forms include consent checkbox
- [ ] Comment forms include consent checkbox (WordPress 4.9.6+)
- [ ] WooCommerce privacy settings configured
- [ ] Third-party data transfers documented (analytics, CDN, payment processors)
- [ ] Data Processing Agreements signed with processors
- [ ] Breach notification procedure documented

## Further Reading

- [Input Sanitization & Output Escaping](./03-data-validation.md) — Secure data handling
- [Analytics](../02-maintenance/05-analytics.md) — Privacy-focused analytics alternatives
- [GDPR Official Text](https://gdpr.eu/) — The regulation itself
- [WordPress Privacy Handbook](https://developer.wordpress.org/plugins/privacy/) — Plugin developer guide
