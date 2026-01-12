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

## Common Pitfalls

1. **Using multiple image optimization plugins** - Creates redundant processing
2. **Over-compressing product images** - Can damage user experience
3. **Ignoring adaptive serving** - Mobile users need different image sizes
4. **Forgetting alt text** - Critical for accessibility and SEO
5. **Not properly handling above-the-fold images** - Should not be lazy-loaded

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
