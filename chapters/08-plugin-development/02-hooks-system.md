# WordPress Hooks System

## Overview

The hooks system is the backbone of WordPress extensibility. It allows plugins and themes to modify WordPress behavior without editing core files. Understanding hooks deeply is essential for any serious WordPress development.

> **Key concept**: Hooks are points in WordPress code where you can insert your own code. They make WordPress infinitely customizable while maintaining upgrade compatibility.

## Types of Hooks

WordPress has two types of hooks:

| Type | Purpose | Return Value | Use Case |
|------|---------|--------------|----------|
| **Actions** | Execute code at specific points | None (void) | Send emails, save data, enqueue scripts |
| **Filters** | Modify data before it's used | Modified data | Change content, alter queries, modify options |

**The simplest way to remember:** Actions are for *doing* things (send email, create file, log something). Filters are for *changing* things (modify text, alter a value, transform data). If you're wondering which to use: Does the hook pass you data that you need to return? It's a filter. Does it just announce "this is happening now"? It's an action.

### Actions

Actions let you add functionality at specific execution points:

```php
// Basic action hook usage
add_action('init', 'my_custom_function');

function my_custom_function() {
    // This runs when WordPress initializes
    register_post_type('book', array(
        'public' => true,
        'label'  => 'Books'
    ));
}

// Anonymous function (closure) - PHP 5.3+
add_action('wp_footer', function() {
    echo '<!-- Custom footer content -->';
});
```

### Filters

Filters intercept and modify data:

```php
// Basic filter hook usage
add_filter('the_content', 'add_reading_time');

function add_reading_time($content) {
    if (is_single()) {
        $word_count = str_word_count(strip_tags($content));
        $reading_time = ceil($word_count / 200); // 200 words per minute
        $reading_time_text = '<p class="reading-time">Reading time: ' . $reading_time . ' min</p>';
        return $reading_time_text . $content;
    }
    return $content;
}

// Filter with multiple parameters
add_filter('post_thumbnail_html', 'modify_thumbnail', 10, 5);

function modify_thumbnail($html, $post_id, $thumbnail_id, $size, $attr) {
    // Add loading="lazy" to all thumbnails
    return str_replace('<img', '<img loading="lazy"', $html);
}
```

## Hook Execution Flow

Understanding when hooks fire is crucial:

```
WordPress Request Lifecycle (Simplified):
┌─────────────────────────────────────────────────────────────┐
│ 1. muplugins_loaded  - After must-use plugins load         │
│ 2. plugins_loaded    - After all plugins load              │
│ 3. setup_theme       - Before theme loads                  │
│ 4. after_setup_theme - After theme's functions.php loads   │
│ 5. init              - WordPress fully initialized         │
│ 6. wp_loaded         - After WordPress, plugins, themes    │
│ 7. template_redirect - Before template is chosen           │
│ 8. wp_head           - In <head> section                   │
│ 9. the_content       - When post content is displayed      │
│ 10. wp_footer        - Before </body>                      │
│ 11. shutdown         - PHP execution ends                  │
└─────────────────────────────────────────────────────────────┘
```

### Admin-Specific Hooks

```
Admin Request Lifecycle:
┌─────────────────────────────────────────────────────────────┐
│ 1. admin_init        - Admin area initialized              │
│ 2. admin_menu        - Admin menu is being built           │
│ 3. admin_enqueue_scripts - Enqueue admin CSS/JS            │
│ 4. current_screen    - Current admin screen determined     │
│ 5. admin_notices     - Display admin notices               │
│ 6. admin_footer      - Admin footer area                   │
└─────────────────────────────────────────────────────────────┘
```

## Priority and Parameters

### Priority

Priority determines execution order (lower = earlier):

```php
// Default priority is 10
add_action('init', 'runs_second');           // Priority 10
add_action('init', 'runs_first', 5);         // Priority 5
add_action('init', 'runs_last', 99);         // Priority 99

// Use cases:
// - Low priority (1-9): Must run before other plugins
// - Default (10): Normal operations
// - High priority (11-99): Run after other plugins, cleanup
// - Very high (100+): Guaranteed last execution
```

### Accepted Arguments

Specify how many arguments your callback receives:

```php
// Filter with multiple arguments
add_filter('wp_insert_post_data', 'modify_post_data', 10, 2);

function modify_post_data($data, $postarr) {
    // $data: sanitized post data
    // $postarr: raw post data from $_POST

    // Auto-generate excerpt if empty
    if (empty($data['post_excerpt']) && !empty($data['post_content'])) {
        $data['post_excerpt'] = wp_trim_words($data['post_content'], 30);
    }

    return $data;
}

// Action with multiple arguments
add_action('save_post', 'on_save_post', 10, 3);

function on_save_post($post_id, $post, $update) {
    // $post_id: ID of the post
    // $post: WP_Post object
    // $update: true if updating, false if new

    if ($update && $post->post_type === 'product') {
        // Clear product cache on update
        wp_cache_delete('product_' . $post_id, 'products');
    }
}
```

## Removing Hooks

### Basic Removal

```php
// Remove a named function
remove_action('wp_head', 'wp_generator');

// Must match exact priority
remove_action('wp_head', 'some_function', 15); // Only works if added with priority 15

// Remove all callbacks from a hook
remove_all_actions('wp_head');
```

### Removing Class Methods

Removing hooks added by classes requires a reference to the same instance:

```php
// This is a common pain point - you need the exact object instance
class SomePlugin {
    public function __construct() {
        add_action('init', array($this, 'init_method'));
    }

    public function init_method() {
        // ...
    }
}

// To remove, you need access to the same instance:
global $some_plugin;
$some_plugin = new SomePlugin();

// Later, to remove:
global $some_plugin;
remove_action('init', array($some_plugin, 'init_method'));
```

### Removing Anonymous Functions

Anonymous functions cannot be removed - avoid them for hooks that others might need to unhook:

```php
// BAD - Cannot be removed
add_action('init', function() {
    // This can never be unhooked
});

// GOOD - Can be removed
add_action('init', 'my_init_function');
function my_init_function() {
    // This can be unhooked later
}
```

## Essential Hooks Reference

### Content Hooks

```php
// Modify post content
add_filter('the_content', 'modify_content');

// Modify post title
add_filter('the_title', 'modify_title', 10, 2);

// Modify excerpt
add_filter('the_excerpt', 'custom_excerpt');
add_filter('excerpt_length', function() { return 30; });
add_filter('excerpt_more', function() { return '...'; });
```

### Query Hooks

```php
// Modify main query (NEVER use on admin)
add_action('pre_get_posts', 'modify_main_query');

function modify_main_query($query) {
    // Only modify main query on frontend
    if (!is_admin() && $query->is_main_query()) {

        // Exclude category from blog
        if ($query->is_home()) {
            $query->set('cat', '-5'); // Exclude category ID 5
        }

        // Custom post type archive ordering
        if ($query->is_post_type_archive('event')) {
            $query->set('orderby', 'meta_value');
            $query->set('meta_key', 'event_date');
            $query->set('order', 'ASC');
        }
    }
}
```

### User Hooks

```php
// After user logs in
add_action('wp_login', 'after_login', 10, 2);

function after_login($user_login, $user) {
    update_user_meta($user->ID, 'last_login', current_time('mysql'));
}

// Before user is created
add_filter('pre_user_login', 'sanitize_username');

// After user registers
add_action('user_register', 'on_user_register');
```

### Script/Style Hooks

```php
// Frontend scripts
add_action('wp_enqueue_scripts', 'enqueue_frontend_assets');

function enqueue_frontend_assets() {
    wp_enqueue_style('main', get_stylesheet_uri(), array(), '1.0.0');
    wp_enqueue_script('main', get_template_directory_uri() . '/js/main.js', array('jquery'), '1.0.0', true);

    // Localize script (pass PHP data to JS)
    wp_localize_script('main', 'myAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce'   => wp_create_nonce('my_nonce')
    ));
}

// Admin scripts
add_action('admin_enqueue_scripts', 'enqueue_admin_assets');

function enqueue_admin_assets($hook) {
    // Only load on specific admin page
    if ($hook !== 'toplevel_page_my-plugin') {
        return;
    }

    wp_enqueue_script('my-admin-script', plugin_dir_url(__FILE__) . 'admin.js');
}
```

### REST API Hooks

```php
// Register custom REST route
add_action('rest_api_init', 'register_custom_routes');

function register_custom_routes() {
    register_rest_route('myplugin/v1', '/data', array(
        'methods'  => 'GET',
        'callback' => 'get_custom_data',
        'permission_callback' => function() {
            return current_user_can('read');
        }
    ));
}

// Modify REST response
add_filter('rest_prepare_post', 'add_custom_field_to_rest', 10, 3);

function add_custom_field_to_rest($response, $post, $request) {
    $response->data['reading_time'] = get_post_meta($post->ID, 'reading_time', true);
    return $response;
}
```

## Creating Custom Hooks

Allow other developers to extend your plugin:

```php
// Creating an action hook
function my_plugin_process_order($order_id) {
    $order = get_order($order_id);

    // Let other plugins do something before processing
    do_action('my_plugin_before_order_process', $order);

    // Process the order
    $result = process_order($order);

    // Let other plugins do something after processing
    do_action('my_plugin_after_order_process', $order, $result);

    return $result;
}

// Creating a filter hook
function my_plugin_get_price($product_id) {
    $price = get_post_meta($product_id, '_price', true);

    // Allow other plugins to modify the price
    $price = apply_filters('my_plugin_product_price', $price, $product_id);

    return $price;
}

// Usage by other plugins:
add_action('my_plugin_before_order_process', function($order) {
    // Log order before processing
    error_log('Processing order: ' . $order->id);
});

add_filter('my_plugin_product_price', function($price, $product_id) {
    // Apply 10% discount for logged-in users
    if (is_user_logged_in()) {
        return $price * 0.9;
    }
    return $price;
}, 10, 2);
```

## Performance Considerations

### Hook Overhead

Each hook has minimal overhead, but it adds up:

```php
// Check if anyone is hooked before expensive operations
if (has_action('my_expensive_hook')) {
    do_action('my_expensive_hook', $expensive_data);
}

// Same for filters
if (has_filter('my_filter')) {
    $data = apply_filters('my_filter', $data);
}
```

### Avoid Repeated Hook Calls

```php
// BAD - Filter called on every iteration
foreach ($posts as $post) {
    $content = apply_filters('my_content_filter', $post->content);
}

// GOOD - Check once, apply if needed
$has_filter = has_filter('my_content_filter');
foreach ($posts as $post) {
    $content = $has_filter
        ? apply_filters('my_content_filter', $post->content)
        : $post->content;
}
```

### Early Returns

```php
// Return early when conditions aren't met
add_action('save_post', 'my_save_handler', 10, 2);

function my_save_handler($post_id, $post) {
    // Quick checks first
    if (wp_is_post_autosave($post_id)) return;
    if (wp_is_post_revision($post_id)) return;
    if ($post->post_type !== 'product') return;
    if (!current_user_can('edit_post', $post_id)) return;

    // Now do the actual work
    update_post_meta($post_id, '_processed', true);
}
```

## Debugging Hooks

### Finding Attached Callbacks

```php
// List all callbacks for a hook
function list_hook_callbacks($hook_name) {
    global $wp_filter;

    if (!isset($wp_filter[$hook_name])) {
        return 'No callbacks attached';
    }

    $callbacks = array();
    foreach ($wp_filter[$hook_name]->callbacks as $priority => $functions) {
        foreach ($functions as $function) {
            $callbacks[] = array(
                'priority' => $priority,
                'callback' => print_r($function['function'], true)
            );
        }
    }

    return $callbacks;
}

// Usage:
print_r(list_hook_callbacks('the_content'));
```

### Tracking Hook Execution

```php
// Debug hook timing (development only)
function debug_hook_timing($hook_name) {
    add_action($hook_name, function() use ($hook_name) {
        static $start_time;

        if (!isset($start_time)) {
            $start_time = microtime(true);
            error_log("HOOK START: {$hook_name}");
        } else {
            $elapsed = microtime(true) - $start_time;
            error_log("HOOK END: {$hook_name} ({$elapsed}s)");
        }
    }, -9999); // Very early

    add_action($hook_name, function() use ($hook_name) {
        // This runs last
    }, 9999);
}
```

### Query Monitor Plugin

For serious debugging, use the Query Monitor plugin which shows:
- All hooks that fired
- Time spent in each hook
- Which callbacks are attached
- Memory usage per hook

## Best Practices

### Naming Conventions

```php
// Prefix your hooks with plugin/theme name
do_action('myplugin_before_save');
apply_filters('myplugin_default_options', $defaults);

// Use descriptive names
do_action('myplugin_order_status_changed', $order_id, $old_status, $new_status);
```

### Documentation

```php
/**
 * Fires before an order is processed.
 *
 * @since 1.0.0
 *
 * @param WC_Order $order The order object being processed.
 * @param array    $data  Additional order data.
 */
do_action('myplugin_before_order_process', $order, $data);

/**
 * Filters the product price before display.
 *
 * @since 1.0.0
 *
 * @param float $price      The current price.
 * @param int   $product_id The product ID.
 * @return float Modified price.
 */
$price = apply_filters('myplugin_product_price', $price, $product_id);
```

### Conditional Loading

```php
// Only add hooks when needed
if (is_admin()) {
    add_action('admin_menu', 'add_admin_pages');
    add_action('admin_init', 'register_settings');
} else {
    add_action('wp_enqueue_scripts', 'enqueue_frontend');
}

// Load AJAX handlers only for AJAX requests
if (wp_doing_ajax()) {
    add_action('wp_ajax_my_action', 'handle_ajax');
    add_action('wp_ajax_nopriv_my_action', 'handle_ajax');
}
```

## Common Mistakes

### Forgetting to Return in Filters

```php
// BAD - Destroys the content!
add_filter('the_content', function($content) {
    // Do something
    // Forgot to return!
});

// GOOD
add_filter('the_content', function($content) {
    // Do something
    return $content; // Always return!
});
```

### Using Wrong Hook Timing

```php
// BAD - Too late to register post type
add_action('wp_loaded', 'register_my_post_type');

// GOOD - Correct hook for post types
add_action('init', 'register_my_post_type');

// BAD - Too early for rewrite rules
add_action('plugins_loaded', 'add_rewrite_rules');

// GOOD - After init
add_action('init', 'add_rewrite_rules');
```

### Modifying Global State Without Restoring

```php
// BAD - Permanently changes query
add_action('pre_get_posts', function($query) {
    $query->set('posts_per_page', 5);
});

// GOOD - Only modify main query on frontend
add_action('pre_get_posts', function($query) {
    if (!is_admin() && $query->is_main_query() && $query->is_home()) {
        $query->set('posts_per_page', 5);
    }
});
```

## Further Reading

For database operations using hooks, see [Database Operations](./03-database-operations.md).

For plugin structure and how to organize hooks, see [Plugin Structure](./01-plugin-structure.md).
