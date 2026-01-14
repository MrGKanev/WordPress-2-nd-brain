# Image Optimization Best Practices

## Overview

Image optimization is critical for WordPress performance, especially on mobile devices and websites mostly used by users using cellular signal only. Properly optimized images can significantly reduce page weight and improve Core Web Vitals metrics like LCP (Largest Contentful Paint).

## Best Practices for Image Optimization

### Image Compression

The most effective approach is to use "smart" compression that adapts to each image:

1. **Adaptive compression levels** - Fixed quality settings (like 80%) result in some images being over-compressed and others under-compressed
2. **Format conversion** - Convert to modern formats like WebP and AVIF for better compression ratios
3. **Responsive image handling** - Utilize WordPress's native srcset functionality rather than disabling image sizes

### WordPress Image Settings

```php
// Add WebP support to WordPress (add to functions.php)
function add_webp_mime_type($mimes) {
    $mimes['webp'] = 'image/webp';
    return $mimes;
}
add_filter('mime_types', 'add_webp_mime_type');
```

### Plugin Recommendations

| Plugin | Installs | Strengths | Best For |
|--------|----------|-----------|----------|
| [EWWW Image Optimizer](https://wordpress.org/plugins/ewww-image-optimizer/) | 1M+ | Local or cloud processing, WebP | Sites wanting local control |
| [ShortPixel](https://wordpress.org/plugins/shortpixel-image-optimizer/) | 300K+ | Best compression, WebP/AVIF | Most WordPress sites |
| [ShortPixel Adaptive Images](https://wordpress.org/plugins/shortpixel-adaptive-images/) | 10K+ | CDN-based responsive images | High-traffic sites |
| [Converter for Media](https://wordpress.org/plugins/webp-converter-for-media/) | 300K+ | Free WebP conversion | Budget-conscious sites |
| [Imagify](https://wordpress.org/plugins/imagify/) | 600K+ | Good UI, decent compression | WP Rocket users |

**Media Management Plugins:**

| Plugin | Purpose |
|--------|---------|
| [Enable Media Replace](https://wordpress.org/plugins/enable-media-replace/) | Replace images without changing URLs (600K+ installs) |
| [Media Cleaner](https://wordpress.org/plugins/media-cleaner/) | Find and remove unused images (90K+ installs) |
| [Media Deduper](https://wordpress.org/plugins/media-deduper/) | Identify duplicate uploads (9K+ installs) |
| [Clean Image Filenames](https://wordpress.org/plugins/clean-image-filenames/) | Sanitize uploaded filenames (30K+ installs) |

> **Expert insight**: "DPI settings don't matter for web images (only for print). When you set a fixed compression level (80% for example) to each image, some will be over-compressed and some under-compressed."

### Image Optimization Workflow

For optimal results, implement this workflow:

1. **Pre-upload optimization** (optional):
   - Resize images to maximum display dimensions
   - Remove unnecessary metadata with tools like ExifTool

2. **Server-side optimization**:
   - Use ShortPixel or another optimization plugin 
   - Enable WebP/AVIF conversion
   - Configure proper delivery method (typically Picture tag)

3. **Delivery optimization**:
   - Implement proper lazy loading (excluding LCP images)
   - Use CDN for image delivery when possible
   - Consider serving different image quality to different devices

## Modern Image Formats

### Format Comparison

| Format | Browser Support | Best For | Compression |
|--------|-----------------|----------|-------------|
| JPEG | 100% | Photographs | Good |
| PNG | 100% | Graphics, transparency | Lossless |
| WebP | ~97% | General use | 25-35% smaller than JPEG |
| AVIF | ~76% | High quality at small sizes | 50% smaller than JPEG |

### AVIF Support

AVIF offers the best compression but requires fallbacks for older browsers.

**Enable AVIF in WordPress:**

```php
// Add AVIF MIME type support
add_filter('mime_types', function($mimes) {
    $mimes['avif'] = 'image/avif';
    return $mimes;
});

// Enable AVIF uploads
add_filter('upload_mimes', function($mimes) {
    $mimes['avif'] = 'image/avif';
    return $mimes;
});
```

**Server configuration for AVIF:**

Nginx:
```nginx
location ~* \.avif$ {
    add_header Content-Type image/avif;
    add_header Cache-Control "public, max-age=31536000";
}
```

Apache (`.htaccess`):
```apache
AddType image/avif avif
```

### Picture Element with Format Fallback

The `<picture>` element serves the best format each browser supports:

```html
<picture>
    <source srcset="image.avif" type="image/avif">
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="Description" width="800" height="600" loading="lazy">
</picture>
```

**WordPress implementation (in theme):**

```php
function theme_responsive_image($attachment_id, $size = 'large', $attr = []) {
    $image = wp_get_attachment_image_src($attachment_id, $size);
    if (!$image) return '';

    $alt = get_post_meta($attachment_id, '_wp_attachment_image_alt', true);
    $upload_dir = wp_upload_dir();
    $base_path = str_replace($upload_dir['baseurl'], $upload_dir['basedir'], $image[0]);

    // Check for WebP/AVIF versions
    $webp_path = preg_replace('/\.(jpe?g|png)$/i', '.webp', $base_path);
    $avif_path = preg_replace('/\.(jpe?g|png)$/i', '.avif', $base_path);

    $webp_url = file_exists($webp_path)
        ? preg_replace('/\.(jpe?g|png)$/i', '.webp', $image[0])
        : null;
    $avif_url = file_exists($avif_path)
        ? preg_replace('/\.(jpe?g|png)$/i', '.avif', $image[0])
        : null;

    $html = '<picture>';
    if ($avif_url) {
        $html .= '<source srcset="' . esc_url($avif_url) . '" type="image/avif">';
    }
    if ($webp_url) {
        $html .= '<source srcset="' . esc_url($webp_url) . '" type="image/webp">';
    }
    $html .= '<img src="' . esc_url($image[0]) . '" ';
    $html .= 'alt="' . esc_attr($alt) . '" ';
    $html .= 'width="' . esc_attr($image[1]) . '" ';
    $html .= 'height="' . esc_attr($image[2]) . '" ';
    $html .= 'loading="lazy">';
    $html .= '</picture>';

    return $html;
}
```

### CSS Background Images with Format Detection

For CSS backgrounds, use Modernizr to detect format support:

**Generate custom Modernizr (include only what you need):**

```bash
npm install -g modernizr
modernizr -c modernizr-config.json
```

**modernizr-config.json:**
```json
{
    "minify": true,
    "options": ["setClasses"],
    "feature-detects": ["img/webp", "img/avif"]
}
```

**CSS with fallbacks:**

```css
/* Base fallback (JPEG) */
.hero-banner {
    background-image: url('../img/hero.jpg');
}

/* WebP for supporting browsers */
.webp .hero-banner {
    background-image: url('../img/hero.webp');
}

/* AVIF for supporting browsers */
.avif .hero-banner {
    background-image: url('../img/hero.avif');
}
```

Modernizr adds `webp` or `avif` classes to `<html>` based on browser support.

## Local Image Optimization Tools

For pre-upload optimization or manual workflows:

### GUI Tools

| Tool | Platform | Best For |
|------|----------|----------|
| [XnViewMP](https://www.xnview.com/en/xnviewmp/) | All | Batch conversion, WebP |
| [Squoosh](https://squoosh.app/) | Web | AVIF encoding, comparison |
| [ImageOptim](https://imageoptim.com/) | macOS | Lossless optimization |
| [Trimage](https://trimage.org/) | Linux/macOS | Lossless PNG/JPEG |

### Command-Line Tools

**PNG optimization:**
```bash
# Pngcrush - lossless PNG compression
pngcrush -brute input.png output.png

# OxiPNG - faster alternative
oxipng -o 4 -i 1 --strip safe input.png
```

**JPEG optimization:**
```bash
# jpegoptim - lossless JPEG optimization
jpegoptim --strip-all image.jpg

# With quality reduction
jpegoptim --max=85 image.jpg
```

**WebP conversion:**
```bash
# cwebp - Google's WebP encoder
cwebp -q 85 input.jpg -o output.webp

# Batch conversion
for f in *.jpg; do cwebp -q 85 "$f" -o "${f%.jpg}.webp"; done
```

**AVIF conversion:**
```bash
# avifenc (from libavif)
avifenc --min 20 --max 30 input.jpg output.avif

# Or use ImageMagick 7+
magick input.jpg -quality 50 output.avif
```

**GIF optimization:**
```bash
# Gifsicle - reduce GIF file size
gifsicle -O3 --colors 256 input.gif -o output.gif

# Batch optimize
gifsicle --batch -O3 *.gif
```

**SVG optimization:**
```bash
# SVGO - SVG Optimizer
svgo input.svg -o output.svg

# Or use web version: jakearchibald.github.io/svgomg/
```

## Progressive Image Loading

For large hero images, implement progressive loading:

**Technique 1: Dominant color placeholder**

```css
.hero-image-container {
    background-color: #3a7bd5; /* Dominant color from image */
}

.hero-image {
    opacity: 0;
    transition: opacity 0.3s ease;
}

.hero-image.loaded {
    opacity: 1;
}
```

```javascript
document.querySelectorAll('.hero-image').forEach(img => {
    if (img.complete) {
        img.classList.add('loaded');
    } else {
        img.addEventListener('load', () => img.classList.add('loaded'));
    }
});
```

**Technique 2: Low-quality image placeholder (LQIP)**

```css
.hero-container {
    background-image: url('../img/hero-tiny.jpg'); /* 20px wide, blurred */
    background-size: cover;
    filter: blur(10px);
}

.hero-container.loaded {
    background-image: url('../img/hero-full.jpg');
    filter: none;
}
```

**Technique 3: Lazy loading with Intersection Observer**

```javascript
const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            if (img.dataset.srcset) {
                img.srcset = img.dataset.srcset;
            }
            img.classList.add('loaded');
            imageObserver.unobserve(img);
        }
    });
}, {
    rootMargin: '200px 0px' // Start loading 200px before viewport
});

document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});
```

## Responsive Images Best Practices

### Using srcset Properly

WordPress generates srcset automatically, but you can customize:

```php
// Customize srcset sizes
add_filter('wp_calculate_image_srcset_meta', function($image_meta, $size_array, $image_src, $attachment_id) {
    // Only include sizes smaller than or equal to uploaded size
    return $image_meta;
}, 10, 4);

// Customize sizes attribute
add_filter('wp_calculate_image_sizes', function($sizes, $size, $image_src, $image_meta, $attachment_id) {
    // Default: (max-width: {width}px) 100vw, {width}px
    // Customize based on your layout
    return '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 800px';
}, 10, 5);
```

### Specifying Dimensions

Always include width and height to prevent Cumulative Layout Shift (CLS):

```html
<!-- Good: Browser knows dimensions before load -->
<img src="image.jpg" alt="Description" width="800" height="600" loading="lazy">

<!-- Bad: Causes layout shift -->
<img src="image.jpg" alt="Description" loading="lazy">
```

WordPress 5.5+ adds dimensions automatically. For older content:

```php
// Add missing dimensions to images
add_filter('the_content', function($content) {
    return preg_replace_callback('/<img([^>]+)>/i', function($matches) {
        if (strpos($matches[1], 'width=') === false) {
            // Attempt to get dimensions from src
            // Implementation depends on your needs
        }
        return $matches[0];
    }, $content);
});
```

## Common Pitfalls

1. **Using multiple image optimization plugins** - Creates redundant processing
2. **Over-compressing product images** - Can damage user experience
3. **Ignoring adaptive serving** - Mobile users need different image sizes
4. **Forgetting alt text** - Critical for accessibility and SEO
5. **Not properly handling above-the-fold images** - Should not be lazy-loaded
6. **Missing width/height attributes** - Causes layout shift (CLS)
7. **Serving oversized images** - 2000px image displayed at 400px wastes bandwidth
8. **Not using modern formats** - WebP/AVIF offer significant savings

## Implementation Example

For a typical WordPress site, implement:

```php
/**
 * Optimize image sizes for theme performance and consistency.
 *
 * This function removes unnecessary default image sizes that WordPress generates 
 * by default (1536x1536 and 2048x2048), helping to reduce storage use and clutter. 
 * It also defines two custom image sizes:
 *  - 'hero': 1600x800 pixels, hard-cropped (ideal for large banner images)
 *  - 'featured': 800x500 pixels, hard-cropped (suitable for blog or post thumbnails)
 *
 * Add this function to your theme’s functions.php file to improve 
 * image handling in line with your design needs.
 */
function optimize_image_sizes() {
    // Remove default image sizes that aren't needed
    remove_image_size('1536x1536');
    remove_image_size('2048x2048');
    
    // Add custom sizes that better match your theme's needs
    add_image_size('hero', 1600, 800, true);
    add_image_size('featured', 800, 500, true);
}
add_action('after_setup_theme', 'optimize_image_sizes');
```
