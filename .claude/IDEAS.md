# Content Ideas & Roadmap

Future topics to research and add to the book.

## High Priority

### Plugin Development
- [ ] **AJAX Patterns** - wp_ajax hooks, nonces, response handling
- [ ] **Settings API** - register_setting, add_settings_section, options pages
- [ ] **Custom Post Types** - register_post_type, capabilities, rewrite rules
- [ ] **Taxonomies** - Custom taxonomies, term meta, hierarchical vs flat
- [ ] **Shortcodes** - Creating, attributes, nested shortcodes

### Security (expand existing chapter)
- [ ] **Input Sanitization** - sanitize_* functions, when to use each
- [ ] **Output Escaping** - esc_html, esc_attr, esc_url, wp_kses
- [ ] **Nonce Verification** - wp_nonce_field, wp_verify_nonce, AJAX nonces
- [ ] **Capability Checks** - current_user_can, custom capabilities
- [ ] **SQL Injection Prevention** - $wpdb->prepare patterns

### Performance (expand existing chapter)
- [ ] **Query Optimization** - WP_Query best practices, avoiding N+1
- [ ] **Transient Strategies** - When to use, cache warming, invalidation
- [ ] **Asset Loading** - Conditional loading, dependencies, defer/async
- [ ] **Profiling Tools** - Query Monitor, Debug Bar, Xdebug basics

## Medium Priority

### Development Workflow
- [ ] **WP-CLI Essentials** - Common commands, custom commands
- [ ] **Local Development** - LocalWP, DDEV, Lando comparison
- [ ] **Debugging** - WP_DEBUG, error logging, debug.log
- [ ] **Version Control** - .gitignore for WordPress, deployment strategies

### Theme Development
- [ ] **Theme Hierarchy** - Template loading order
- [ ] **Theme.json** - Block theme configuration
- [ ] **FSE (Full Site Editing)** - Block themes basics
- [ ] **Child Themes** - When and how to use

### Gutenberg / Block Editor
- [ ] **Block Development Intro** - @wordpress/scripts, block.json
- [ ] **Block Patterns** - Creating and registering
- [ ] **Block Variations** - Extending core blocks
- [ ] **InnerBlocks** - Nested block patterns

## Low Priority (Nice to Have)

### Multisite
- [ ] **Network Setup** - Subdomain vs subdirectory
- [ ] **Network Admin** - Managing sites and users
- [ ] **Plugin Considerations** - Network activation, site-specific

### REST API
- [ ] **Custom Endpoints** - register_rest_route
- [ ] **Authentication** - Application passwords, JWT
- [ ] **Extending Default Endpoints** - Adding fields, modifying responses

### E-commerce (WooCommerce)
- [ ] **WooCommerce Hooks** - Key action/filter points
- [ ] **Custom Product Types** - Extending product classes
- [ ] **Checkout Customization** - Fields, validation, payment gateways
- [ ] **Performance for WooCommerce** - Specific optimizations

### Internationalization
- [ ] **i18n Basics** - __(), _e(), _n(), text domains
- [ ] **POT File Generation** - WP-CLI, tools
- [ ] **RTL Support** - CSS considerations

## Research Topics

Things to investigate before writing:

### Emerging Standards
- [ ] WordPress Interactivity API
- [ ] Block Bindings API (WordPress 6.5+)
- [ ] Plugin Dependencies header
- [ ] Site Health improvements

### Industry Shifts
- [ ] Headless WordPress trends
- [ ] WordPress vs Jamstack
- [ ] AI integration in WordPress
- [ ] Core performance improvements in recent versions

## Content Maintenance

Periodic review needed:

### Annual Review
- [ ] PHP version recommendations (check EOL dates)
- [ ] Plugin recommendations (check if still maintained)
- [ ] Performance benchmarks (re-test with current versions)
- [ ] Security best practices (check for new vulnerabilities)

### After Major WordPress Releases
- [ ] New features to document
- [ ] Deprecated functions to note
- [ ] Changed best practices
- [ ] New default behaviors

## Contribution Ideas

For external contributors:

### Easy First Contributions
- Fix typos and grammar
- Add missing "Further Reading" links
- Improve code examples with better comments
- Add practical examples to theoretical sections

### Intermediate Contributions
- Write new sections for existing chapters
- Add comparison tables
- Create checklists for common tasks
- Improve cross-referencing between sections

### Advanced Contributions
- Write new chapters
- Add performance benchmarks with data
- Create decision flowcharts
- Write case studies from real projects
