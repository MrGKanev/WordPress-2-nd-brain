# Plugin Testing

Untested code is code you hope works. Tested code is code you know works. WordPress plugin testing isn't glamorous, but it catches bugs before users do—especially the subtle ones that only appear when WooCommerce is active, or when the site runs PHP 8.2, or when another plugin filters the same hook.

## Testing Levels

| Level | What It Tests | Speed | Complexity |
|-------|---------------|-------|------------|
| **Unit tests** | Individual functions in isolation | Fast | Low |
| **Integration tests** | Functions interacting with WordPress | Medium | Medium |
| **E2E tests** | Full browser-based workflows | Slow | High |

Most plugins need integration tests. Pure unit tests are valuable for utility functions. E2E tests are for critical user-facing workflows (checkout, forms).

## Setting Up PHPUnit for WordPress

### Prerequisites

- A PHP version supported by your target WordPress version, plus every PHP version in your declared support matrix
- `php-xml` and `php-mbstring`
- MySQL/MariaDB (tests use a real database)
- Composer
- WP-CLI (for scaffolding)

### Scaffold Test Files

```bash
# From your plugin directory
wp scaffold plugin-tests myplugin

# This creates:
# phpunit.xml.dist   — PHPUnit configuration
# .phpcs.xml.dist    — Coding standards config
# tests/
#   bootstrap.php    — Test setup
#   test-sample.php  — Example test
# bin/
#   install-wp-tests.sh — Database setup script
```

### Install Test Framework

```bash
# Create test database (uses a SEPARATE database — never your live one)
bash bin/install-wp-tests.sh wordpress_tests root '' localhost latest

# Arguments: db_name db_user db_pass db_host wp_version
```

This downloads WordPress test framework and creates a test database. The test database gets wiped on every run.

### Install PHPUnit via Composer

```json
{
    "require-dev": {
        "phpunit/phpunit": "^9.0",
        "yoast/phpunit-polyfills": "^1.0"
    }
}
```

```bash
composer install
```

### Run Tests

```bash
./vendor/bin/phpunit
```

## Writing Integration Tests

WordPress integration tests extend `WP_UnitTestCase`, which provides:

- A fresh database for each test (tables are rolled back via transactions)
- Factory methods for creating posts, users, terms
- Assertion helpers for WordPress-specific checks

### Basic Test Structure

```php
class Test_MyPlugin_Core extends WP_UnitTestCase {

    public function set_up() {
        parent::set_up();
        // Runs before each test
    }

    public function tear_down() {
        // Runs after each test
        parent::tear_down();
    }

    public function test_plugin_is_active() {
        $this->assertTrue( is_plugin_active( 'myplugin/myplugin.php' ) );
    }
}
```

### Testing Functions

```php
class Test_MyPlugin_Helpers extends WP_UnitTestCase {

    public function test_format_price_with_decimals() {
        $result = myplugin_format_price( 19.99 );
        $this->assertEquals( '$19.99', $result );
    }

    public function test_format_price_rounds_correctly() {
        $result = myplugin_format_price( 19.999 );
        $this->assertEquals( '$20.00', $result );
    }

    public function test_format_price_handles_zero() {
        $result = myplugin_format_price( 0 );
        $this->assertEquals( '$0.00', $result );
    }

    public function test_format_price_handles_negative() {
        $result = myplugin_format_price( -5.50 );
        $this->assertEquals( '-$5.50', $result );
    }
}
```

### Using Factories

`WP_UnitTestCase` includes factories for creating test data:

```php
class Test_MyPlugin_PostFeatures extends WP_UnitTestCase {

    public function test_custom_meta_is_saved() {
        // Create a test post
        $post_id = self::factory()->post->create( array(
            'post_title'  => 'Test Post',
            'post_status' => 'publish',
        ) );

        // Run plugin function
        myplugin_save_score( $post_id, 85 );

        // Assert
        $score = get_post_meta( $post_id, '_myplugin_score', true );
        $this->assertEquals( 85, $score );
    }

    public function test_feature_requires_publish_status() {
        $draft_id = self::factory()->post->create( array(
            'post_status' => 'draft',
        ) );

        $result = myplugin_process_post( $draft_id );

        $this->assertFalse( $result );
    }

    public function test_only_admins_can_delete() {
        // Create a subscriber user
        $user_id = self::factory()->user->create( array(
            'role' => 'subscriber',
        ) );
        wp_set_current_user( $user_id );

        $post_id = self::factory()->post->create();
        $result  = myplugin_delete_item( $post_id );

        $this->assertWPError( $result );
    }
}
```

### Testing Hooks

```php
class Test_MyPlugin_Hooks extends WP_UnitTestCase {

    public function test_filter_modifies_title() {
        // Verify the filter is registered
        $this->assertNotFalse(
            has_filter( 'the_title', 'myplugin_modify_title' )
        );

        // Test the filter output
        $result = apply_filters( 'the_title', 'Original Title', 0 );
        $this->assertStringContainsString( 'Original Title', $result );
    }

    public function test_action_fires_on_save() {
        $fired = false;

        // Listen for our custom action
        add_action( 'myplugin_after_save', function() use ( &$fired ) {
            $fired = true;
        } );

        // Trigger the save
        $post_id = self::factory()->post->create();
        myplugin_save_data( $post_id, array( 'key' => 'value' ) );

        $this->assertTrue( $fired );
    }
}
```

### Testing AJAX Handlers

```php
class Test_MyPlugin_Ajax extends WP_UnitTestCase {

    public function test_ajax_returns_data() {
        // Log in as admin
        $user_id = self::factory()->user->create( array( 'role' => 'administrator' ) );
        wp_set_current_user( $user_id );

        // Set up the AJAX request
        $_POST['action'] = 'myplugin_get_data';
        $_POST['nonce']  = wp_create_nonce( 'myplugin_nonce' );
        $_POST['post_id'] = self::factory()->post->create();

        // Capture output
        try {
            $this->_handleAjax( 'myplugin_get_data' );
        } catch ( WPAjaxDieContinueException $e ) {
            // Expected — wp_send_json calls wp_die
        }

        $response = json_decode( $this->_last_response );
        $this->assertTrue( $response->success );
    }

    public function test_ajax_rejects_unauthorized() {
        // Not logged in
        wp_set_current_user( 0 );

        $_POST['action'] = 'myplugin_get_data';
        $_POST['nonce']  = 'invalid';

        try {
            $this->_handleAjax( 'myplugin_get_data' );
        } catch ( WPAjaxDieStopException $e ) {
            // Expected
        }

        $response = json_decode( $this->_last_response );
        $this->assertFalse( $response->success );
    }
}
```

### Testing REST API Endpoints

```php
class Test_MyPlugin_REST extends WP_UnitTestCase {

    private WP_REST_Server $server;

    public function set_up() {
        parent::set_up();

        global $wp_rest_server;
        $this->server = $wp_rest_server = new WP_REST_Server();
        do_action( 'rest_api_init' );
    }

    public function test_endpoint_is_registered() {
        $routes = $this->server->get_routes();
        $this->assertArrayHasKey( '/myplugin/v1/items', $routes );
    }

    public function test_get_items_returns_data() {
        // Create test data
        self::factory()->post->create_many( 3, array(
            'post_type' => 'myplugin_item',
        ) );

        $request  = new WP_REST_Request( 'GET', '/myplugin/v1/items' );
        $response = $this->server->dispatch( $request );

        $this->assertEquals( 200, $response->get_status() );
        $this->assertCount( 3, $response->get_data() );
    }

    public function test_create_item_requires_auth() {
        $request  = new WP_REST_Request( 'POST', '/myplugin/v1/items' );
        $request->set_body_params( array( 'title' => 'New Item' ) );

        $response = $this->server->dispatch( $request );

        $this->assertEquals( 401, $response->get_status() );
    }
}
```

## CI/CD with GitHub Actions

Automate tests on every push:

```yaml
# .github/workflows/tests.yml
name: Plugin Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        php: ['7.4', '8.0', '8.1', '8.2']
        wp: ['latest', '6.4']

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: wordpress_tests
        ports:
          - 3306:3306

    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ matrix.php }}
          extensions: mysql, mbstring, xml

      - name: Install Composer dependencies
        run: composer install --no-progress

      - name: Install WordPress test suite
        run: bash bin/install-wp-tests.sh wordpress_tests root root 127.0.0.1 ${{ matrix.wp }}

      - name: Run tests
        run: ./vendor/bin/phpunit
```

This tests your plugin across multiple PHP and WordPress version combinations. If it passes on PHP 7.4 + WP 6.4 and PHP 8.2 + WP latest, you have solid coverage.

## What to Test

### High Value (Test These First)

- **Data integrity** — Does your plugin save and retrieve data correctly?
- **Security** — Do permission checks work? Are nonces verified?
- **Edge cases** — Empty inputs, missing data, large datasets
- **Hooks** — Do your filters return expected values?

### Medium Value

- **Admin UI logic** — Settings save/load correctly
- **API endpoints** — Correct responses, error handling
- **Compatibility** — Works with popular plugins (WooCommerce, ACF)

### Low Value (Usually Skip)

- **WordPress core functions** — `get_post()` works; you don't need to test it
- **CSS/HTML output** — Better tested visually or with E2E tools
- **Third-party API responses** — Mock these instead of testing live

## Common Assertions

| Assertion | Use For |
|-----------|---------|
| `assertEquals( $expected, $actual )` | Exact value match |
| `assertTrue( $condition )` | Boolean checks |
| `assertFalse( $condition )` | Negative checks |
| `assertWPError( $result )` | Function returns WP_Error |
| `assertNotWPError( $result )` | Function succeeds |
| `assertCount( $expected, $array )` | Array length |
| `assertStringContainsString( $needle, $haystack )` | Partial string match |
| `assertArrayHasKey( $key, $array )` | Array structure |
| `assertEmpty( $value )` | Empty result |

## Further Reading

- [REST API](./06-rest-api.md) — Building endpoints to test
- [AJAX Patterns](./05-ajax-patterns.md) — AJAX handler patterns
- [Input Sanitization](../03-security/03-data-validation.md) — Security testing patterns
- [WordPress Plugin Test Handbook](https://make.wordpress.org/cli/handbook/misc/plugin-unit-tests/)
