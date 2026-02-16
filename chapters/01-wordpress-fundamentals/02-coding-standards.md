# WordPress Coding Standards

WordPress has official coding standards for PHP, JavaScript, HTML, and CSS. Following them isn't about style preferences — it's about writing code that other WordPress developers can read, review, and maintain. If you submit to WordPress.org or contribute to core, these are mandatory. Even for private projects, they catch real bugs.

## Why Standards Matter

- **Code review**: Reviewers focus on logic, not formatting
- **Consistency**: Code looks the same across plugins, themes, and core
- **Bug prevention**: Many rules catch common mistakes (Yoda conditions, loose comparisons)
- **WordPress.org compliance**: Required for the plugin/theme directories

## PHP Coding Standards (WPCS)

### Key Rules

| Rule | Wrong | Right |
|------|-------|-------|
| Brace style | `function foo() {` on same line is fine | `function foo() {` — same line is correct in WP |
| Indentation | 4 spaces | 1 tab |
| Yoda conditions | `if ( $x == 5 )` | `if ( 5 === $x )` |
| Strict comparison | `==` and `!=` | `===` and `!==` |
| Space inside parentheses | `if($x)` | `if ( $x )` |
| Array syntax | `array()` and `[]` both exist | `array()` for WP Core style |
| String quotes | Mixed | Single quotes unless interpolation needed |
| Naming: functions | `camelCase()` | `snake_case()` |
| Naming: classes | `myClass` | `My_Class` |
| Naming: constants | `myConst` | `MY_CONST` |
| Naming: files | `myFile.php` | `class-my-file.php` |

### Yoda Conditions

Put the literal value on the left side of comparisons:

```php
// Standard (risky — typo = assignment bug)
if ( $status = 'active' ) { // Bug! Should be ==, but this assigns

// Yoda (safe — typo causes an error, not a bug)
if ( 'active' === $status ) { // If you typo =, PHP throws an error
```

### Function and Hook Naming

```php
// Prefix everything with your plugin/theme slug
function mytheme_enqueue_scripts() { ... }
function myplugin_register_settings() { ... }

// Hook callbacks should clearly describe what they do
add_action( 'init', 'myplugin_register_post_types' );
add_filter( 'the_content', 'myplugin_append_share_buttons' );
```

### Documentation Standards (PHPDoc)

```php
/**
 * Calculate the shipping cost based on weight and destination.
 *
 * @since 1.0.0
 *
 * @param float  $weight      Package weight in kg.
 * @param string $destination Country code (ISO 3166-1 alpha-2).
 * @return float Shipping cost in the store's base currency.
 */
function myplugin_calculate_shipping( $weight, $destination ) {
    // ...
}
```

Required for:
- Functions and methods
- Classes
- Class properties
- File headers (for plugins: Plugin Name, Description, Version, Author, etc.)

## Setting Up PHP_CodeSniffer

### Installation

```bash
# Install globally via Composer
composer global require "squizlabs/php_codesniffer"
composer global require "wp-coding-standards/wpcs"

# Set the installed_paths
phpcs --config-set installed_paths ~/.composer/vendor/wp-coding-standards/wpcs

# Verify WordPress standards are available
phpcs -i
# Should list: WordPress, WordPress-Core, WordPress-Docs, WordPress-Extra
```

### Per-Project Setup

```bash
# In your plugin/theme directory
composer require --dev wp-coding-standards/wpcs
```

Create a `phpcs.xml` configuration file:

```xml
<?xml version="1.0"?>
<ruleset name="My Plugin">
    <description>Custom ruleset for My Plugin</description>

    <!-- What to scan -->
    <file>.</file>

    <!-- What to skip -->
    <exclude-pattern>/vendor/</exclude-pattern>
    <exclude-pattern>/node_modules/</exclude-pattern>
    <exclude-pattern>/tests/</exclude-pattern>

    <!-- Use WordPress Extra (includes Core + Docs) -->
    <rule ref="WordPress-Extra"/>

    <!-- Check for proper text domain -->
    <rule ref="WordPress.WP.I18n">
        <properties>
            <property name="text_domain" type="array">
                <element value="my-plugin-textdomain"/>
            </property>
        </properties>
    </rule>

    <!-- Set minimum PHP version -->
    <config name="minimum_wp_version" value="6.0"/>
    <config name="testVersion" value="7.4-"/>
</ruleset>
```

### Running PHPCS

```bash
# Check all files
phpcs

# Check specific file
phpcs includes/class-my-feature.php

# Auto-fix what can be auto-fixed
phpcbf

# Show only errors (skip warnings)
phpcs -n

# Show sniff codes (useful for understanding violations)
phpcs -s
```

### Available Rulesets

| Ruleset | What It Checks |
|---------|---------------|
| `WordPress-Core` | Formatting, naming, syntax |
| `WordPress-Docs` | PHPDoc documentation |
| `WordPress-Extra` | Core + security + best practices |
| `WordPress` | Everything (Core + Docs + Extra) |

For most projects, `WordPress-Extra` is the right choice — it catches security issues and bad practices without requiring documentation on every function.

## JavaScript Standards

WordPress JavaScript follows a modified jQuery style guide:

| Rule | Standard |
|------|----------|
| Indentation | Tab |
| Semicolons | Required |
| Variable naming | camelCase |
| String quotes | Single quotes |
| Strict equality | `===` always |
| Spacing | Spaces inside parentheses, after `:` in objects |

### ESLint Configuration

For modern WordPress JavaScript (blocks, React):

```bash
npm install --save-dev @wordpress/eslint-plugin
```

`.eslintrc.js`:

```javascript
module.exports = {
    extends: [ 'plugin:@wordpress/eslint-plugin/recommended' ],
};
```

This covers both traditional jQuery-style code and modern React/JSX code.

## CSS Standards

| Rule | Standard |
|------|----------|
| Indentation | Tab |
| Selectors | Lowercase, hyphenated (`my-class` not `myClass`) |
| Properties | Alphabetical order within blocks |
| Shorthand | Use when setting all values |
| Units | No units on zero values (`margin: 0` not `margin: 0px`) |

## Editor Configuration

### EditorConfig

Create `.editorconfig` in your project root:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = tab
indent_size = 4
trim_trailing_whitespace = true
insert_final_newline = true

[*.yml]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

### VS Code Settings

```json
{
    "phpcs.standard": "WordPress-Extra",
    "phpcs.executablePath": "./vendor/bin/phpcs",
    "editor.formatOnSave": false,
    "[php]": {
        "editor.tabSize": 4,
        "editor.insertSpaces": false
    }
}
```

### PhpStorm

1. Settings → PHP → Quality Tools → PHP_CodeSniffer
2. Set path to `phpcs` executable
3. Settings → Editor → Inspections → PHP → Quality Tools
4. Enable PHP_CodeSniffer validation
5. Set standard to "WordPress" or point to your `phpcs.xml`

## CI/CD Integration

### GitHub Actions

```yaml
name: Coding Standards
on: [push, pull_request]

jobs:
  phpcs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'
          tools: cs2pr, phpcs, composer
      - run: composer install --no-progress
      - run: phpcs --report-full --report-checkstyle=./phpcs-report.xml
      - uses: staabm/annotate-pull-request-from-checkstyle@v1
        if: failure()
        with:
          files: phpcs-report.xml
```

### Pre-Commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit
FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.php$')
if [ -n "$FILES" ]; then
    vendor/bin/phpcs $FILES
    if [ $? -ne 0 ]; then
        echo "PHPCS errors found. Fix before committing."
        exit 1
    fi
fi
```

## Common PHPCS Violations

| Violation | What It Means | Fix |
|-----------|-------------|-----|
| `WordPress.Security.EscapeOutput` | Unescaped output | Use `esc_html()`, `esc_attr()`, etc. |
| `WordPress.Security.NonceVerification` | Missing nonce check | Add `wp_verify_nonce()` |
| `WordPress.DB.PreparedSQL` | SQL without `$wpdb->prepare()` | Use prepared statements |
| `WordPress.WP.I18n.MissingTranslatorsComment` | Missing translator note for complex strings | Add `// translators:` comment |
| `WordPress.PHP.YodaConditions` | Non-Yoda comparison | Flip: `'value' === $var` |
| `WordPress.WP.GlobalVariablesOverride` | Overwriting WP globals | Use different variable names |

## Further Reading

- [Plugin Structure](../08-plugin-development/01-plugin-structure.md) — File organization and naming
- [Plugin Testing](../08-plugin-development/13-plugin-testing.md) — Automated testing alongside PHPCS
- [WordPress PHP Coding Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/php/) — Official reference
- [WPCS GitHub Repository](https://github.com/WordPress/WordPress-Coding-Standards) — Rules and documentation
