# Composer for WordPress

Composer is PHP's dependency manager. In the WordPress world, it's used for managing plugin/theme dependencies in custom projects, building with Bedrock-style structures, and autoloading classes in plugin development. It's not required for typical WordPress work, but once your projects outgrow "install plugins from wp-admin," Composer becomes essential.

## Why Use Composer with WordPress

| Without Composer | With Composer |
|-----------------|---------------|
| Manual plugin downloads | `composer install` installs everything |
| FTP uploads for updates | `composer update` updates dependencies |
| No version locking | `composer.lock` ensures identical environments |
| "Works on my machine" problems | Same versions everywhere |
| Manual class loading | PSR-4 autoloading |

## WordPress and Composer: The Basics

### WPackagist

WordPress plugins and themes from the official directories are available as Composer packages via [WPackagist](https://wpackagist.org/):

```bash
# In your project root
composer init

# Add WPackagist as a repository
# (add to composer.json)
```

```json
{
    "repositories": [
        {
            "type": "composer",
            "url": "https://wpackagist.org",
            "only": [
                "wpackagist-plugin/*",
                "wpackagist-theme/*"
            ]
        }
    ],
    "require": {
        "wpackagist-plugin/advanced-custom-fields": "^6.0",
        "wpackagist-plugin/wordpress-seo": "^22.0",
        "wpackagist-theme/flavor": "^1.0"
    },
    "extra": {
        "installer-paths": {
            "wp-content/plugins/{$name}/": [
                "type:wordpress-plugin"
            ],
            "wp-content/themes/{$name}/": [
                "type:wordpress-theme"
            ]
        }
    }
}
```

Then:

```bash
composer install
```

Plugins and themes are installed to their correct directories automatically.

### Installing Premium Plugins

Premium plugins aren't on WPackagist. Options:

| Method | How |
|--------|-----|
| **Private Packagist** | Host packages on private Composer repository ($) |
| **SatisPress** | WordPress plugin that exposes installed plugins as Composer packages |
| **Direct ZIP** | Package type "dist" with URL to download |
| **Git repository** | If the plugin has a Git repo |

```json
{
    "repositories": [
        {
            "type": "package",
            "package": {
                "name": "vendor/premium-plugin",
                "version": "2.5.0",
                "type": "wordpress-plugin",
                "dist": {
                    "url": "https://example.com/downloads/premium-plugin-2.5.0.zip",
                    "type": "zip"
                }
            }
        }
    ]
}
```

## Bedrock

[Bedrock](https://roots.io/bedrock/) by Roots is the most popular Composer-based WordPress boilerplate. It restructures WordPress for modern development:

### Bedrock Directory Structure

```
project/
├── composer.json           # Dependencies
├── .env                    # Environment variables (credentials)
├── config/
│   ├── application.php     # WordPress config (replaces wp-config.php)
│   └── environments/
│       ├── development.php
│       ├── staging.php
│       └── production.php
├── web/                    # Document root
│   ├── app/                # wp-content equivalent
│   │   ├── plugins/
│   │   ├── themes/
│   │   └── mu-plugins/
│   ├── wp/                 # WordPress core (installed by Composer)
│   └── index.php
└── vendor/                 # Composer packages
```

### Key Bedrock Features

| Feature | Benefit |
|---------|---------|
| `.env` for credentials | No passwords in version control |
| WordPress as a dependency | Core managed by Composer, not committed |
| Separate config per environment | Different settings for dev/staging/production |
| Modern directory structure | Document root is `web/`, not project root |
| mu-plugins autoloader | Composer-installed mu-plugins just work |

### Getting Started with Bedrock

```bash
composer create-project roots/bedrock my-project
cd my-project

# Configure environment
cp .env.example .env
# Edit .env with database credentials, site URL, etc.

# Install a plugin
composer require wpackagist-plugin/wordpress-seo

# Install WordPress
# Point web server to /web directory
# Run WordPress installer
```

### When to Use Bedrock

| Scenario | Use Bedrock? |
|----------|-------------|
| Team development with version control | Yes |
| Automated deployments (CI/CD) | Yes |
| Multiple environments (dev/staging/prod) | Yes |
| Client project you'll maintain | Yes |
| Quick one-off site | Probably not |
| Shared hosting with FTP only | No (needs SSH/CLI access) |

## Composer in Plugin Development

### Autoloading Classes

Instead of manually `require`-ing PHP files, use Composer's autoloader:

```json
{
    "name": "vendor/my-plugin",
    "autoload": {
        "psr-4": {
            "MyPlugin\\": "src/"
        }
    }
}
```

Directory structure:

```
my-plugin/
├── composer.json
├── my-plugin.php          # Main plugin file
├── src/
│   ├── Plugin.php         # MyPlugin\Plugin
│   ├── Admin/
│   │   └── Settings.php   # MyPlugin\Admin\Settings
│   └── Frontend/
│       └── Display.php    # MyPlugin\Frontend\Display
└── vendor/                # Composer autoloader
```

Main plugin file:

```php
<?php
/**
 * Plugin Name: My Plugin
 */

if ( file_exists( __DIR__ . '/vendor/autoload.php' ) ) {
    require __DIR__ . '/vendor/autoload.php';
}

// Now classes autoload by namespace
$plugin = new MyPlugin\Plugin();
$plugin->init();
```

### Dev Dependencies

Keep development tools separate from production:

```json
{
    "require": {
        "php": ">=7.4"
    },
    "require-dev": {
        "wp-coding-standards/wpcs": "^3.0",
        "phpunit/phpunit": "^9.0",
        "yoast/phpunit-polyfills": "^2.0"
    }
}
```

```bash
# Install everything (development)
composer install

# Install without dev dependencies (production)
composer install --no-dev
```

### Scoping Dependencies (PHP-Scoper)

If your plugin uses Composer libraries, they might conflict with other plugins using the same library at a different version. PHP-Scoper prefixes namespaces to avoid this:

```bash
# Without scoping: both plugins use Guzzle, version conflict
Plugin A → Guzzle 6.5
Plugin B → Guzzle 7.0  # Fatal error: incompatible

# With scoping: each plugin has its own copy
Plugin A → MyPluginA\Vendor\GuzzleHttp\...
Plugin B → MyPluginB\Vendor\GuzzleHttp\...
```

| Tool | Purpose |
|------|---------|
| **PHP-Scoper** | Prefix namespaces of dependencies |
| **Mozart** | WordPress-specific dependency isolation |
| **Strauss** | Successor to Mozart, actively maintained |

## Version Constraints

| Constraint | Meaning | Example |
|-----------|---------|---------|
| `^6.0` | >= 6.0, < 7.0 (next major) | Most common, safe |
| `~6.0` | >= 6.0, < 6.1 (next minor) | More conservative |
| `6.0.*` | >= 6.0.0, < 6.1.0 | Same as tilde |
| `>=6.0` | Any version 6.0 or higher | Risky, no upper bound |
| `6.0.5` | Exactly this version | Pinned, no updates |
| `dev-main` | Latest from main branch | Development only |

**Recommendation:** Use `^` (caret) for most dependencies. It allows patch and minor updates but prevents breaking major version changes.

## Common Workflows

### Adding a Dependency

```bash
# Add a plugin
composer require wpackagist-plugin/wp-mail-smtp

# Add a PHP library for your plugin
composer require monolog/monolog

# Add a dev tool
composer require --dev squizlabs/php_codesniffer
```

### Updating Dependencies

```bash
# Update everything
composer update

# Update one package
composer update wpackagist-plugin/wordpress-seo

# Check for outdated packages
composer outdated

# Check for security vulnerabilities
composer audit
```

### composer.lock

The `composer.lock` file records the exact versions installed. **Always commit this file.** It ensures every developer and every deployment uses identical versions.

```bash
# Install from lock file (production/CI)
composer install --no-dev --optimize-autoloader

# Update lock file (when you want newer versions)
composer update
```

## Deployment with Composer

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Install dependencies
  run: composer install --no-dev --optimize-autoloader --prefer-dist

- name: Deploy
  run: rsync -avz --exclude='.git' --exclude='node_modules' ./ server:/var/www/html/
```

### What to Deploy

| Include | Exclude |
|---------|---------|
| `vendor/` (production deps only) | `.git/` |
| `composer.json` | `composer.lock` (already used by install) |
| `wp-content/` or `web/app/` | `node_modules/` |
| WordPress core | `.env` (use server-side env) |
| Theme build output | Source SCSS/TS files |

## Limitations

| Limitation | Workaround |
|-----------|-----------|
| WordPress core isn't a Composer package by default | Use `johnpbloch/wordpress-core` or Bedrock |
| Premium plugins aren't on WPackagist | SatisPress, private Packagist, or manual |
| Shared hosting often lacks SSH | Use local build + deploy, or switch hosting |
| Some plugins modify their own files | Those plugins break with Composer-managed installs |
| Client might install plugins via wp-admin | Educate or use mu-plugin to prevent |

## Further Reading

- [WordPress Coding Standards](./02-coding-standards.md) — PHPCS as a Composer dev dependency
- [Plugin Structure](../08-plugin-development/01-plugin-structure.md) — File organization
- [Plugin Testing](../08-plugin-development/13-plugin-testing.md) — PHPUnit via Composer
- [Bedrock Documentation](https://roots.io/bedrock/docs/) — Official Bedrock guide
- [WPackagist](https://wpackagist.org/) — WordPress Composer mirror
