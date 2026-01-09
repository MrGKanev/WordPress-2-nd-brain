# Internationalization (i18n)

## Overview

Internationalization (i18n) prepares your plugin for translation into any language. Localization (l10n) is the actual translation. WordPress has built-in functions that make both straightforward—if you use them correctly from the start.

Any plugin distributed publicly should be internationalized. Even internal plugins benefit when teams are multilingual.

## Basic Translation Functions

### Returning Translated Strings

```php
// __() - Returns translated string
$text = __( 'Hello World', 'my-plugin' );

// Use when storing or manipulating text
$message = sprintf(
    __( 'You have %d new messages', 'my-plugin' ),
    $count
);
```

### Echoing Translated Strings

```php
// _e() - Echoes translated string
_e( 'Submit', 'my-plugin' );

// Same as:
echo __( 'Submit', 'my-plugin' );
```

### Translation with Escaping

Always use escaped versions in output:

```php
// esc_html__() - Return escaped for HTML
echo '<p>' . esc_html__( 'Welcome message', 'my-plugin' ) . '</p>';

// esc_html_e() - Echo escaped for HTML
echo '<p>';
esc_html_e( 'Welcome message', 'my-plugin' );
echo '</p>';

// esc_attr__() - Return escaped for attributes
echo '<input placeholder="' . esc_attr__( 'Enter name', 'my-plugin' ) . '">';

// esc_attr_e() - Echo escaped for attributes
echo '<input value="';
esc_attr_e( 'Submit', 'my-plugin' );
echo '">';
```

## Text Domains

The text domain identifies which plugin a translation belongs to. It should match your plugin slug:

```php
// Plugin header
/**
 * Plugin Name: My Awesome Plugin
 * Text Domain: my-awesome-plugin
 * Domain Path: /languages
 */

// All translation functions use the same text domain
__( 'Text', 'my-awesome-plugin' );
_e( 'Text', 'my-awesome-plugin' );
esc_html__( 'Text', 'my-awesome-plugin' );
```

### Loading Text Domain

```php
add_action( 'init', 'my_plugin_load_textdomain' );

function my_plugin_load_textdomain() {
    load_plugin_textdomain(
        'my-awesome-plugin',
        false,
        dirname( plugin_basename( __FILE__ ) ) . '/languages'
    );
}
```

Translation files go in `/languages/`:
```
my-plugin/
├── languages/
│   ├── my-awesome-plugin.pot          (Template)
│   ├── my-awesome-plugin-fr_FR.po     (French source)
│   ├── my-awesome-plugin-fr_FR.mo     (French compiled)
│   ├── my-awesome-plugin-de_DE.po     (German source)
│   └── my-awesome-plugin-de_DE.mo     (German compiled)
└── my-plugin.php
```

## Advanced Translation Functions

### Singular/Plural: _n()

```php
// _n() handles singular and plural forms
$message = sprintf(
    _n(
        '%d item',      // Singular
        '%d items',     // Plural
        $count,         // Number to check
        'my-plugin'     // Text domain
    ),
    $count
);

// Examples:
// $count = 1: "1 item"
// $count = 5: "5 items"
```

### Context for Ambiguous Strings: _x()

When the same English word has different meanings:

```php
// _x() adds context for translators
$post = _x( 'Post', 'noun - a blog post', 'my-plugin' );
$post = _x( 'Post', 'verb - to publish', 'my-plugin' );

// Context appears in translation tools
// Translators see: "Post" with note "noun - a blog post"
```

### Combined Context and Plural: _nx()

```php
$message = sprintf(
    _nx(
        '%d comment',           // Singular
        '%d comments',          // Plural
        $count,                 // Number
        'comment count',        // Context
        'my-plugin'             // Text domain
    ),
    $count
);
```

### Escaped Versions with Context

```php
// esc_html_x() - escaped with context
echo '<p>' . esc_html_x( 'Read', 'past tense', 'my-plugin' ) . '</p>';

// esc_attr_x() - for attributes with context
echo '<input value="' . esc_attr_x( 'Post', 'verb', 'my-plugin' ) . '">';
```

## Function Reference

| Function | Returns/Echoes | Escaped | Context | Plural |
|----------|----------------|---------|---------|--------|
| `__()` | Returns | No | No | No |
| `_e()` | Echoes | No | No | No |
| `_x()` | Returns | No | Yes | No |
| `_ex()` | Echoes | No | Yes | No |
| `_n()` | Returns | No | No | Yes |
| `_nx()` | Returns | No | Yes | Yes |
| `esc_html__()` | Returns | HTML | No | No |
| `esc_html_e()` | Echoes | HTML | No | No |
| `esc_html_x()` | Returns | HTML | Yes | No |
| `esc_attr__()` | Returns | Attr | No | No |
| `esc_attr_e()` | Echoes | Attr | No | No |
| `esc_attr_x()` | Returns | Attr | Yes | No |

## Translator Comments

Help translators understand context:

```php
// translators: %s is the user's name
$welcome = sprintf( __( 'Welcome back, %s!', 'my-plugin' ), $user_name );

// translators: %1$s is the date, %2$s is the time
$message = sprintf(
    __( 'Published on %1$s at %2$s', 'my-plugin' ),
    $date,
    $time
);

// translators: This appears on the settings page header
__( 'Configuration', 'my-plugin' );
```

The comment must be on the line immediately before the translation function.

## JavaScript Translations

### Registering Script Translations

```php
add_action( 'wp_enqueue_scripts', 'my_plugin_scripts' );

function my_plugin_scripts() {
    wp_enqueue_script(
        'my-plugin-script',
        plugin_dir_url( __FILE__ ) . 'js/script.js',
        array(),
        '1.0.0',
        true
    );

    // Register translations for this script
    wp_set_script_translations(
        'my-plugin-script',  // Script handle
        'my-plugin',         // Text domain
        plugin_dir_path( __FILE__ ) . 'languages'  // Path to translations
    );
}
```

### Using Translations in JavaScript

```javascript
// Import from @wordpress/i18n
import { __, _n, _x, sprintf } from '@wordpress/i18n';

// Simple translation
const text = __( 'Hello World', 'my-plugin' );

// With placeholder
const message = sprintf(
    __( 'Hello, %s!', 'my-plugin' ),
    userName
);

// Plural
const items = sprintf(
    _n(
        '%d item selected',
        '%d items selected',
        count,
        'my-plugin'
    ),
    count
);

// With context
const label = _x( 'Post', 'noun', 'my-plugin' );
```

### Building JavaScript with Translations

When using `@wordpress/scripts`:

```bash
# Build extracts strings to languages/my-plugin-script.pot
npm run build
```

JSON translation files for JavaScript:
```
languages/
├── my-plugin-fr_FR-my-plugin-script.json  # French JS translations
├── my-plugin-de_DE-my-plugin-script.json  # German JS translations
└── my-plugin.pot                           # PHP template
```

## Creating POT Files

### Using WP-CLI

```bash
# Generate POT file from plugin
wp i18n make-pot wp-content/plugins/my-plugin languages/my-plugin.pot

# With specific headers
wp i18n make-pot wp-content/plugins/my-plugin languages/my-plugin.pot \
    --headers='{"Report-Msgid-Bugs-To":"https://example.com/support"}'

# Include JavaScript
wp i18n make-pot wp-content/plugins/my-plugin languages/my-plugin.pot \
    --include="*.php,*.js"
```

### POT File Structure

```
# Copyright (C) 2024 Author Name
# This file is distributed under the GPL-2.0+.
msgid ""
msgstr ""
"Project-Id-Version: My Plugin 1.0.0\n"
"Report-Msgid-Bugs-To: https://example.com\n"
"POT-Creation-Date: 2024-01-15T10:00:00+00:00\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"

#: includes/class-main.php:45
msgid "Settings"
msgstr ""

#: includes/class-main.php:52
#. translators: %s is the plugin name
msgid "Welcome to %s"
msgstr ""

#: includes/class-main.php:60
msgid "item"
msgid_plural "items"
msgstr[0] ""
msgstr[1] ""
```

## Translation Workflow

### 1. Write Translatable Code

```php
// Use translation functions for all user-facing strings
function display_message() {
    echo '<h1>' . esc_html__( 'Welcome', 'my-plugin' ) . '</h1>';
    echo '<p>' . esc_html__( 'Thank you for using our plugin.', 'my-plugin' ) . '</p>';
}
```

### 2. Generate POT File

```bash
wp i18n make-pot . languages/my-plugin.pot
```

### 3. Create PO Files for Each Language

Using Poedit or similar tool:
1. Open POT file
2. Create new translation
3. Select language (e.g., French - fr_FR)
4. Translate strings
5. Save as `my-plugin-fr_FR.po`

### 4. Compile MO Files

```bash
# WP-CLI
wp i18n make-mo languages/my-plugin-fr_FR.po

# Or Poedit does this automatically on save
```

### 5. Create JSON for JavaScript (if needed)

```bash
wp i18n make-json languages/my-plugin-fr_FR.po --no-purge
```

## Best Practices

### Do

```php
// DO: Use complete sentences
__( 'No items found', 'my-plugin' );

// DO: Include punctuation
__( 'Are you sure?', 'my-plugin' );

// DO: Use placeholders for variables
sprintf( __( 'Hello, %s!', 'my-plugin' ), $name );

// DO: Keep HTML outside translation
echo '<strong>' . esc_html__( 'Important', 'my-plugin' ) . '</strong>';

// DO: Add context for ambiguous words
_x( 'Order', 'sorting order', 'my-plugin' );
_x( 'Order', 'purchase order', 'my-plugin' );
```

### Don't

```php
// DON'T: Concatenate sentences
__( 'You have ', 'my-plugin' ) . $count . __( ' messages', 'my-plugin' );
// FIX: sprintf( __( 'You have %d messages', 'my-plugin' ), $count );

// DON'T: Translate HTML
__( '<strong>Warning!</strong>', 'my-plugin' );
// FIX: '<strong>' . esc_html__( 'Warning!', 'my-plugin' ) . '</strong>';

// DON'T: Use variables in translation function
__( $dynamic_string, 'my-plugin' );  // Can't be extracted!
// FIX: Use a switch or predefined strings

// DON'T: Forget the text domain
__( 'Hello' );  // Wrong!
__( 'Hello', 'my-plugin' );  // Correct

// DON'T: Use text domain variable
__( 'Hello', $domain );  // Can't be extracted!
__( 'Hello', MY_PLUGIN_DOMAIN );  // Can't be extracted!
```

### Variables in Strings

```php
// WRONG: Breaks extraction
$action = 'delete';
__( "Are you sure you want to $action this?", 'my-plugin' );

// CORRECT: Use predefined strings
$messages = array(
    'delete' => __( 'Are you sure you want to delete this?', 'my-plugin' ),
    'publish' => __( 'Are you sure you want to publish this?', 'my-plugin' ),
);
echo $messages[ $action ];

// CORRECT: Use placeholders
sprintf(
    __( 'Are you sure you want to %s this?', 'my-plugin' ),
    $action_label  // This is also translated elsewhere
);
```

## Common Patterns

### Date and Number Formatting

```php
// Use WordPress date/number functions - they respect locale
$formatted_date = date_i18n( get_option( 'date_format' ), $timestamp );
$formatted_number = number_format_i18n( $number, 2 );

// Currency (need custom handling)
$price = sprintf(
    __( '%s %s', 'my-plugin' ),  // Allows reordering
    number_format_i18n( $amount, 2 ),
    esc_html( $currency )
);
```

### Messages with Links

```php
// Keep HTML out, use placeholders
printf(
    /* translators: %s is a link to documentation */
    esc_html__( 'Learn more in our %s.', 'my-plugin' ),
    '<a href="https://example.com/docs">' . esc_html__( 'documentation', 'my-plugin' ) . '</a>'
);

// For complex HTML, use wp_kses
$allowed = array( 'a' => array( 'href' => array() ) );
echo wp_kses(
    sprintf(
        __( 'Visit <a href="%s">our website</a> for more info.', 'my-plugin' ),
        'https://example.com'
    ),
    $allowed
);
```

### Admin Notices

```php
function my_plugin_admin_notice() {
    ?>
    <div class="notice notice-success">
        <p><?php esc_html_e( 'Settings saved successfully.', 'my-plugin' ); ?></p>
    </div>
    <?php
}
```

## Plugin Header Translation

```php
/**
 * Plugin Name: My Awesome Plugin
 * Plugin URI: https://example.com/my-plugin
 * Description: This plugin does amazing things.
 * Version: 1.0.0
 * Author: Your Name
 * Author URI: https://example.com
 * Text Domain: my-awesome-plugin
 * Domain Path: /languages
 * License: GPL-2.0+
 */

// These can be translated using translate.wordpress.org
// or by adding:
// * Title of the plugin: My Awesome Plugin
// * Description of the plugin: This plugin does amazing things.
```

## RTL Support

For right-to-left languages (Arabic, Hebrew, etc.):

```php
// Check if current language is RTL
if ( is_rtl() ) {
    wp_enqueue_style( 'my-plugin-rtl', plugin_dir_url( __FILE__ ) . 'css/rtl.css' );
}
```

```css
/* style.css - base styles */
.sidebar { float: left; margin-right: 20px; }

/* rtl.css - RTL overrides */
.sidebar { float: right; margin-right: 0; margin-left: 20px; }
```

Or use logical properties:

```css
/* Modern CSS - works for both LTR and RTL */
.sidebar {
    float: inline-start;
    margin-inline-end: 20px;
}
```

## Further Reading

- [Plugin Structure](./01-plugin-structure.md) - Where to put translation files
- [WordPress Plugin Internationalization](https://developer.wordpress.org/plugins/internationalization/) - Official guide
- [Poedit](https://poedit.net/) - Translation editor
- [GlotPress](https://glotpress.org/) - WordPress.org translation platform
