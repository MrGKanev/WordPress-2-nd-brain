# WordPress REST API

## Overview

The WordPress REST API provides a standardized way to interact with WordPress using HTTP requests. It powers the block editor, enables headless WordPress, and lets external applications communicate with your site.

Understanding the REST API is essential for modern WordPress development - whether building custom endpoints for plugins or consuming WordPress data from external applications.

## REST API Basics

### Default Endpoints

WordPress exposes content through `/wp-json/wp/v2/`:

```bash
# List posts
GET /wp-json/wp/v2/posts

# Get single post
GET /wp-json/wp/v2/posts/123

# List pages
GET /wp-json/wp/v2/pages

# Get current user
GET /wp-json/wp/v2/users/me

# List categories
GET /wp-json/wp/v2/categories
```

### Testing with cURL

```bash
# Get posts
curl https://example.com/wp-json/wp/v2/posts

# Get posts with authentication (Application Password)
curl -u "username:xxxx xxxx xxxx xxxx xxxx xxxx" \
     https://example.com/wp-json/wp/v2/posts

# Create a post
curl -X POST \
     -u "username:xxxx xxxx xxxx xxxx xxxx xxxx" \
     -H "Content-Type: application/json" \
     -d '{"title":"New Post","content":"Post content","status":"publish"}' \
     https://example.com/wp-json/wp/v2/posts
```

### Discovering the API

```bash
# Root endpoint shows all available routes
GET /wp-json/

# Namespace shows routes within namespace
GET /wp-json/wp/v2
```

## Registering Custom Endpoints

### Basic Endpoint

```php
add_action( 'rest_api_init', 'register_my_routes' );

function register_my_routes() {
    register_rest_route( 'myplugin/v1', '/items', array(
        'methods'             => 'GET',
        'callback'            => 'get_items_callback',
        'permission_callback' => '__return_true', // Public endpoint
    ) );
}

function get_items_callback( $request ) {
    $items = array(
        array( 'id' => 1, 'name' => 'Item One' ),
        array( 'id' => 2, 'name' => 'Item Two' ),
    );

    return rest_ensure_response( $items );
}
```

### Route with Parameters

```php
register_rest_route( 'myplugin/v1', '/items/(?P<id>\d+)', array(
    'methods'             => 'GET',
    'callback'            => 'get_single_item',
    'permission_callback' => '__return_true',
    'args'                => array(
        'id' => array(
            'required'          => true,
            'validate_callback' => function( $param ) {
                return is_numeric( $param );
            },
            'sanitize_callback' => 'absint',
        ),
    ),
) );

function get_single_item( $request ) {
    $id = $request['id'];

    // Fetch item...
    $item = get_item_by_id( $id );

    if ( ! $item ) {
        return new WP_Error(
            'not_found',
            __( 'Item not found', 'myplugin' ),
            array( 'status' => 404 )
        );
    }

    return rest_ensure_response( $item );
}
```

### Multiple Methods on One Route

```php
register_rest_route( 'myplugin/v1', '/items/(?P<id>\d+)', array(
    // GET - Read
    array(
        'methods'             => WP_REST_Server::READABLE,
        'callback'            => 'get_item',
        'permission_callback' => '__return_true',
    ),
    // POST/PUT - Update
    array(
        'methods'             => WP_REST_Server::EDITABLE,
        'callback'            => 'update_item',
        'permission_callback' => 'can_edit_items',
    ),
    // DELETE - Remove
    array(
        'methods'             => WP_REST_Server::DELETABLE,
        'callback'            => 'delete_item',
        'permission_callback' => 'can_delete_items',
    ),
) );
```

### Method Constants

| Constant | Methods | Use For |
|----------|---------|---------|
| `WP_REST_Server::READABLE` | GET | Retrieving data |
| `WP_REST_Server::CREATABLE` | POST | Creating new items |
| `WP_REST_Server::EDITABLE` | POST, PUT, PATCH | Updating items |
| `WP_REST_Server::DELETABLE` | DELETE | Removing items |
| `WP_REST_Server::ALLMETHODS` | All | Any operation |

## Authentication

### Permission Callbacks

Every endpoint needs a permission callback:

```php
// Public endpoint - anyone can access
'permission_callback' => '__return_true',

// Logged-in users only
'permission_callback' => 'is_user_logged_in',

// Specific capability
'permission_callback' => function() {
    return current_user_can( 'edit_posts' );
},

// Custom logic
'permission_callback' => function( $request ) {
    $post_id = $request['id'];
    return current_user_can( 'edit_post', $post_id );
},
```

### Authentication Methods

**Cookie Authentication (same-site requests):**
```javascript
// Nonce passed with request
fetch('/wp-json/myplugin/v1/items', {
    headers: {
        'X-WP-Nonce': wpApiSettings.nonce
    }
});
```

**Application Passwords (WordPress 5.6+):**
```bash
# Generated in Users → Profile → Application Passwords
curl -u "username:xxxx xxxx xxxx xxxx xxxx xxxx" \
     https://example.com/wp-json/wp/v2/posts
```

```php
// PHP with Application Password
$response = wp_remote_get( 'https://example.com/wp-json/wp/v2/posts', array(
    'headers' => array(
        'Authorization' => 'Basic ' . base64_encode( 'username:app-password' ),
    ),
) );
```

**JWT (requires plugin):**
```javascript
// After obtaining token
fetch('/wp-json/myplugin/v1/items', {
    headers: {
        'Authorization': 'Bearer ' + jwtToken
    }
});
```

### Nonce for JavaScript

```php
// Enqueue and localize
add_action( 'wp_enqueue_scripts', function() {
    wp_enqueue_script( 'my-api-script', '...', array(), '1.0', true );

    wp_localize_script( 'my-api-script', 'myApi', array(
        'root'  => esc_url_raw( rest_url() ),
        'nonce' => wp_create_nonce( 'wp_rest' ),
    ) );
} );
```

```javascript
// Use in JavaScript
fetch(myApi.root + 'myplugin/v1/items', {
    headers: {
        'X-WP-Nonce': myApi.nonce,
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Request and Response

### Working with WP_REST_Request

```php
function my_callback( WP_REST_Request $request ) {
    // Get URL parameters
    $id = $request['id'];                    // From route pattern
    $id = $request->get_param( 'id' );       // Same thing

    // Get query parameters (?page=2)
    $page = $request->get_param( 'page' );

    // Get body (POST/PUT)
    $body = $request->get_body();            // Raw body
    $json = $request->get_json_params();     // Parsed JSON
    $params = $request->get_params();        // All params

    // Get specific body param
    $title = $request->get_param( 'title' );

    // Get headers
    $auth = $request->get_header( 'authorization' );

    // Get files (multipart)
    $files = $request->get_file_params();

    // Get HTTP method
    $method = $request->get_method();
}
```

### Building Responses

```php
// Simple response (auto-wrapped)
return array( 'id' => 1, 'name' => 'Item' );

// Explicit response object
return rest_ensure_response( $data );

// With status code
$response = new WP_REST_Response( $data, 201 );
return $response;

// With headers
$response = new WP_REST_Response( $data );
$response->header( 'X-Custom-Header', 'value' );
return $response;

// Error response
return new WP_Error(
    'error_code',
    __( 'Error message', 'textdomain' ),
    array( 'status' => 400 )
);
```

### Pagination

```php
function get_items_paginated( $request ) {
    $page     = $request->get_param( 'page' ) ?: 1;
    $per_page = $request->get_param( 'per_page' ) ?: 10;

    $query = new WP_Query( array(
        'post_type'      => 'item',
        'posts_per_page' => $per_page,
        'paged'          => $page,
    ) );

    $items = array();
    foreach ( $query->posts as $post ) {
        $items[] = prepare_item_for_response( $post );
    }

    $response = rest_ensure_response( $items );

    // Add pagination headers
    $response->header( 'X-WP-Total', $query->found_posts );
    $response->header( 'X-WP-TotalPages', $query->max_num_pages );

    return $response;
}

// Register with pagination args
register_rest_route( 'myplugin/v1', '/items', array(
    'methods'  => 'GET',
    'callback' => 'get_items_paginated',
    'args'     => array(
        'page'     => array(
            'default'           => 1,
            'sanitize_callback' => 'absint',
        ),
        'per_page' => array(
            'default'           => 10,
            'sanitize_callback' => 'absint',
            'validate_callback' => function( $value ) {
                return $value <= 100; // Max 100 per page
            },
        ),
    ),
) );
```

## Argument Validation

### Schema-Based Validation

```php
register_rest_route( 'myplugin/v1', '/items', array(
    'methods'  => 'POST',
    'callback' => 'create_item',
    'args'     => array(
        'title' => array(
            'required'          => true,
            'type'              => 'string',
            'description'       => __( 'Item title', 'myplugin' ),
            'sanitize_callback' => 'sanitize_text_field',
            'validate_callback' => function( $value ) {
                return strlen( $value ) >= 3;
            },
        ),
        'status' => array(
            'required' => false,
            'type'     => 'string',
            'default'  => 'draft',
            'enum'     => array( 'draft', 'publish', 'private' ),
        ),
        'price' => array(
            'required' => true,
            'type'     => 'number',
            'minimum'  => 0,
        ),
        'tags' => array(
            'type'  => 'array',
            'items' => array(
                'type' => 'integer',
            ),
        ),
    ),
) );
```

### Custom Validation

```php
'args' => array(
    'email' => array(
        'required'          => true,
        'validate_callback' => function( $value, $request, $key ) {
            if ( ! is_email( $value ) ) {
                return new WP_Error(
                    'invalid_email',
                    __( 'Invalid email address', 'myplugin' )
                );
            }
            return true;
        },
        'sanitize_callback' => 'sanitize_email',
    ),
    'date' => array(
        'validate_callback' => function( $value ) {
            $date = DateTime::createFromFormat( 'Y-m-d', $value );
            return $date && $date->format( 'Y-m-d' ) === $value;
        },
    ),
),
```

## Extending Default Endpoints

### Adding Fields to Posts

```php
add_action( 'rest_api_init', 'add_custom_rest_fields' );

function add_custom_rest_fields() {
    register_rest_field( 'post', 'reading_time', array(
        'get_callback' => function( $post ) {
            $content   = get_post_field( 'post_content', $post['id'] );
            $word_count = str_word_count( strip_tags( $content ) );
            return ceil( $word_count / 200 );
        },
        'schema' => array(
            'description' => __( 'Estimated reading time in minutes', 'myplugin' ),
            'type'        => 'integer',
        ),
    ) );

    // Writable field
    register_rest_field( 'post', 'custom_field', array(
        'get_callback' => function( $post ) {
            return get_post_meta( $post['id'], 'custom_field', true );
        },
        'update_callback' => function( $value, $post ) {
            update_post_meta( $post->ID, 'custom_field', sanitize_text_field( $value ) );
        },
        'schema' => array(
            'type' => 'string',
        ),
    ) );
}
```

### Modifying Response Data

```php
// Add data to all post responses
add_filter( 'rest_prepare_post', 'modify_post_response', 10, 3 );

function modify_post_response( $response, $post, $request ) {
    // Add featured image URL
    $response->data['featured_image_url'] = get_the_post_thumbnail_url( $post->ID, 'full' );

    // Add author details
    $author = get_userdata( $post->post_author );
    $response->data['author_name'] = $author->display_name;

    return $response;
}
```

### Modifying Query Parameters

```php
// Allow filtering posts by custom meta
add_filter( 'rest_post_query', 'modify_post_query', 10, 2 );

function modify_post_query( $args, $request ) {
    if ( isset( $request['featured'] ) && $request['featured'] ) {
        $args['meta_query'] = array(
            array(
                'key'   => 'is_featured',
                'value' => '1',
            ),
        );
    }

    return $args;
}
```

## REST API for Custom Post Types

CPTs registered with `show_in_rest` get automatic endpoints:

```php
register_post_type( 'event', array(
    'public'       => true,
    'show_in_rest' => true,
    'rest_base'    => 'events',           // /wp-json/wp/v2/events
    'rest_controller_class' => 'WP_REST_Posts_Controller',
    'supports'     => array( 'title', 'editor', 'custom-fields' ),
) );
```

### Custom Controller

For complex CPTs, create a custom controller:

```php
class My_Events_Controller extends WP_REST_Posts_Controller {

    public function __construct() {
        parent::__construct( 'event' );
        $this->namespace = 'myplugin/v1';
        $this->rest_base = 'events';
    }

    // Override to add custom fields to response
    public function prepare_item_for_response( $post, $request ) {
        $response = parent::prepare_item_for_response( $post, $request );

        // Add event-specific data
        $response->data['event_date']     = get_post_meta( $post->ID, '_event_date', true );
        $response->data['event_location'] = get_post_meta( $post->ID, '_event_location', true );

        return $response;
    }

    // Override to handle custom fields on create/update
    protected function prepare_item_for_database( $request ) {
        $prepared = parent::prepare_item_for_database( $request );

        // Additional meta will be saved via rest_after_insert_event hook
        return $prepared;
    }
}

// Use custom controller
register_post_type( 'event', array(
    'show_in_rest'          => true,
    'rest_controller_class' => 'My_Events_Controller',
) );
```

## Error Handling

### Returning Errors

```php
function my_callback( $request ) {
    $id = $request['id'];

    // Not found
    if ( ! item_exists( $id ) ) {
        return new WP_Error(
            'rest_item_not_found',
            __( 'Item not found.', 'myplugin' ),
            array( 'status' => 404 )
        );
    }

    // Validation error
    if ( ! is_valid_item( $id ) ) {
        return new WP_Error(
            'rest_invalid_item',
            __( 'Invalid item data.', 'myplugin' ),
            array( 'status' => 400 )
        );
    }

    // Server error
    $result = process_item( $id );
    if ( false === $result ) {
        return new WP_Error(
            'rest_processing_failed',
            __( 'Failed to process item.', 'myplugin' ),
            array( 'status' => 500 )
        );
    }

    return rest_ensure_response( $result );
}
```

### HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (new resource) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Authenticated but not permitted |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Something went wrong server-side |

## Caching REST Responses

```php
function get_items_cached( $request ) {
    $cache_key = 'rest_items_' . md5( serialize( $request->get_params() ) );
    $items     = get_transient( $cache_key );

    if ( false === $items ) {
        $items = fetch_items_from_database();
        set_transient( $cache_key, $items, HOUR_IN_SECONDS );
    }

    $response = rest_ensure_response( $items );

    // Set cache headers for CDN/browser
    $response->header( 'Cache-Control', 'max-age=3600' );

    return $response;
}

// Invalidate on data change
add_action( 'save_post_item', function( $post_id ) {
    delete_transient( 'rest_items_' . md5( serialize( array() ) ) );
} );
```

## JavaScript Consumption

### Using Fetch

```javascript
// GET request
async function getItems() {
    const response = await fetch('/wp-json/myplugin/v1/items', {
        headers: {
            'X-WP-Nonce': myApi.nonce
        }
    });
    return response.json();
}

// POST request
async function createItem(data) {
    const response = await fetch('/wp-json/myplugin/v1/items', {
        method: 'POST',
        headers: {
            'X-WP-Nonce': myApi.nonce,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
    }

    return response.json();
}

// DELETE request
async function deleteItem(id) {
    const response = await fetch(`/wp-json/myplugin/v1/items/${id}`, {
        method: 'DELETE',
        headers: {
            'X-WP-Nonce': myApi.nonce
        }
    });
    return response.ok;
}
```

### Using wp.apiFetch (Block Editor)

```javascript
import apiFetch from '@wordpress/api-fetch';

// GET
const items = await apiFetch({ path: '/myplugin/v1/items' });

// POST
const newItem = await apiFetch({
    path: '/myplugin/v1/items',
    method: 'POST',
    data: { title: 'New Item', status: 'publish' }
});

// With URL parameters
const filtered = await apiFetch({
    path: '/myplugin/v1/items',
    params: { page: 2, per_page: 10 }
});
```

## Complete Example

```php
<?php
/**
 * REST API endpoint for managing bookmarks
 */

class Bookmarks_REST_Controller extends WP_REST_Controller {

    protected $namespace = 'myplugin/v1';
    protected $rest_base = 'bookmarks';

    public function register_routes() {
        // GET /bookmarks - List all
        register_rest_route( $this->namespace, '/' . $this->rest_base, array(
            array(
                'methods'             => WP_REST_Server::READABLE,
                'callback'            => array( $this, 'get_items' ),
                'permission_callback' => array( $this, 'get_items_permissions_check' ),
                'args'                => $this->get_collection_params(),
            ),
            // POST /bookmarks - Create new
            array(
                'methods'             => WP_REST_Server::CREATABLE,
                'callback'            => array( $this, 'create_item' ),
                'permission_callback' => array( $this, 'create_item_permissions_check' ),
                'args'                => $this->get_endpoint_args_for_item_schema( true ),
            ),
        ) );

        // Single item routes
        register_rest_route( $this->namespace, '/' . $this->rest_base . '/(?P<id>[\d]+)', array(
            array(
                'methods'             => WP_REST_Server::READABLE,
                'callback'            => array( $this, 'get_item' ),
                'permission_callback' => array( $this, 'get_item_permissions_check' ),
            ),
            array(
                'methods'             => WP_REST_Server::DELETABLE,
                'callback'            => array( $this, 'delete_item' ),
                'permission_callback' => array( $this, 'delete_item_permissions_check' ),
            ),
        ) );
    }

    public function get_items_permissions_check( $request ) {
        return is_user_logged_in();
    }

    public function get_items( $request ) {
        $user_id = get_current_user_id();

        $bookmarks = get_user_meta( $user_id, 'bookmarks', true ) ?: array();

        return rest_ensure_response( $bookmarks );
    }

    public function create_item_permissions_check( $request ) {
        return is_user_logged_in();
    }

    public function create_item( $request ) {
        $user_id  = get_current_user_id();
        $post_id  = $request->get_param( 'post_id' );

        if ( ! get_post( $post_id ) ) {
            return new WP_Error(
                'invalid_post',
                __( 'Post not found', 'myplugin' ),
                array( 'status' => 404 )
            );
        }

        $bookmarks   = get_user_meta( $user_id, 'bookmarks', true ) ?: array();
        $bookmarks[] = absint( $post_id );
        $bookmarks   = array_unique( $bookmarks );

        update_user_meta( $user_id, 'bookmarks', $bookmarks );

        return rest_ensure_response( array(
            'id'      => $post_id,
            'message' => __( 'Bookmark added', 'myplugin' ),
        ) );
    }

    public function delete_item_permissions_check( $request ) {
        return is_user_logged_in();
    }

    public function delete_item( $request ) {
        $user_id = get_current_user_id();
        $post_id = absint( $request['id'] );

        $bookmarks = get_user_meta( $user_id, 'bookmarks', true ) ?: array();
        $bookmarks = array_diff( $bookmarks, array( $post_id ) );

        update_user_meta( $user_id, 'bookmarks', array_values( $bookmarks ) );

        return rest_ensure_response( array(
            'deleted' => true,
            'id'      => $post_id,
        ) );
    }

    public function get_item_schema() {
        return array(
            '$schema'    => 'http://json-schema.org/draft-04/schema#',
            'title'      => 'bookmark',
            'type'       => 'object',
            'properties' => array(
                'id' => array(
                    'description' => __( 'Bookmark ID', 'myplugin' ),
                    'type'        => 'integer',
                    'readonly'    => true,
                ),
                'post_id' => array(
                    'description' => __( 'Post ID to bookmark', 'myplugin' ),
                    'type'        => 'integer',
                    'required'    => true,
                ),
            ),
        );
    }
}

// Initialize
add_action( 'rest_api_init', function() {
    $controller = new Bookmarks_REST_Controller();
    $controller->register_routes();
} );
```

## Further Reading

- [AJAX Patterns](./05-ajax-patterns.md) - When to use AJAX vs REST
- [Input Sanitization & Output Escaping](../03-security/03-data-validation.md) - Securing API inputs
- [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/) - Official documentation
- [REST API Authentication](https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/) - Official auth guide
