# Content Security Policy (CSP)

Content Security Policy tells browsers which resources are allowed to load on your pages. It's the strongest defense against XSS attacks—even if an attacker injects a `<script>` tag, the browser refuses to execute it because it's not in the policy.

The problem: WordPress and its plugin ecosystem make strict CSP challenging. Inline scripts, inline styles, and third-party resources are everywhere. This guide covers practical CSP implementation that works with real WordPress sites.

## How CSP Works

CSP is delivered as an HTTP header. The browser reads it and blocks any resource that violates the policy:

```
Content-Security-Policy: script-src 'self'; style-src 'self' 'unsafe-inline'; img-src *;
```

This policy says:
- **Scripts**: Only from my domain (no inline, no external CDNs)
- **Styles**: From my domain + inline styles allowed
- **Images**: From anywhere

### CSP Directives

| Directive | Controls | Example |
|-----------|----------|---------|
| `default-src` | Fallback for all types | `'self'` |
| `script-src` | JavaScript | `'self' cdn.example.com` |
| `style-src` | CSS | `'self' 'unsafe-inline'` |
| `img-src` | Images | `'self' data: *.wp.com` |
| `font-src` | Fonts | `'self' fonts.gstatic.com` |
| `connect-src` | AJAX, WebSocket, fetch | `'self' api.example.com` |
| `frame-src` | iframes | `youtube.com vimeo.com` |
| `media-src` | Audio, video | `'self'` |
| `object-src` | Flash, Java applets | `'none'` |
| `base-uri` | `<base>` tag | `'self'` |
| `form-action` | Form submissions | `'self'` |
| `frame-ancestors` | Who can embed your site | `'none'` (prevents clickjacking) |

### Source Values

| Value | Meaning |
|-------|---------|
| `'self'` | Same origin (your domain) |
| `'none'` | Block everything |
| `'unsafe-inline'` | Allow inline scripts/styles (weakens CSP significantly) |
| `'unsafe-eval'` | Allow dynamic code execution (avoid if possible) |
| `'nonce-abc123'` | Allow specific inline scripts with matching nonce attribute |
| `'strict-dynamic'` | Trust scripts loaded by already-trusted scripts |
| `https:` | Any HTTPS URL |
| `data:` | Data URIs (inline images, fonts) |
| `*.example.com` | Wildcard subdomain matching |

## The WordPress CSP Challenge

WordPress makes strict CSP difficult because:

1. **Inline scripts everywhere** — `wp_add_inline_script()`, admin bar, Gutenberg
2. **Inline styles** — `wp_add_inline_style()`, block editor, customizer output
3. **Plugin diversity** — Each plugin adds its own scripts, styles, and external resources
4. **Admin vs frontend** — Admin area uses very different resources than the public site

### Practical Approach

Instead of trying to lock down everything at once, start with a report-only policy, identify violations, and tighten gradually.

## Implementation

### Step 1: Report-Only Mode

Start by observing what your site loads without blocking anything:

```php
add_action( 'send_headers', function() {
    if ( is_admin() ) {
        return; // Don't apply CSP to admin initially
    }

    header( "Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-src 'self'; report-uri /csp-report-endpoint" );
} );
```

Check the browser console for violations. Each violation shows what would be blocked under an enforced policy.

### Step 2: Catalog Required Resources

Common WordPress resources you'll need to allow:

| Resource | Domain | Directive |
|----------|--------|-----------|
| Google Fonts | `fonts.googleapis.com`, `fonts.gstatic.com` | `style-src`, `font-src` |
| Google Analytics | `www.google-analytics.com`, `www.googletagmanager.com` | `script-src`, `connect-src`, `img-src` |
| YouTube embeds | `www.youtube.com`, `www.youtube-nocookie.com` | `frame-src` |
| Vimeo embeds | `player.vimeo.com` | `frame-src` |
| Gravatar | `*.gravatar.com`, `secure.gravatar.com` | `img-src` |
| WordPress.org | `*.wordpress.org`, `*.wp.com` | `img-src`, `connect-src` |
| Cloudflare | `cdnjs.cloudflare.com` | `script-src`, `style-src` |
| Stripe | `js.stripe.com`, `api.stripe.com` | `script-src`, `frame-src`, `connect-src` |

### Step 3: Nonce-Based CSP (Recommended)

Instead of `'unsafe-inline'`, use nonces. WordPress 6.0+ supports script nonces:

```php
// Generate a nonce for this request
function myplugin_csp_nonce() {
    static $nonce;
    if ( ! $nonce ) {
        $nonce = wp_create_nonce( 'csp-nonce-' . time() );
    }
    return $nonce;
}

// Add nonce to inline scripts
add_filter( 'wp_inline_script_attributes', function( $attributes ) {
    $attributes['nonce'] = myplugin_csp_nonce();
    return $attributes;
} );

// Send CSP header with nonce
add_action( 'send_headers', function() {
    if ( is_admin() ) {
        return;
    }

    $nonce = myplugin_csp_nonce();

    $policy = implode( '; ', array(
        "default-src 'self'",
        "script-src 'self' 'nonce-{$nonce}' 'strict-dynamic'",
        "style-src 'self' 'unsafe-inline'",  // Inline styles are hard to nonce in WP
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self'",
        "frame-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
    ) );

    header( "Content-Security-Policy: {$policy}" );
} );
```

`'strict-dynamic'` is the key: it means "trust any script loaded by an already-trusted script." So if your nonce-approved script loads a library from a CDN, that library is automatically trusted. This dramatically simplifies managing third-party scripts.

### Step 4: Server-Level Configuration

For better performance, set CSP at the web server level:

**Nginx:**

```nginx
# In your server block
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-src 'self' youtube.com; object-src 'none'; frame-ancestors 'none';" always;
```

**Apache (.htaccess):**

```apache
Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; object-src 'none';"
```

**Cloudflare:** Add via Transform Rules or Workers for dynamic nonce injection.

## Realistic CSP for WordPress

A practical policy that works with most WordPress sites:

```
Content-Security-Policy:
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self' data: fonts.gstatic.com;
    connect-src 'self';
    frame-src 'self' youtube.com youtube-nocookie.com vimeo.com;
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'self';
    upgrade-insecure-requests;
```

This is a **pragmatic starting point**, not a perfect policy. `'unsafe-inline'` and `'unsafe-eval'` weaken protection but are required by many WordPress plugins and the block editor.

### Tightening Over Time

| Phase | Changes | Breaks |
|-------|---------|--------|
| **Start** | Allow `unsafe-inline` + `unsafe-eval` | Nothing |
| **Phase 2** | Replace `unsafe-inline` scripts with nonces | Some plugins |
| **Phase 3** | Remove `unsafe-eval` | Gutenberg editor, some plugins |
| **Phase 4** | Replace `unsafe-inline` styles with nonces/hashes | Many plugins |

Each phase breaks more things but improves security. Phase 2 is realistic for most sites. Phase 3-4 may require significant plugin changes.

## Related Security Headers

CSP works best alongside other security headers:

```php
add_action( 'send_headers', function() {
    // Prevent MIME type sniffing
    header( 'X-Content-Type-Options: nosniff' );

    // Prevent clickjacking (CSP frame-ancestors is preferred, this is fallback)
    header( 'X-Frame-Options: SAMEORIGIN' );

    // Control referrer information
    header( 'Referrer-Policy: strict-origin-when-cross-origin' );

    // Restrict browser features
    header( 'Permissions-Policy: camera=(), microphone=(), geolocation=()' );

    // Force HTTPS
    header( 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload' );
} );
```

## Testing Your Policy

| Tool | Purpose |
|------|---------|
| [CSP Evaluator](https://csp-evaluator.withgoogle.com/) | Analyze policy strength |
| [SecurityHeaders.com](https://securityheaders.com/) | Full header audit |
| Browser DevTools → Console | See CSP violations in real-time |
| Report-Only mode | Monitor before enforcing |

## Further Reading

- [Server-Level Hardening](./02-server-hardening.md) — Nginx security configuration
- [Cloudflare Hardening](./01-cloudflare-hardening.md) — Edge-level headers
- [MDN CSP Reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) — Complete specification
- [Google CSP Guide](https://developers.google.com/web/fundamentals/security/csp) — Implementation best practices
