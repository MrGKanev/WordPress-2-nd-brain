# Settings API

Every non-trivial plugin needs a settings page. WordPress provides a structured API for this—`register_setting()`, `add_settings_section()`, `add_settings_field()`. It handles sanitization, nonce verification, and option storage automatically. The alternative—building forms from scratch with `$_POST` handling—is more code, more bugs, and more security surface.

## When to Use the Settings API

| Approach | Use When |
|----------|----------|
| **Settings API** | Standard plugin options, admin pages |
| **Customizer API** | Theme-related visual settings with live preview |
| **Options stored directly** | Simple single-value options set programmatically |
| **Custom admin page with REST API** | React-based modern settings UI |

For most plugins, the Settings API is the right choice. It's boring, it works, and WordPress handles the plumbing.

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│              Settings Page                   │
│                                              │
│  ┌─ Section: General ─────────────────────┐  │
│  │  Field: Site Title        [________]   │  │
│  │  Field: Enable Feature    [✓]          │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌─ Section: Advanced ────────────────────┐  │
│  │  Field: API Key           [________]   │  │
│  │  Field: Cache TTL         [________]   │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  [Save Changes]                              │
└─────────────────────────────────────────────┘
```

The hierarchy:
1. **Menu page** — Where the settings page lives in the admin menu
2. **Settings group** — Ties options to a page (used in `settings_fields()`)
3. **Sections** — Visual groupings within the page
4. **Fields** — Individual inputs within sections

## Basic Implementation

### Step 1: Register the Menu Page

```php
add_action( 'admin_menu', 'myplugin_add_settings_page' );

function myplugin_add_settings_page() {
    add_options_page(
        'My Plugin Settings',     // Page title
        'My Plugin',              // Menu title
        'manage_options',         // Capability required
        'myplugin-settings',      // Menu slug
        'myplugin_render_settings_page' // Callback
    );
}
```

**Menu location options:**

| Function | Location | Best For |
|----------|----------|----------|
| `add_options_page()` | Settings submenu | Simple utility plugins |
| `add_management_page()` | Tools submenu | Import/export tools |
| `add_menu_page()` | Top-level menu | Complex plugins (WooCommerce, Yoast) |
| `add_submenu_page()` | Under any existing menu | Extending existing sections |

Most plugins should use `add_options_page()`. Reserve top-level menus for plugins that genuinely need multiple pages.

### Step 2: Register Settings, Sections, and Fields

```php
add_action( 'admin_init', 'myplugin_register_settings' );

function myplugin_register_settings() {
    // Register the setting (option name in wp_options)
    register_setting(
        'myplugin_settings_group',   // Option group
        'myplugin_options',          // Option name
        array(
            'type'              => 'array',
            'sanitize_callback' => 'myplugin_sanitize_options',
            'default'           => array(
                'enable_feature' => false,
                'api_key'        => '',
                'cache_ttl'      => 3600,
            ),
        )
    );

    // Add a section
    add_settings_section(
        'myplugin_general_section',      // Section ID
        'General Settings',              // Title
        'myplugin_general_section_cb',   // Description callback
        'myplugin-settings'              // Page slug (must match menu slug)
    );

    // Add fields to the section
    add_settings_field(
        'myplugin_enable_feature',       // Field ID
        'Enable Feature',                // Label
        'myplugin_enable_feature_cb',    // Render callback
        'myplugin-settings',             // Page slug
        'myplugin_general_section'       // Section ID
    );

    add_settings_field(
        'myplugin_api_key',
        'API Key',
        'myplugin_api_key_cb',
        'myplugin-settings',
        'myplugin_general_section'
    );
}
```

### Step 3: Render Callbacks

```php
// Section description
function myplugin_general_section_cb() {
    echo '<p>Configure the main plugin behavior.</p>';
}

// Checkbox field
function myplugin_enable_feature_cb() {
    $options = get_option( 'myplugin_options' );
    $checked = ! empty( $options['enable_feature'] );
    ?>
    <label>
        <input type="checkbox"
               name="myplugin_options[enable_feature]"
               value="1"
               <?php checked( $checked ); ?>>
        Activate the main feature
    </label>
    <?php
}

// Text field
function myplugin_api_key_cb() {
    $options = get_option( 'myplugin_options' );
    $value   = $options['api_key'] ?? '';
    ?>
    <input type="text"
           name="myplugin_options[api_key]"
           value="<?php echo esc_attr( $value ); ?>"
           class="regular-text">
    <p class="description">Enter your API key from the dashboard.</p>
    <?php
}
```

### Step 4: Render the Settings Page

```php
function myplugin_render_settings_page() {
    // Check permissions
    if ( ! current_user_can( 'manage_options' ) ) {
        return;
    }
    ?>
    <div class="wrap">
        <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>

        <?php settings_errors(); ?>

        <form action="options.php" method="post">
            <?php
            settings_fields( 'myplugin_settings_group' );
            do_settings_sections( 'myplugin-settings' );
            submit_button();
            ?>
        </form>
    </div>
    <?php
}
```

**Critical:** The form must POST to `options.php`. WordPress handles the save, nonce verification, and redirect automatically. Don't try to handle `$_POST` yourself.

## Sanitization

The sanitize callback receives the entire options array and must return a clean version:

```php
function myplugin_sanitize_options( $input ) {
    $sanitized = array();

    // Boolean: force true/false
    $sanitized['enable_feature'] = ! empty( $input['enable_feature'] );

    // String: sanitize text
    $sanitized['api_key'] = sanitize_text_field( $input['api_key'] ?? '' );

    // Integer: force range
    $sanitized['cache_ttl'] = absint( $input['cache_ttl'] ?? 3600 );
    $sanitized['cache_ttl'] = max( 60, min( 86400, $sanitized['cache_ttl'] ) );

    // URL: validate format
    $sanitized['webhook_url'] = esc_url_raw( $input['webhook_url'] ?? '' );

    // Select: validate against allowed values
    $allowed_modes = array( 'basic', 'advanced', 'expert' );
    $sanitized['mode'] = in_array( $input['mode'] ?? '', $allowed_modes, true )
        ? $input['mode']
        : 'basic';

    return $sanitized;
}
```

| Data Type | Sanitization | Example |
|-----------|-------------|---------|
| Checkbox | `! empty()` | True/false |
| Text | `sanitize_text_field()` | API keys, names |
| Textarea | `sanitize_textarea_field()` | Descriptions |
| URL | `esc_url_raw()` | Webhook URLs |
| Email | `sanitize_email()` | Notification addresses |
| Number | `absint()` or `intval()` | Counts, TTLs |
| Select/Radio | Validate against allowed list | Mode selection |
| HTML | `wp_kses_post()` | Rich text content |

## Tabbed Settings Pages

For plugins with many options, tabs keep things organized:

```php
function myplugin_render_settings_page() {
    if ( ! current_user_can( 'manage_options' ) ) {
        return;
    }

    $active_tab = $_GET['tab'] ?? 'general';
    ?>
    <div class="wrap">
        <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>

        <nav class="nav-tab-wrapper">
            <a href="?page=myplugin-settings&tab=general"
               class="nav-tab <?php echo $active_tab === 'general' ? 'nav-tab-active' : ''; ?>">
                General
            </a>
            <a href="?page=myplugin-settings&tab=advanced"
               class="nav-tab <?php echo $active_tab === 'advanced' ? 'nav-tab-active' : ''; ?>">
                Advanced
            </a>
        </nav>

        <?php settings_errors(); ?>

        <form action="options.php" method="post">
            <?php
            settings_fields( 'myplugin_settings_group' );

            if ( $active_tab === 'general' ) {
                do_settings_sections( 'myplugin-settings-general' );
            } else {
                do_settings_sections( 'myplugin-settings-advanced' );
            }

            submit_button();
            ?>
        </form>
    </div>
    <?php
}
```

Register sections on different page slugs (`myplugin-settings-general`, `myplugin-settings-advanced`) to separate which fields appear on which tab.

## OOP Approach

For larger plugins, wrap settings in a class:

```php
class MyPlugin_Settings {

    private string $option_name = 'myplugin_options';
    private string $page_slug   = 'myplugin-settings';

    public function __construct() {
        add_action( 'admin_menu', array( $this, 'add_page' ) );
        add_action( 'admin_init', array( $this, 'register' ) );
    }

    public function add_page(): void {
        add_options_page(
            'My Plugin',
            'My Plugin',
            'manage_options',
            $this->page_slug,
            array( $this, 'render' )
        );
    }

    public function register(): void {
        register_setting( 'myplugin_group', $this->option_name, array(
            'sanitize_callback' => array( $this, 'sanitize' ),
            'default'           => $this->defaults(),
        ) );

        // Register sections and fields...
    }

    public function defaults(): array {
        return array(
            'enable_feature' => false,
            'api_key'        => '',
            'cache_ttl'      => 3600,
        );
    }

    public function get( string $key ) {
        $options = get_option( $this->option_name, $this->defaults() );
        return $options[ $key ] ?? $this->defaults()[ $key ] ?? null;
    }

    public function sanitize( array $input ): array {
        // Sanitization logic...
        return $sanitized;
    }

    public function render(): void {
        // Page rendering...
    }
}

// Initialize
new MyPlugin_Settings();
```

The `get()` helper method is useful throughout the plugin—call `$settings->get( 'api_key' )` instead of manually fetching and parsing options everywhere.

## Common Field Types

### Select Dropdown

```php
function myplugin_mode_cb() {
    $options = get_option( 'myplugin_options' );
    $current = $options['mode'] ?? 'basic';
    ?>
    <select name="myplugin_options[mode]">
        <option value="basic" <?php selected( $current, 'basic' ); ?>>Basic</option>
        <option value="advanced" <?php selected( $current, 'advanced' ); ?>>Advanced</option>
        <option value="expert" <?php selected( $current, 'expert' ); ?>>Expert</option>
    </select>
    <?php
}
```

### Number with Range

```php
function myplugin_cache_ttl_cb() {
    $options = get_option( 'myplugin_options' );
    $value   = $options['cache_ttl'] ?? 3600;
    ?>
    <input type="number"
           name="myplugin_options[cache_ttl]"
           value="<?php echo absint( $value ); ?>"
           min="60" max="86400" step="60"
           class="small-text">
    <span>seconds (60–86400)</span>
    <?php
}
```

### Textarea

```php
function myplugin_custom_css_cb() {
    $options = get_option( 'myplugin_options' );
    $value   = $options['custom_css'] ?? '';
    ?>
    <textarea name="myplugin_options[custom_css]"
              rows="8" cols="50"
              class="large-text code"><?php echo esc_textarea( $value ); ?></textarea>
    <p class="description">Custom CSS applied to the frontend.</p>
    <?php
}
```

### Color Picker

```php
// Enqueue the color picker
add_action( 'admin_enqueue_scripts', function( $hook ) {
    if ( $hook !== 'settings_page_myplugin-settings' ) {
        return;
    }
    wp_enqueue_style( 'wp-color-picker' );
    wp_enqueue_script( 'wp-color-picker' );
    wp_add_inline_script( 'wp-color-picker', "
        jQuery(document).ready(function($) {
            $('.myplugin-color-picker').wpColorPicker();
        });
    " );
} );

function myplugin_accent_color_cb() {
    $options = get_option( 'myplugin_options' );
    $value   = $options['accent_color'] ?? '#0073aa';
    ?>
    <input type="text"
           name="myplugin_options[accent_color]"
           value="<?php echo esc_attr( $value ); ?>"
           class="myplugin-color-picker">
    <?php
}
```

## Common Mistakes

**Forgetting to store unchecked checkboxes.** Browsers don't send unchecked checkboxes in POST data. Your sanitize callback must handle missing keys:

```php
// WRONG: checkbox disappears if unchecked, old value persists
$sanitized['feature'] = sanitize_text_field( $input['feature'] );

// RIGHT: explicitly set false when missing
$sanitized['feature'] = ! empty( $input['feature'] );
```

**Using wrong option group name.** If `settings_fields()` uses a different group than `register_setting()`, the form silently fails. Triple-check these match.

**Loading settings on every request.** Call `get_option()` only when needed, not at init. Options with `autoload` enabled are loaded automatically, but parsing large arrays on every request wastes cycles.

**Not setting defaults.** Always provide defaults in `register_setting()` and in your getter. A fresh installation should work without saving settings first.

## WordPress.org Compliance

If submitting to the plugin directory:

- Don't add top-level menus unless your plugin has multiple pages
- Use `manage_options` capability for admin settings
- Don't load settings page assets globally—check `$hook` first
- Include a link from the Plugins list to your settings page:

```php
add_filter( 'plugin_action_links_' . plugin_basename( __FILE__ ), function( $links ) {
    $settings_link = '<a href="options-general.php?page=myplugin-settings">Settings</a>';
    array_unshift( $links, $settings_link );
    return $links;
} );
```

## Further Reading

- [Plugin Structure](./01-plugin-structure.md) — File organization for settings classes
- [Database Operations](./03-database-operations.md) — Options API deep dive
- [Input Sanitization & Output Escaping](../03-security/03-data-validation.md) — Sanitization functions reference
- [WordPress Settings API Handbook](https://developer.wordpress.org/plugins/settings/settings-api/)
