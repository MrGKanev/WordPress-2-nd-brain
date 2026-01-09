# AJAX Patterns in WordPress

## Overview

AJAX lets you update parts of a page without reloading. In WordPress, this means communicating with the server through `admin-ajax.php` or the REST API. Understanding WordPress AJAX is essential for any interactive plugin.

## How WordPress AJAX Works

All AJAX requests in WordPress go through `wp-admin/admin-ajax.php`:

```
Browser → POST to admin-ajax.php → WordPress loads → Your hook fires → JSON response
```

The `action` parameter determines which handler runs:

```javascript
// Frontend JavaScript
jQuery.post(ajaxurl, {
    action: 'my_custom_action',  // This determines the PHP handler
    data: 'some value'
});
```

```php
// PHP handler
add_action( 'wp_ajax_my_custom_action', 'handle_my_custom_action' );
```

## Basic AJAX Pattern

### Step 1: Enqueue JavaScript and Pass Data

```php
add_action( 'wp_enqueue_scripts', 'my_plugin_scripts' );

function my_plugin_scripts() {
    wp_enqueue_script(
        'my-plugin-ajax',
        plugin_dir_url( __FILE__ ) . 'js/ajax.js',
        array( 'jquery' ),
        '1.0.0',
        true  // Load in footer
    );

    // Pass data to JavaScript
    wp_localize_script( 'my-plugin-ajax', 'myPluginAjax', array(
        'ajaxurl' => admin_url( 'admin-ajax.php' ),
        'nonce'   => wp_create_nonce( 'my_plugin_nonce' ),
        'i18n'    => array(
            'loading' => __( 'Loading...', 'my-plugin' ),
            'error'   => __( 'An error occurred', 'my-plugin' ),
        ),
    ) );
}
```

### Step 2: Write the JavaScript

```javascript
// js/ajax.js
jQuery(document).ready(function($) {

    $('#my-button').on('click', function(e) {
        e.preventDefault();

        var $button = $(this);
        var $result = $('#result');

        // Show loading state
        $button.prop('disabled', true);
        $result.html(myPluginAjax.i18n.loading);

        $.ajax({
            url: myPluginAjax.ajaxurl,
            type: 'POST',
            data: {
                action: 'my_plugin_action',
                nonce: myPluginAjax.nonce,
                item_id: $button.data('id')
            },
            success: function(response) {
                if (response.success) {
                    $result.html(response.data.message);
                } else {
                    $result.html(response.data.message || myPluginAjax.i18n.error);
                }
            },
            error: function() {
                $result.html(myPluginAjax.i18n.error);
            },
            complete: function() {
                $button.prop('disabled', false);
            }
        });
    });

});
```

### Step 3: Create the PHP Handler

```php
// For logged-in users
add_action( 'wp_ajax_my_plugin_action', 'handle_my_plugin_action' );

// For non-logged-in users (if needed)
add_action( 'wp_ajax_nopriv_my_plugin_action', 'handle_my_plugin_action' );

function handle_my_plugin_action() {
    // 1. Verify nonce
    if ( ! check_ajax_referer( 'my_plugin_nonce', 'nonce', false ) ) {
        wp_send_json_error( array(
            'message' => __( 'Security check failed', 'my-plugin' ),
        ) );
    }

    // 2. Check capabilities (if needed)
    if ( ! current_user_can( 'edit_posts' ) ) {
        wp_send_json_error( array(
            'message' => __( 'You do not have permission', 'my-plugin' ),
        ) );
    }

    // 3. Sanitize input
    $item_id = isset( $_POST['item_id'] ) ? absint( $_POST['item_id'] ) : 0;

    if ( ! $item_id ) {
        wp_send_json_error( array(
            'message' => __( 'Invalid item ID', 'my-plugin' ),
        ) );
    }

    // 4. Do the work
    $result = do_something_with_item( $item_id );

    if ( is_wp_error( $result ) ) {
        wp_send_json_error( array(
            'message' => $result->get_error_message(),
        ) );
    }

    // 5. Return success
    wp_send_json_success( array(
        'message' => __( 'Action completed successfully', 'my-plugin' ),
        'data'    => $result,
    ) );
}
```

## The Two AJAX Hooks

WordPress provides two hooks for each action:

| Hook | When It Fires |
|------|---------------|
| `wp_ajax_{action}` | Only for logged-in users |
| `wp_ajax_nopriv_{action}` | Only for logged-out users |

```php
// Logged-in users only (admin features)
add_action( 'wp_ajax_save_settings', 'save_settings_handler' );

// Both logged-in and logged-out (public features)
add_action( 'wp_ajax_load_posts', 'load_posts_handler' );
add_action( 'wp_ajax_nopriv_load_posts', 'load_posts_handler' );

// Logged-out only (rare, but possible)
add_action( 'wp_ajax_nopriv_guest_action', 'guest_action_handler' );
```

## Security: Nonces

Nonces prevent Cross-Site Request Forgery (CSRF). They verify the request came from your site.

### Creating Nonces

```php
// In PHP (passed to JavaScript)
$nonce = wp_create_nonce( 'my_action_nonce' );

// In a form
wp_nonce_field( 'my_action_nonce', 'my_nonce_field' );

// In a URL
$url = wp_nonce_url( $base_url, 'my_action_nonce', 'my_nonce' );
```

### Verifying Nonces

```php
// In AJAX handler - returns false on failure
if ( ! check_ajax_referer( 'my_action_nonce', 'nonce', false ) ) {
    wp_send_json_error( 'Invalid nonce' );
}

// Or let WordPress handle the die() on failure
check_ajax_referer( 'my_action_nonce', 'nonce' );

// For non-AJAX (returns false or 1/2)
if ( ! wp_verify_nonce( $_POST['my_nonce_field'], 'my_action_nonce' ) ) {
    wp_die( 'Security check failed' );
}
```

### Nonce Lifespan

Nonces are valid for 24 hours (12-24 hours technically, due to time-based generation). For long-running pages:

```php
// Refresh nonce periodically
add_filter( 'heartbeat_received', function( $response ) {
    $response['new_nonce'] = wp_create_nonce( 'my_action_nonce' );
    return $response;
}, 10, 1 );
```

## Response Functions

WordPress provides standard response functions:

```php
// Success response
wp_send_json_success( array(
    'message' => 'It worked!',
    'count'   => 42,
) );
// Output: {"success":true,"data":{"message":"It worked!","count":42}}

// Error response
wp_send_json_error( array(
    'message' => 'Something went wrong',
    'code'    => 'invalid_input',
) );
// Output: {"success":false,"data":{"message":"Something went wrong","code":"invalid_input"}}

// Generic JSON (without success wrapper)
wp_send_json( array( 'key' => 'value' ) );
// Output: {"key":"value"}
```

All three functions:
- Set `Content-Type: application/json`
- Call `wp_die()` automatically
- Are the clean way to end AJAX handlers

## Common AJAX Patterns

### Load More Posts

```javascript
// JavaScript
$('#load-more').on('click', function() {
    var $button = $(this);
    var page = $button.data('page') || 1;

    $.ajax({
        url: myAjax.ajaxurl,
        type: 'POST',
        data: {
            action: 'load_more_posts',
            nonce: myAjax.nonce,
            page: page + 1,
            category: $button.data('category')
        },
        beforeSend: function() {
            $button.text('Loading...');
        },
        success: function(response) {
            if (response.success) {
                $('#posts-container').append(response.data.html);
                $button.data('page', page + 1);

                if (!response.data.has_more) {
                    $button.hide();
                }
            }
        },
        complete: function() {
            $button.text('Load More');
        }
    });
});
```

```php
// PHP handler
add_action( 'wp_ajax_load_more_posts', 'handle_load_more_posts' );
add_action( 'wp_ajax_nopriv_load_more_posts', 'handle_load_more_posts' );

function handle_load_more_posts() {
    check_ajax_referer( 'my_nonce', 'nonce' );

    $page     = isset( $_POST['page'] ) ? absint( $_POST['page'] ) : 1;
    $category = isset( $_POST['category'] ) ? sanitize_text_field( $_POST['category'] ) : '';

    $query = new WP_Query( array(
        'post_type'      => 'post',
        'posts_per_page' => 10,
        'paged'          => $page,
        'category_name'  => $category,
    ) );

    ob_start();
    if ( $query->have_posts() ) {
        while ( $query->have_posts() ) {
            $query->the_post();
            get_template_part( 'template-parts/content', 'excerpt' );
        }
    }
    $html = ob_get_clean();
    wp_reset_postdata();

    wp_send_json_success( array(
        'html'     => $html,
        'has_more' => $page < $query->max_num_pages,
    ) );
}
```

### Form Submission

```javascript
// JavaScript
$('#my-form').on('submit', function(e) {
    e.preventDefault();

    var $form = $(this);
    var $submit = $form.find('[type="submit"]');
    var $message = $form.find('.form-message');

    $.ajax({
        url: myAjax.ajaxurl,
        type: 'POST',
        data: $form.serialize() + '&action=submit_form&nonce=' + myAjax.nonce,
        beforeSend: function() {
            $submit.prop('disabled', true).val('Submitting...');
            $message.removeClass('error success').empty();
        },
        success: function(response) {
            if (response.success) {
                $message.addClass('success').html(response.data.message);
                $form[0].reset();
            } else {
                $message.addClass('error').html(response.data.message);
            }
        },
        error: function() {
            $message.addClass('error').html('Connection error. Please try again.');
        },
        complete: function() {
            $submit.prop('disabled', false).val('Submit');
        }
    });
});
```

```php
// PHP handler
add_action( 'wp_ajax_submit_form', 'handle_form_submission' );
add_action( 'wp_ajax_nopriv_submit_form', 'handle_form_submission' );

function handle_form_submission() {
    check_ajax_referer( 'my_nonce', 'nonce' );

    // Sanitize all fields
    $name    = sanitize_text_field( $_POST['name'] ?? '' );
    $email   = sanitize_email( $_POST['email'] ?? '' );
    $message = sanitize_textarea_field( $_POST['message'] ?? '' );

    // Validate
    $errors = array();

    if ( empty( $name ) ) {
        $errors[] = __( 'Name is required', 'my-plugin' );
    }

    if ( ! is_email( $email ) ) {
        $errors[] = __( 'Valid email is required', 'my-plugin' );
    }

    if ( empty( $message ) ) {
        $errors[] = __( 'Message is required', 'my-plugin' );
    }

    if ( ! empty( $errors ) ) {
        wp_send_json_error( array(
            'message' => implode( '<br>', $errors ),
        ) );
    }

    // Process form...
    $sent = wp_mail(
        get_option( 'admin_email' ),
        sprintf( __( 'Contact from %s', 'my-plugin' ), $name ),
        $message,
        array( 'Reply-To: ' . $email )
    );

    if ( $sent ) {
        wp_send_json_success( array(
            'message' => __( 'Thank you! Your message has been sent.', 'my-plugin' ),
        ) );
    } else {
        wp_send_json_error( array(
            'message' => __( 'Failed to send message. Please try again.', 'my-plugin' ),
        ) );
    }
}
```

### Live Search

```javascript
// JavaScript with debouncing
var searchTimeout;

$('#search-input').on('input', function() {
    var query = $(this).val();
    var $results = $('#search-results');

    clearTimeout(searchTimeout);

    if (query.length < 3) {
        $results.empty();
        return;
    }

    searchTimeout = setTimeout(function() {
        $.ajax({
            url: myAjax.ajaxurl,
            type: 'POST',
            data: {
                action: 'live_search',
                nonce: myAjax.nonce,
                query: query
            },
            beforeSend: function() {
                $results.html('<li>Searching...</li>');
            },
            success: function(response) {
                if (response.success && response.data.results.length) {
                    var html = response.data.results.map(function(item) {
                        return '<li><a href="' + item.url + '">' + item.title + '</a></li>';
                    }).join('');
                    $results.html(html);
                } else {
                    $results.html('<li>No results found</li>');
                }
            }
        });
    }, 300);  // 300ms debounce
});
```

```php
// PHP handler
add_action( 'wp_ajax_live_search', 'handle_live_search' );
add_action( 'wp_ajax_nopriv_live_search', 'handle_live_search' );

function handle_live_search() {
    check_ajax_referer( 'my_nonce', 'nonce' );

    $query = sanitize_text_field( $_POST['query'] ?? '' );

    if ( strlen( $query ) < 3 ) {
        wp_send_json_error();
    }

    $posts = get_posts( array(
        'post_type'      => 'post',
        's'              => $query,
        'posts_per_page' => 10,
    ) );

    $results = array_map( function( $post ) {
        return array(
            'id'    => $post->ID,
            'title' => esc_html( $post->post_title ),
            'url'   => get_permalink( $post ),
        );
    }, $posts );

    wp_send_json_success( array( 'results' => $results ) );
}
```

## AJAX vs REST API

WordPress also has a REST API. When to use which?

| Use AJAX When | Use REST API When |
|---------------|-------------------|
| Simple internal operations | Building a public API |
| Legacy code compatibility | Headless WordPress |
| Quick admin features | Mobile app backend |
| No need for external access | Third-party integrations |

### REST API Equivalent

```php
// Register REST endpoint
add_action( 'rest_api_init', function() {
    register_rest_route( 'my-plugin/v1', '/items/(?P<id>\d+)', array(
        'methods'             => 'GET',
        'callback'            => 'get_item_callback',
        'permission_callback' => function() {
            return current_user_can( 'read' );
        },
        'args'                => array(
            'id' => array(
                'required'          => true,
                'validate_callback' => function( $param ) {
                    return is_numeric( $param );
                },
            ),
        ),
    ) );
} );

function get_item_callback( $request ) {
    $id   = $request['id'];
    $item = get_post( $id );

    if ( ! $item ) {
        return new WP_Error( 'not_found', 'Item not found', array( 'status' => 404 ) );
    }

    return rest_ensure_response( array(
        'id'    => $item->ID,
        'title' => $item->post_title,
    ) );
}
```

```javascript
// JavaScript fetch to REST API
fetch('/wp-json/my-plugin/v1/items/123', {
    headers: {
        'X-WP-Nonce': myPlugin.restNonce
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Debugging AJAX

### In Browser DevTools

1. Open Network tab
2. Filter by "XHR" or "Fetch"
3. Make the AJAX request
4. Click the request to see:
   - Request payload (what was sent)
   - Response (what came back)
   - Headers

### In PHP

```php
function my_ajax_handler() {
    // Log incoming data
    error_log( 'AJAX request: ' . print_r( $_POST, true ) );

    // Your handler code...

    // Log response before sending
    $response = array( 'success' => true, 'data' => $result );
    error_log( 'AJAX response: ' . print_r( $response, true ) );

    wp_send_json( $response );
}
```

### Common Issues

**"0" response:**
- Handler not registered (check hook name matches action)
- Handler doesn't call `wp_send_json_*()` or `wp_die()`

**"-1" response:**
- Nonce verification failed
- Check nonce was passed and matches

**403 Forbidden:**
- Missing `wp_ajax_nopriv_` hook for logged-out users
- Permission callback failing

## Performance Considerations

### Minimize Admin-AJAX Load

Admin-AJAX loads WordPress fully. For simple operations, consider:

```php
// Fast AJAX endpoint (loads minimal WordPress)
// Create: /wp-content/mu-plugins/fast-ajax.php

if ( isset( $_GET['fast-action'] ) && $_GET['fast-action'] === 'heartbeat-light' ) {
    // Only load what's needed
    define( 'SHORTINIT', true );
    require_once dirname( __FILE__ ) . '/../../../wp-load.php';

    // Handle request...
    wp_send_json( array( 'status' => 'ok' ) );
    exit;
}
```

### Batch Requests

Instead of multiple requests:

```javascript
// Bad: Multiple requests
items.forEach(function(item) {
    $.post(ajaxurl, { action: 'process_item', id: item.id });
});

// Good: Single batched request
$.post(ajaxurl, {
    action: 'process_items',
    ids: items.map(item => item.id)
});
```

## Further Reading

- [WordPress Hooks System](./02-hooks-system.md) - Understanding actions and filters
- [Input Sanitization & Output Escaping](../03-security/03-data-validation.md) - Securing AJAX handlers
- [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/) - Official REST API docs
- [AJAX in Plugins](https://developer.wordpress.org/plugins/javascript/ajax/) - Official AJAX documentation
