# WordPress Interactivity API

The Interactivity API (introduced in WordPress 6.5) provides a standard way to add client-side behavior to blocks. Instead of writing vanilla JavaScript or bundling React for frontend interactions, you use HTML directives that WordPress processes — similar to how Alpine.js or Vue works, but integrated into the block editor ecosystem.

## Why the Interactivity API Exists

Before this API, adding interactivity to WordPress blocks was messy:

| Approach | Problem |
|----------|---------|
| Vanilla JS in `view.js` | No shared state between blocks, manual DOM management |
| React on the frontend | Heavy, different runtime than server-rendered blocks |
| Alpine.js / Petite-Vue | External dependency, not standardized |
| jQuery | Outdated patterns, performance overhead |

The Interactivity API solves this by providing:
- **Declarative directives** in HTML (no imperative DOM manipulation)
- **Shared state** between blocks on the same page
- **Server-side rendering** compatibility (progressive enhancement)
- **Standard pattern** all block developers can follow

## Core Concepts

### Directives

Directives are HTML attributes that define behavior:

```html
<div
    data-wp-interactive="myPlugin"
    data-wp-context='{ "isOpen": false }'
>
    <button data-wp-on--click="actions.toggle">
        Toggle
    </button>
    <div data-wp-bind--hidden="!context.isOpen">
        This content shows/hides
    </div>
</div>
```

### Available Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `data-wp-interactive` | Declares the interactive namespace | `data-wp-interactive="myPlugin"` |
| `data-wp-context` | Sets local state for this element tree | `data-wp-context='{ "count": 0 }'` |
| `data-wp-on--{event}` | Event handlers | `data-wp-on--click="actions.increment"` |
| `data-wp-bind--{attr}` | Bind attributes to state | `data-wp-bind--hidden="!state.isVisible"` |
| `data-wp-class--{name}` | Toggle CSS classes | `data-wp-class--active="state.isActive"` |
| `data-wp-style--{prop}` | Dynamic inline styles | `data-wp-style--color="state.textColor"` |
| `data-wp-text` | Set text content | `data-wp-text="state.message"` |
| `data-wp-html` | Set inner HTML (use carefully) | `data-wp-html="state.richContent"` |
| `data-wp-watch` | Run effect when dependencies change | `data-wp-watch="callbacks.onCountChange"` |
| `data-wp-init` | Run on element mount | `data-wp-init="callbacks.setup"` |
| `data-wp-each` | Loop over array | `data-wp-each="state.items"` |

### State vs. Context

| Concept | Scope | Use For |
|---------|-------|---------|
| **State** (`store().state`) | Global — shared across all instances | App-wide values (theme mode, user preferences) |
| **Context** (`data-wp-context`) | Local — scoped to element tree | Per-instance values (is this accordion open?) |

## Basic Example: Toggle Block

### Block Server-Side (PHP)

```php
<?php
// render.php for a toggle block
$unique_id = wp_unique_id( 'toggle-' );
?>
<div
    <?php echo get_block_wrapper_attributes(); ?>
    data-wp-interactive="myPlugin"
    data-wp-context='<?php echo wp_json_encode( array( 'isOpen' => false ) ); ?>'
>
    <button
        data-wp-on--click="actions.toggle"
        data-wp-bind--aria-expanded="context.isOpen"
        aria-controls="<?php echo esc_attr( $unique_id ); ?>"
    >
        <span data-wp-text="context.isOpen ? 'Hide' : 'Show'">Show</span> Details
    </button>

    <div
        id="<?php echo esc_attr( $unique_id ); ?>"
        data-wp-bind--hidden="!context.isOpen"
        hidden
    >
        <?php echo $content; ?>
    </div>
</div>
```

### Client-Side Store (JavaScript)

```javascript
// view.js
import { store } from '@wordpress/interactivity';

store( 'myPlugin', {
    actions: {
        toggle() {
            const context = getContext();
            context.isOpen = ! context.isOpen;
        },
    },
} );
```

### Registering the View Script

In `block.json`:

```json
{
    "apiVersion": 3,
    "name": "my-plugin/toggle",
    "title": "Toggle Block",
    "supports": {
        "interactivity": true
    },
    "viewScriptModule": "file:./view.js"
}
```

Note: Use `viewScriptModule` (not `viewScript`) for Interactivity API — it uses ES modules.

## Practical Example: Accordion

```php
<?php // render.php ?>
<div
    <?php echo get_block_wrapper_attributes( array( 'class' => 'accordion' ) ); ?>
    data-wp-interactive="myPlugin/accordion"
    data-wp-context='<?php echo wp_json_encode( array( 'activeIndex' => -1 ) ); ?>'
>
    <?php foreach ( $items as $index => $item ) : ?>
        <div class="accordion-item" data-wp-context='<?php echo wp_json_encode( array( 'index' => $index ) ); ?>'>
            <button
                class="accordion-trigger"
                data-wp-on--click="actions.toggleItem"
                data-wp-bind--aria-expanded="callbacks.isItemOpen"
                data-wp-class--is-open="callbacks.isItemOpen"
            >
                <?php echo esc_html( $item['title'] ); ?>
            </button>
            <div
                class="accordion-panel"
                data-wp-bind--hidden="!callbacks.isItemOpen"
            >
                <?php echo wp_kses_post( $item['content'] ); ?>
            </div>
        </div>
    <?php endforeach; ?>
</div>
```

```javascript
// view.js
import { store, getContext } from '@wordpress/interactivity';

store( 'myPlugin/accordion', {
    actions: {
        toggleItem() {
            const ctx = getContext();
            const parent = getContext( { level: 1 } ); // Parent context
            parent.activeIndex = parent.activeIndex === ctx.index ? -1 : ctx.index;
        },
    },
    callbacks: {
        isItemOpen() {
            const ctx = getContext();
            const parent = getContext( { level: 1 } );
            return parent.activeIndex === ctx.index;
        },
    },
} );
```

## State Management

### Global State

```javascript
const { state } = store( 'myPlugin', {
    state: {
        count: 0,
        get doubleCount() {
            return state.count * 2;
        },
    },
    actions: {
        increment() {
            state.count++;
        },
    },
} );
```

Access in HTML:

```html
<span data-wp-text="state.count">0</span>
<span data-wp-text="state.doubleCount">0</span>
<button data-wp-on--click="actions.increment">+1</button>
```

### Derived State (Getters)

Use `get` properties for computed values:

```javascript
store( 'myPlugin', {
    state: {
        items: [],
        filter: 'all',
        get filteredItems() {
            if ( state.filter === 'all' ) return state.items;
            return state.items.filter( item => item.status === state.filter );
        },
        get itemCount() {
            return state.filteredItems.length;
        },
    },
} );
```

### Side Effects (Watchers)

```javascript
store( 'myPlugin', {
    callbacks: {
        // Runs when referenced state changes
        onCountChange() {
            const { count } = store( 'myPlugin' ).state;
            // Save to localStorage, fetch data, etc.
            localStorage.setItem( 'count', count );
        },
    },
} );
```

```html
<div data-wp-watch="callbacks.onCountChange">
    <!-- This element "watches" for state changes -->
</div>
```

## Server-Side Rendering

The Interactivity API is designed for progressive enhancement. Content is server-rendered first, then enhanced with interactivity:

```
Server renders HTML with directives → Browser loads → JS processes directives → Interactive
```

This means:
- Content is visible before JavaScript loads (good for SEO and performance)
- If JavaScript fails, content is still accessible
- Initial render doesn't wait for JavaScript bundle

### Providing Initial State from PHP

```php
// In render.php or via wp_interactivity_state()
wp_interactivity_state( 'myPlugin', array(
    'items'    => $items_from_database,
    'apiUrl'   => rest_url( 'myplugin/v1/items' ),
    'nonce'    => wp_create_nonce( 'wp_rest' ),
) );
```

Access in JavaScript:

```javascript
const { state } = store( 'myPlugin' );
// state.items, state.apiUrl, state.nonce are available
```

## Async Operations

### Fetching Data

```javascript
import { store, getContext } from '@wordpress/interactivity';

store( 'myPlugin', {
    state: {
        isLoading: false,
    },
    actions: {
        *loadMore() {
            const { state } = store( 'myPlugin' );
            state.isLoading = true;

            try {
                const response = yield fetch( state.apiUrl );
                const data = yield response.json();
                state.items.push( ...data );
            } finally {
                state.isLoading = false;
            }
        },
    },
} );
```

Generator functions (`function*`) are used for async actions — the Interactivity API handles the async flow.

## When to Use the Interactivity API

| Use Case | Interactivity API? | Alternative |
|----------|-------------------|-------------|
| Block with show/hide behavior | Yes | — |
| Block with counters/toggles | Yes | — |
| Block fetching data client-side | Yes | — |
| Full SPA-like application | No | React app, Next.js |
| Non-block frontend feature | No | Regular JavaScript |
| Admin-only functionality | No | React (wp-element) |
| Simple one-time animation | No | CSS or vanilla JS |

### Key Requirement

The Interactivity API only works within **block markup**. It's not a general-purpose JavaScript framework for WordPress — it's specifically for making blocks interactive.

## Comparison with Other Approaches

| Feature | Interactivity API | Alpine.js | React (frontend) | Vanilla JS |
|---------|------------------|-----------|-------------------|-----------|
| WordPress integration | Native | External dependency | Possible | Manual |
| Learning curve | Medium | Low | High | Low-Medium |
| Server rendering | Built-in | Separate | Requires SSR setup | Manual |
| Shared state between blocks | Yes | No (without extra work) | With context/store | Manual |
| Bundle size | Included in WP | ~15KB | ~45KB+ | 0KB |
| Block editor compatible | Yes | Not standard | Already used in editor | Yes |

## Further Reading

- [Block Development](./08-block-development.md) — Block fundamentals
- [REST API](./06-rest-api.md) — Building endpoints for data fetching
- [AJAX Patterns](./05-ajax-patterns.md) — Traditional async patterns
- [Interactivity API Reference](https://developer.wordpress.org/block-editor/reference-guides/interactivity-api/) — Official documentation
