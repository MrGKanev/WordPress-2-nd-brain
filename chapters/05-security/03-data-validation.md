# Input Sanitization & Output Escaping

## Overview

The most common security vulnerabilities in WordPress plugins come from improper handling of user data. Understanding when to sanitize input and when to escape output is fundamental to writing secure code.

**The golden rule:** Never trust user input. Ever.

## The Two-Step Protection Model

Data security in WordPress follows a simple principle:

```
User Input → SANITIZE → Store in Database → ESCAPE → Display to User
             (clean)                        (safe)
```

| Step | When | Purpose |
|------|------|---------|
| **Sanitization** | When receiving data | Clean and normalize input before storage |
| **Escaping** | When displaying data | Prevent code execution in output context |

Both are necessary. Sanitization alone doesn't prevent XSS. Escaping alone doesn't prevent bad data storage.

## Input Sanitization

Sanitization cleans data before you use or store it. WordPress provides functions for common data types.

### Text Sanitization Functions

```php
// sanitize_text_field() - General text, strips tags and encodes special characters
$title = sanitize_text_field( $_POST['title'] );
// Input:  "<script>alert('xss')</script>Hello"
// Output: "Hello"

// sanitize_textarea_field() - Preserves line breaks, otherwise like text_field
$description = sanitize_textarea_field( $_POST['description'] );
// Input:  "Line 1\nLine 2<script>bad</script>"
// Output: "Line 1\nLine 2"

// sanitize_title() - Creates slug-safe strings
$slug = sanitize_title( $_POST['post_title'] );
// Input:  "My Amazing Post!"
// Output: "my-amazing-post"

// sanitize_file_name() - Safe for filesystem operations
$filename = sanitize_file_name( $_FILES['upload']['name'] );
// Input:  "../../../etc/passwd"
// Output: "etc-passwd"

// sanitize_html_class() - Valid CSS class names
$class = sanitize_html_class( $_POST['custom_class'] );
// Input:  "my-class<script>"
// Output: "my-classscript"

// sanitize_key() - Lowercase alphanumeric with dashes/underscores
$key = sanitize_key( $_POST['option_name'] );
// Input:  "My Option Name!"
// Output: "my_option_name"
```

### Specific Data Type Sanitization

```php
// sanitize_email() - Valid email or empty string
$email = sanitize_email( $_POST['email'] );
// Input:  "test<script>@example.com"
// Output: "test@example.com"

// sanitize_url() - Alias for esc_url_raw(), for database storage
$url = sanitize_url( $_POST['website'] );
// Input:  "javascript:alert(1)"
// Output: ""

// absint() - Absolute integer (non-negative)
$post_id = absint( $_GET['post_id'] );
// Input:  "-5" or "5abc"
// Output: 5

// intval() - Integer, can be negative
$offset = intval( $_GET['offset'] );
// Input:  "-10"
// Output: -10

// floatval() - Floating point number
$price = floatval( $_POST['price'] );
// Input:  "19.99abc"
// Output: 19.99
```

### HTML Sanitization with wp_kses

When you need to allow some HTML but not all:

```php
// wp_kses_post() - Allows HTML valid in posts (most formatting tags)
$content = wp_kses_post( $_POST['content'] );
// Allows: <p>, <a>, <strong>, <em>, <img>, etc.
// Strips: <script>, <iframe>, <form>, event handlers

// wp_kses() - Custom allowed tags
$allowed = array(
    'a' => array(
        'href'  => array(),
        'title' => array(),
        'class' => array(),
    ),
    'strong' => array(),
    'em'     => array(),
);
$content = wp_kses( $_POST['bio'], $allowed );
// Only allows <a>, <strong>, <em> with specified attributes

// wp_kses_data() - Very restrictive, for data attributes
$data = wp_kses_data( $_POST['data'] );
```

### When to Use Which Function

| Data Type | Function | Example Use Case |
|-----------|----------|------------------|
| Plain text | `sanitize_text_field()` | Titles, names, single-line input |
| Multiline text | `sanitize_textarea_field()` | Descriptions, addresses |
| Email | `sanitize_email()` | Contact forms, user registration |
| URL | `sanitize_url()` | Website fields, links |
| Integer ID | `absint()` | Post IDs, user IDs |
| Integer (any) | `intval()` | Pagination, offsets |
| Slug | `sanitize_title()` | Custom slugs, URL-safe strings |
| HTML content | `wp_kses_post()` | WYSIWYG editor content |
| Limited HTML | `wp_kses()` | Comment-like content |
| Filename | `sanitize_file_name()` | Upload handling |
| Array | `array_map()` + sanitizer | Multiple values |

### Sanitizing Arrays

```php
// Single level array
$ids = array_map( 'absint', $_POST['selected_ids'] );

// Array of strings
$tags = array_map( 'sanitize_text_field', $_POST['tags'] );

// Associative array
$data = array(
    'title'   => sanitize_text_field( $_POST['data']['title'] ),
    'content' => wp_kses_post( $_POST['data']['content'] ),
    'email'   => sanitize_email( $_POST['data']['email'] ),
);
```

## Output Escaping

Escaping converts special characters so they're displayed as text, not executed as code. Different output contexts require different escaping functions.

### Why Context Matters

The same data needs different escaping depending on where it appears:

```php
$user_input = '"><script>alert("xss")</script>';

// In HTML context - different escapes for different places
echo '<div>' . esc_html( $user_input ) . '</div>';
echo '<input value="' . esc_attr( $user_input ) . '">';
echo '<a href="' . esc_url( $url_input ) . '">Link</a>';
```

### HTML Context Functions

```php
// esc_html() - For displaying in HTML body
echo '<p>' . esc_html( $text ) . '</p>';
// Converts: < > & " ' to HTML entities

// esc_attr() - For HTML attributes
echo '<input value="' . esc_attr( $value ) . '">';
// Same as esc_html, but safe for attribute context

// esc_textarea() - For textarea content
echo '<textarea>' . esc_textarea( $content ) . '</textarea>';
// Handles textarea-specific encoding
```

### URL Functions

```php
// esc_url() - For href, src, and other URL attributes
echo '<a href="' . esc_url( $link ) . '">Click</a>';
echo '<img src="' . esc_url( $image_url ) . '">';
// Validates URL structure, removes dangerous protocols

// esc_url_raw() - For database storage (doesn't encode ampersands)
$url_for_db = esc_url_raw( $input_url );
// Use this when storing, esc_url() when displaying
```

### JavaScript Context

```php
// esc_js() - For inline JavaScript strings
echo '<button onclick="alert(\'' . esc_js( $message ) . '\')">';
// Escapes quotes and special JS characters

// wp_json_encode() - For passing data to JavaScript
echo '<script>var data = ' . wp_json_encode( $array ) . ';</script>';
// Properly encodes arrays/objects for JS
```

### Translation Functions with Escaping

WordPress provides combined translation + escaping functions:

```php
// esc_html__() - Translate and escape for HTML
echo '<p>' . esc_html__( 'Welcome message', 'textdomain' ) . '</p>';

// esc_html_e() - Same, but echoes directly
esc_html_e( 'Submit', 'textdomain' );

// esc_attr__() - Translate and escape for attributes
echo '<input placeholder="' . esc_attr__( 'Enter name', 'textdomain' ) . '">';

// esc_attr_e() - Same, but echoes directly
echo '<input value="'; esc_attr_e( 'Save', 'textdomain' ); echo '">';
```

### Escaping Quick Reference

| Context | Function | Example |
|---------|----------|---------|
| HTML body | `esc_html()` | `<p><?php echo esc_html( $text ); ?></p>` |
| HTML attribute | `esc_attr()` | `<input value="<?php echo esc_attr( $val ); ?>">` |
| URL (href, src) | `esc_url()` | `<a href="<?php echo esc_url( $url ); ?>">` |
| Textarea content | `esc_textarea()` | `<textarea><?php echo esc_textarea( $content ); ?></textarea>` |
| Inline JavaScript | `esc_js()` | `onclick="fn('<?php echo esc_js( $str ); ?>')"` |
| JSON data | `wp_json_encode()` | `<script>var x = <?php echo wp_json_encode( $data ); ?>;</script>` |

## Database Security: Prepared Statements

Never interpolate variables directly into SQL queries. Always use `$wpdb->prepare()`.

### The Problem

```php
// DANGEROUS - SQL Injection vulnerability
$id = $_GET['id'];
$results = $wpdb->get_results( "SELECT * FROM {$wpdb->posts} WHERE ID = $id" );
// Attacker input: "1 OR 1=1" returns all posts
// Attacker input: "1; DROP TABLE wp_posts" deletes everything
```

### The Solution: $wpdb->prepare()

```php
// SAFE - Prepared statement
$id = absint( $_GET['id'] );
$results = $wpdb->get_results(
    $wpdb->prepare(
        "SELECT * FROM {$wpdb->posts} WHERE ID = %d",
        $id
    )
);
```

### Placeholder Types

| Placeholder | Type | Example |
|-------------|------|---------|
| `%d` | Integer | IDs, counts, boolean (0/1) |
| `%f` | Float | Prices, coordinates |
| `%s` | String | Names, content, any text |

### Common Patterns

```php
// Single value
$post = $wpdb->get_row(
    $wpdb->prepare(
        "SELECT * FROM {$wpdb->posts} WHERE ID = %d",
        $post_id
    )
);

// Multiple values
$posts = $wpdb->get_results(
    $wpdb->prepare(
        "SELECT * FROM {$wpdb->posts} WHERE post_author = %d AND post_status = %s",
        $author_id,
        'publish'
    )
);

// LIKE queries - escape wildcards properly
$search = '%' . $wpdb->esc_like( $search_term ) . '%';
$results = $wpdb->get_results(
    $wpdb->prepare(
        "SELECT * FROM {$wpdb->posts} WHERE post_title LIKE %s",
        $search
    )
);

// IN clause with multiple values
$ids = array( 1, 2, 3, 4, 5 );
$placeholders = implode( ', ', array_fill( 0, count( $ids ), '%d' ) );
$results = $wpdb->get_results(
    $wpdb->prepare(
        "SELECT * FROM {$wpdb->posts} WHERE ID IN ($placeholders)",
        $ids
    )
);
```

### When Using WP_Query

`WP_Query` and related functions handle sanitization internally:

```php
// Safe - WP_Query sanitizes internally
$query = new WP_Query( array(
    'post_type'   => sanitize_key( $_GET['type'] ),  // Still sanitize for validation
    'post_status' => 'publish',
    'meta_query'  => array(
        array(
            'key'   => 'color',
            'value' => sanitize_text_field( $_GET['color'] ),
        ),
    ),
) );

// Use $wpdb->prepare() only for custom SQL, not WP_Query
```

## Real-World Examples

### Vulnerable Code vs. Secure Code

**Example 1: Search Form (XSS)**

```php
// VULNERABLE - Reflects user input without escaping
<input type="text" value="<?php echo $_GET['s']; ?>">

// SECURE - Escapes output
<input type="text" value="<?php echo esc_attr( $_GET['s'] ); ?>">
```

**Example 2: Admin Settings (SQL Injection)**

```php
// VULNERABLE - Direct concatenation
function get_item( $id ) {
    global $wpdb;
    return $wpdb->get_row( "SELECT * FROM {$wpdb->prefix}items WHERE id = $id" );
}

// SECURE - Prepared statement
function get_item( $id ) {
    global $wpdb;
    return $wpdb->get_row(
        $wpdb->prepare(
            "SELECT * FROM {$wpdb->prefix}items WHERE id = %d",
            absint( $id )
        )
    );
}
```

**Example 3: AJAX Handler (Multiple Vulnerabilities)**

```php
// VULNERABLE
add_action( 'wp_ajax_save_data', 'save_data' );
function save_data() {
    global $wpdb;
    $wpdb->insert(
        $wpdb->prefix . 'data',
        array(
            'title'   => $_POST['title'],        // No sanitization
            'content' => $_POST['content'],      // No sanitization
        )
    );
    echo $_POST['title'] . ' saved!';            // No escaping
    wp_die();
}

// SECURE
add_action( 'wp_ajax_save_data', 'save_data' );
function save_data() {
    // Verify nonce
    check_ajax_referer( 'save_data_nonce', 'nonce' );

    // Check capabilities
    if ( ! current_user_can( 'edit_posts' ) ) {
        wp_send_json_error( 'Unauthorized' );
    }

    global $wpdb;

    // Sanitize input
    $title   = sanitize_text_field( $_POST['title'] );
    $content = wp_kses_post( $_POST['content'] );

    $wpdb->insert(
        $wpdb->prefix . 'data',
        array(
            'title'   => $title,
            'content' => $content,
        ),
        array( '%s', '%s' )  // Format specifiers
    );

    // Escape output
    wp_send_json_success( esc_html( $title ) . ' saved!' );
}
```

### Complete Form Handling Example

```php
// Form display
function display_contact_form() {
    // Get previously submitted values (if validation failed)
    $name  = isset( $_POST['contact_name'] ) ? sanitize_text_field( $_POST['contact_name'] ) : '';
    $email = isset( $_POST['contact_email'] ) ? sanitize_email( $_POST['contact_email'] ) : '';

    ?>
    <form method="post" action="">
        <?php wp_nonce_field( 'contact_form', 'contact_nonce' ); ?>

        <label for="contact_name">Name:</label>
        <input type="text"
               id="contact_name"
               name="contact_name"
               value="<?php echo esc_attr( $name ); ?>">

        <label for="contact_email">Email:</label>
        <input type="email"
               id="contact_email"
               name="contact_email"
               value="<?php echo esc_attr( $email ); ?>">

        <button type="submit">Send</button>
    </form>
    <?php
}

// Form processing
function process_contact_form() {
    // Check if form was submitted
    if ( ! isset( $_POST['contact_nonce'] ) ) {
        return;
    }

    // Verify nonce
    if ( ! wp_verify_nonce( $_POST['contact_nonce'], 'contact_form' ) ) {
        wp_die( 'Security check failed' );
    }

    // Sanitize all inputs
    $name    = sanitize_text_field( $_POST['contact_name'] );
    $email   = sanitize_email( $_POST['contact_email'] );
    $message = sanitize_textarea_field( $_POST['contact_message'] );

    // Validate
    $errors = array();

    if ( empty( $name ) ) {
        $errors[] = 'Name is required';
    }

    if ( ! is_email( $email ) ) {
        $errors[] = 'Valid email is required';
    }

    if ( ! empty( $errors ) ) {
        // Display errors (escaped)
        foreach ( $errors as $error ) {
            echo '<p class="error">' . esc_html( $error ) . '</p>';
        }
        return;
    }

    // Process the valid, sanitized data
    wp_mail(
        get_option( 'admin_email' ),
        'Contact Form: ' . $name,
        $message,
        array( 'Reply-To: ' . $email )
    );

    echo '<p class="success">' . esc_html__( 'Message sent!', 'textdomain' ) . '</p>';
}
add_action( 'init', 'process_contact_form' );
```

## Security Checklist

When handling user data:

- [ ] **Verify nonce** for all form submissions and AJAX requests
- [ ] **Check capabilities** - does user have permission for this action?
- [ ] **Sanitize all input** immediately when receiving it
- [ ] **Validate data** - is the email actually an email? Is the ID actually numeric?
- [ ] **Use prepared statements** for any custom SQL queries
- [ ] **Escape all output** using the appropriate function for the context
- [ ] **Use type casting** (`absint()`, `(bool)`) for expected data types

## Common Mistakes

**Escaping when storing, not when displaying:**
```php
// WRONG - escaping before storage
update_post_meta( $id, 'key', esc_html( $value ) );
// Now stored data has HTML entities, will double-escape on display

// RIGHT - sanitize for storage, escape for display
update_post_meta( $id, 'key', sanitize_text_field( $value ) );
echo esc_html( get_post_meta( $id, 'key', true ) );
```

**Using esc_html() for URLs:**
```php
// WRONG - esc_html doesn't validate URL protocol
echo '<a href="' . esc_html( $url ) . '">';
// Allows: javascript:alert(1)

// RIGHT - esc_url validates and sanitizes URLs
echo '<a href="' . esc_url( $url ) . '">';
```

**Trusting data from the database:**
```php
// WRONG - assuming database data is safe
echo '<p>' . get_post_meta( $id, 'custom_field', true ) . '</p>';
// If attacker got data into DB, this executes it

// RIGHT - always escape output regardless of source
echo '<p>' . esc_html( get_post_meta( $id, 'custom_field', true ) ) . '</p>';
```

## Further Reading

- [Server-Level Hardening](./02-server-hardening.md) - Security beyond code
- [Cloudflare Hardening](./01-cloudflare-hardening.md) - Network-level protection
- [WordPress Plugin Security](https://developer.wordpress.org/plugins/security/) - Official documentation
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) - Industry standards
