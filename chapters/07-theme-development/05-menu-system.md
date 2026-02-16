# Menu System Deep Dive

WordPress's menu system handles everything from simple navigation bars to complex mega menus. It's built on `wp_nav_menu()`, a deceptively simple function that outputs navigation HTML. The real power (and complexity) comes from walker classes and the various filters available at each rendering stage.

## Registering Menu Locations

Before users can assign menus, your theme must register locations:

```php
add_action( 'after_setup_theme', function() {
    register_nav_menus( array(
        'primary'   => __( 'Primary Navigation', 'theme-textdomain' ),
        'footer'    => __( 'Footer Navigation', 'theme-textdomain' ),
        'mobile'    => __( 'Mobile Navigation', 'theme-textdomain' ),
    ) );
} );
```

For block themes, navigation is handled through the Navigation block instead. But classic themes and hybrid themes still rely on `register_nav_menus()`.

## Displaying Menus

### Basic Usage

```php
wp_nav_menu( array(
    'theme_location' => 'primary',
    'container'      => 'nav',
    'container_class'=> 'main-navigation',
    'menu_class'     => 'nav-menu',
    'fallback_cb'    => false, // Don't show anything if no menu assigned
) );
```

### All Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `theme_location` | `''` | Which registered location to use |
| `menu` | `''` | Specific menu (ID, slug, or name) |
| `container` | `'div'` | Wrapping element (`false` to disable) |
| `container_class` | `'menu-{slug}-container'` | Container CSS class |
| `container_id` | `''` | Container ID attribute |
| `menu_class` | `'menu'` | CSS class on the `<ul>` |
| `menu_id` | `'{slug}'` | ID on the `<ul>` |
| `items_wrap` | `'<ul>...</ul>'` | Format string for list wrapper |
| `before` | `''` | Text/HTML before `<a>` tag |
| `after` | `''` | Text/HTML after `</a>` tag |
| `link_before` | `''` | Text/HTML before link text |
| `link_after` | `''` | Text/HTML after link text |
| `depth` | `0` | Menu depth (0 = unlimited) |
| `walker` | `Walker_Nav_Menu` | Custom walker class |
| `fallback_cb` | `wp_page_menu` | Fallback if no menu assigned |

### Conditional Menu Display

```php
// Only display menu if it has items
if ( has_nav_menu( 'primary' ) ) {
    wp_nav_menu( array( 'theme_location' => 'primary' ) );
}
```

## Walker Classes

Walkers control how each menu item is rendered. The default `Walker_Nav_Menu` outputs standard `<li><a>` markup. Custom walkers let you change every aspect of the HTML output.

### Walker_Nav_Menu Methods

| Method | Controls | When Called |
|--------|----------|------------|
| `start_lvl()` | Opening `<ul>` tag for submenus | Before a submenu list |
| `end_lvl()` | Closing `</ul>` tag | After a submenu list |
| `start_el()` | Individual menu item `<li>` and `<a>` | For each item |
| `end_el()` | Closing `</li>` | After each item |

### Custom Walker Example

A walker that adds dropdown arrows and BEM-style classes:

```php
class Theme_Nav_Walker extends Walker_Nav_Menu {

    public function start_lvl( &$output, $depth = 0, $args = null ) {
        $indent = str_repeat( "\t", $depth );
        $output .= "\n{$indent}<ul class=\"nav-menu__submenu nav-menu__submenu--level-{$depth}\">\n";
    }

    public function start_el( &$output, $data_object, $depth = 0, $args = null, $current_object_id = 0 ) {
        $classes   = empty( $data_object->classes ) ? array() : (array) $data_object->classes;
        $has_children = in_array( 'menu-item-has-children', $classes, true );

        $class_string = 'nav-menu__item';
        if ( in_array( 'current-menu-item', $classes, true ) ) {
            $class_string .= ' nav-menu__item--active';
        }
        if ( $has_children ) {
            $class_string .= ' nav-menu__item--has-children';
        }

        $output .= sprintf( '<li class="%s">', esc_attr( $class_string ) );
        $output .= sprintf(
            '<a href="%s" class="nav-menu__link">%s</a>',
            esc_url( $data_object->url ),
            esc_html( $data_object->title )
        );

        if ( $has_children ) {
            $output .= '<button class="nav-menu__toggle" aria-expanded="false">';
            $output .= '<span class="screen-reader-text">Submenu</span>';
            $output .= '</button>';
        }
    }
}
```

Usage:

```php
wp_nav_menu( array(
    'theme_location' => 'primary',
    'walker'         => new Theme_Nav_Walker(),
) );
```

## Menu Filters

Filters let you modify menu output without a full custom walker.

### Commonly Used Filters

| Filter | Purpose | Parameters |
|--------|---------|------------|
| `wp_nav_menu_items` | Modify the full HTML of all items | `$items`, `$args` |
| `wp_nav_menu_objects` | Modify menu item objects before rendering | `$sorted_items`, `$args` |
| `nav_menu_link_attributes` | Modify `<a>` tag attributes | `$atts`, `$menu_item`, `$args`, `$depth` |
| `nav_menu_css_class` | Modify item CSS classes | `$classes`, `$menu_item`, `$args`, `$depth` |
| `walker_nav_menu_start_el` | Modify individual item HTML | `$item_output`, `$menu_item`, `$depth`, `$args` |

### Practical Filter Examples

```php
// Add a search form to the end of primary menu
add_filter( 'wp_nav_menu_items', function( $items, $args ) {
    if ( 'primary' === $args->theme_location ) {
        $items .= '<li class="menu-item menu-item-search">' . get_search_form( false ) . '</li>';
    }
    return $items;
}, 10, 2 );

// Add aria-current to current menu item link
add_filter( 'nav_menu_link_attributes', function( $atts, $menu_item ) {
    if ( $menu_item->current ) {
        $atts['aria-current'] = 'page';
    }
    return $atts;
}, 10, 2 );
```

## Mobile Navigation Patterns

### Off-Canvas Menu

The most common mobile pattern — menu slides in from the side:

```php
// Separate mobile menu location for different content/order
wp_nav_menu( array(
    'theme_location' => 'mobile',
    'container'      => 'nav',
    'container_class'=> 'mobile-navigation',
    'container_id'   => 'mobile-menu',
    'depth'          => 2,
    'fallback_cb'    => false,
) );
```

The JavaScript and CSS for toggle behavior are frontend concerns, but the key WordPress decision is whether to use the same menu location or a separate one for mobile.

| Approach | Pros | Cons |
|----------|------|------|
| Same menu, responsive CSS | One menu to manage | Limited flexibility |
| Separate mobile location | Different items/order for mobile | Two menus to maintain |
| Same menu, filtered output | One source, different rendering | More complex code |

### Hamburger Button Markup

```php
<button class="menu-toggle" aria-controls="mobile-menu" aria-expanded="false">
    <span class="screen-reader-text"><?php esc_html_e( 'Menu', 'theme-textdomain' ); ?></span>
    <span class="hamburger" aria-hidden="true"></span>
</button>
```

The `aria-controls` must match the menu container's `id`. The `aria-expanded` must toggle with JavaScript.

## Mega Menus

Mega menus show expanded content on hover/click — product categories, featured images, descriptions. They require more than standard WordPress menu markup.

### Approach Options

| Method | Complexity | Best For |
|--------|-----------|----------|
| **Custom walker + CSS** | Medium | Simple column layouts |
| **Menu item meta** | Medium | Adding images/descriptions to items |
| **Plugin** | Low | Complex layouts without custom code |
| **Block-based** | Medium | Block themes with Navigation block |

### Using Menu Item Descriptions

Enable descriptions in Screen Options (Menu admin screen), then display them:

```php
// In custom walker's start_el method
if ( ! empty( $data_object->description ) ) {
    $output .= '<span class="menu-item-description">' . esc_html( $data_object->description ) . '</span>';
}
```

### Mega Menu Plugins

| Plugin | Approach |
|--------|----------|
| **Max Mega Menu** | Replaces walker, drag-and-drop builder |
| **WP Mega Menu** | Widget areas inside menu items |
| **Jeelz Menu** | Separate mega menu builder |

## Accessibility

Navigation accessibility is critical — it's often the first thing screen reader users interact with.

### Required Practices

| Practice | Why |
|----------|-----|
| Use `<nav>` with `aria-label` | Screen readers announce navigation regions |
| `aria-current="page"` on current link | Tells screen readers which page the user is on |
| `aria-expanded` on submenu toggles | Announces submenu open/closed state |
| Keyboard navigation (Tab, Enter, Escape) | Not everyone uses a mouse |
| Skip navigation link | Let keyboard users skip past long menus |

### Skip Link

```php
// First element inside <body>
<a class="skip-link screen-reader-text" href="#main-content">
    <?php esc_html_e( 'Skip to content', 'theme-textdomain' ); ?>
</a>
```

```css
.skip-link {
    position: absolute;
    top: -100%;
    z-index: 999;
}
.skip-link:focus {
    top: 0;
    left: 0;
    padding: 1em;
    background: #fff;
}
```

### Keyboard Navigation for Submenus

Submenus must be:
- Openable with Enter or Space (not just hover)
- Closable with Escape
- Navigable with arrow keys
- Focus-trappable (Tab shouldn't jump out unexpectedly)

The WordPress core Twenty Twenty-Four and Twenty Twenty-Five themes demonstrate accessible navigation patterns worth studying.

## Menu Caching

On high-traffic sites, menu rendering adds up. Each `wp_nav_menu()` call queries the database.

```php
// Cache menu output in a transient
function theme_cached_menu( $location ) {
    $cache_key = 'nav_menu_' . $location;
    $output    = get_transient( $cache_key );

    if ( false === $output ) {
        $output = wp_nav_menu( array(
            'theme_location' => $location,
            'echo'           => false,
        ) );
        set_transient( $cache_key, $output, HOUR_IN_SECONDS );
    }

    echo $output;
}

// Purge cache when menu is updated
add_action( 'wp_update_nav_menu', function() {
    $locations = get_registered_nav_menus();
    foreach ( array_keys( $locations ) as $location ) {
        delete_transient( 'nav_menu_' . $location );
    }
} );
```

This works for logged-out visitors. Don't cache menus that change based on user state (login/role).

## Further Reading

- [Template Hierarchy](./01-template-hierarchy.md) — Where menus fit in theme templates
- [Accessibility Basics](./04-accessibility.md) — Broader accessibility requirements
- [Block Themes](./03-block-themes.md) — Navigation block in FSE
- [Frontend Asset Optimization](../04-performance/13-frontend-asset-optimization.md) — JavaScript for menu interactions
