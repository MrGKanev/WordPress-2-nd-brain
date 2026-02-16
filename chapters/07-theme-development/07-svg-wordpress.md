# SVG in WordPress

SVG (Scalable Vector Graphics) is the ideal format for logos, icons, illustrations, and UI elements — it scales to any size without quality loss and is typically much smaller than equivalent PNGs. But WordPress blocks SVG uploads by default because SVG files can contain JavaScript, making them a potential XSS vector.

## Why WordPress Blocks SVGs

An SVG file is XML. It can contain `<script>` tags, event handlers (`onload`, `onclick`), and external references. A malicious SVG uploaded to your media library could execute JavaScript when viewed:

```xml
<!-- Malicious SVG — this is why WordPress blocks them -->
<svg xmlns="http://www.w3.org/2000/svg">
    <text x="10" y="20">Looks harmless</text>
</svg>
```

The actual malicious patterns are more subtle — embedded event handlers, external entity references, and data URIs that WordPress's basic file type checks wouldn't catch.

## Safe SVG Upload

### Plugin Approach (Recommended)

| Plugin | Sanitization | Features |
|--------|-------------|----------|
| **Safe SVG** | Yes (DOMPurify-based server-side) | Media library preview, sanitization |
| **SVG Support** | Basic | Allows SVG upload with role control |
| **WP SVG Images** | Yes | Sanitization + media library integration |

**Safe SVG** by Starter Templates is the most widely used. It sanitizes uploaded SVGs by parsing the XML, removing dangerous elements and attributes, and saving a clean version.

### Manual Approach (Without Plugin)

If you prefer not to use a plugin, allow SVG uploads with sanitization:

```php
// Allow SVG upload for administrators only
add_filter( 'upload_mimes', function( $mimes ) {
    if ( current_user_can( 'manage_options' ) ) {
        $mimes['svg']  = 'image/svg+xml';
        $mimes['svgz'] = 'image/svg+xml';
    }
    return $mimes;
} );

// Fix SVG file type detection (WordPress 5.0+)
add_filter( 'wp_check_filetype_and_ext', function( $data, $file, $filename, $mimes ) {
    $ext = pathinfo( $filename, PATHINFO_EXTENSION );
    if ( 'svg' === $ext ) {
        $data['type'] = 'image/svg+xml';
        $data['ext']  = 'svg';
    }
    return $data;
}, 10, 4 );
```

**This alone is NOT safe.** You must sanitize the SVG content on upload. Consider using the `enshrined/svg-sanitize` PHP library:

```bash
composer require enshrined/svg-sanitize
```

```php
use enshrined\svgSanitize\Sanitizer;

add_filter( 'wp_handle_upload_prefilter', function( $file ) {
    if ( 'image/svg+xml' !== $file['type'] ) {
        return $file;
    }

    $sanitizer = new Sanitizer();
    $dirty_svg = file_get_contents( $file['tmp_name'] );
    $clean_svg = $sanitizer->sanitize( $dirty_svg );

    if ( false === $clean_svg ) {
        $file['error'] = 'This SVG file could not be sanitized and was rejected.';
        return $file;
    }

    file_put_contents( $file['tmp_name'], $clean_svg );
    return $file;
} );
```

## Inline SVG in Themes

For icons and UI elements, inline SVG in your templates gives you full CSS control and eliminates HTTP requests.

### Direct Inline

```php
<button class="menu-toggle">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <line x1="3" y1="6" x2="21" y2="6"/>
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
    </svg>
    <span class="screen-reader-text">Menu</span>
</button>
```

Key attributes:
- `aria-hidden="true"` — Decorative icons should be hidden from screen readers
- `stroke="currentColor"` — Icon color inherits from CSS `color` property
- Pair with `screen-reader-text` for accessible labels

### Helper Function

```php
function theme_inline_svg( $name, $args = array() ) {
    $defaults = array(
        'class'       => '',
        'aria_hidden' => true,
        'role'        => 'img',
    );
    $args = wp_parse_args( $args, $defaults );

    $file = get_template_directory() . "/assets/svg/{$name}.svg";
    if ( ! file_exists( $file ) ) {
        return '';
    }

    $svg = file_get_contents( $file );

    // Add class
    if ( $args['class'] ) {
        $svg = str_replace( '<svg', '<svg class="' . esc_attr( $args['class'] ) . '"', $svg );
    }

    // Add aria-hidden for decorative icons
    if ( $args['aria_hidden'] ) {
        $svg = str_replace( '<svg', '<svg aria-hidden="true"', $svg );
    }

    return $svg;
}
```

Usage:

```php
echo theme_inline_svg( 'arrow-right', array( 'class' => 'icon icon-arrow' ) );
```

## SVG Sprite System

For sites using many icons, an SVG sprite combines all icons into one file. Each icon is defined once and referenced by ID throughout the site.

### Creating the Sprite

```xml
<!-- assets/svg/sprite.svg -->
<svg xmlns="http://www.w3.org/2000/svg" style="display:none">
    <symbol id="icon-search" viewBox="0 0 24 24">
        <circle cx="11" cy="11" r="8" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65" stroke="currentColor" stroke-width="2"/>
    </symbol>

    <symbol id="icon-cart" viewBox="0 0 24 24">
        <circle cx="9" cy="21" r="1" fill="currentColor"/>
        <circle cx="20" cy="21" r="1" fill="currentColor"/>
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" fill="none" stroke="currentColor" stroke-width="2"/>
    </symbol>

    <symbol id="icon-menu" viewBox="0 0 24 24">
        <line x1="3" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2"/>
        <line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>
        <line x1="3" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2"/>
    </symbol>
</svg>
```

### Using the Sprite

Include the sprite once in your theme (typically in `header.php` or via a hook):

```php
add_action( 'wp_body_open', function() {
    $sprite = get_template_directory() . '/assets/svg/sprite.svg';
    if ( file_exists( $sprite ) ) {
        echo file_get_contents( $sprite );
    }
} );
```

Then reference icons by ID:

```html
<svg class="icon" aria-hidden="true">
    <use href="#icon-search"/>
</svg>
```

### Benefits Over Individual Files

| Approach | HTTP Requests | Caching | CSS Control |
|----------|-------------|---------|-------------|
| Individual SVG files | 1 per icon | Good | Limited |
| Inline SVG | 0 | None (in HTML) | Full |
| SVG sprite | 0 (inline) or 1 (external) | Good if external | Full |
| Icon font | 1-2 files | Good | Color only |

SVG sprites give the best of both worlds: one load, full CSS control, and each icon is accessible as a distinct element.

## Styling SVGs with CSS

### Color Control

```css
/* Icons using currentColor inherit text color */
.icon {
    width: 1em;
    height: 1em;
    fill: currentColor; /* or stroke: currentColor */
}

/* Override for specific contexts */
.button--primary .icon {
    color: white;
}
```

### Sizing

```css
/* Size relative to text */
.icon {
    width: 1em;
    height: 1em;
    vertical-align: -0.125em; /* Optical alignment with text */
}

/* Fixed size */
.icon--large {
    width: 48px;
    height: 48px;
}
```

### Hover and Transitions

```css
.icon {
    transition: transform 0.2s ease, color 0.2s ease;
}

.button:hover .icon {
    transform: translateX(4px);
}
```

## SVG in the Block Editor

### Custom Block with SVG

In block development, use SVG for block icons:

```javascript
import { registerBlockType } from '@wordpress/blocks';

const icon = (
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L2 22h20L12 2z"/>
    </svg>
);

registerBlockType( 'myplugin/custom-block', {
    icon: icon,
    // ... block configuration
} );
```

### SVG as Block Content

For blocks that output SVGs (decorative separators, icons), make sure the SVG is included in the `save()` function so it persists in the post content.

## Performance Considerations

| Consideration | Recommendation |
|--------------|----------------|
| Optimize SVG files | Run through SVGO before use |
| Remove metadata | Editor comments, unused IDs, empty groups |
| Simplify paths | Reduce decimal precision, merge shapes |
| Gzip/Brotli | SVGs compress extremely well (~60-80% reduction) |
| Avoid base64 in CSS | Use inline or sprite instead (base64 is 33% larger) |

### SVGO Configuration

[SVGO](https://github.com/svg/svgo) optimizes SVG files:

```bash
npx svgo input.svg -o output.svg

# Or batch optimize
npx svgo -f ./assets/svg/ -o ./assets/svg/
```

A typical SVGO optimization reduces file size by 30-60% by removing editor metadata, unnecessary attributes, and simplifying paths.

## Accessibility

| Element Type | Approach |
|-------------|----------|
| Decorative icon | `aria-hidden="true"`, no title |
| Meaningful icon (no text label) | `role="img"` + `<title>` inside SVG |
| Icon with visible text label | `aria-hidden="true"` on SVG, text provides context |
| Complex illustration | `role="img"` + `aria-labelledby` referencing `<title>` and `<desc>` |

```html
<!-- Meaningful icon without text label -->
<svg role="img" aria-labelledby="close-title">
    <title id="close-title">Close dialog</title>
    <path d="M18 6L6 18M6 6l12 12" stroke="currentColor"/>
</svg>

<!-- Decorative icon with text label -->
<button>
    <svg aria-hidden="true"><use href="#icon-search"/></svg>
    Search
</button>
```

## Further Reading

- [Accessibility Basics](./04-accessibility.md) — ARIA and accessible markup
- [Frontend Asset Optimization](../04-performance/13-frontend-asset-optimization.md) — Asset optimization strategies
- [Image Optimization](../04-performance/06-image-optimizations.md) — Image format decisions
- [SVGO Documentation](https://github.com/svg/svgo) — SVG optimization tool
