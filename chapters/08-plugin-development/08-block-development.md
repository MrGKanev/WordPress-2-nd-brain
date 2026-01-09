# Gutenberg Block Development

## Overview

The Block Editor (Gutenberg) is the default WordPress editing experience. Creating custom blocks allows plugins to add rich, interactive content types that editors can use without touching code. Understanding block development is increasingly important as WordPress moves toward Full Site Editing.

This guide covers the fundamentals. Block development is JavaScript-heavy and changes frequently—the official documentation should be your primary reference for current APIs.

## Block Basics

### What is a Block?

A block is a unit of content in the editor:

```
┌─────────────────────────────┐
│  Paragraph Block            │  ← Built-in
│  "Some text content..."     │
└─────────────────────────────┘

┌─────────────────────────────┐
│  Image Block                │  ← Built-in
│  [Image with controls]      │
└─────────────────────────────┘

┌─────────────────────────────┐
│  Product Card Block         │  ← Custom (your plugin)
│  [Product image, price...]  │
└─────────────────────────────┘
```

### Static vs. Dynamic Blocks

| Type | Rendering | Best For |
|------|-----------|----------|
| **Static** | Saved HTML in post content | Simple content (testimonials, CTAs) |
| **Dynamic** | PHP generates HTML on frontend | Content from database (recent posts, user data) |

## Project Setup

### Using @wordpress/scripts

The official build tool handles webpack, Babel, and build configuration:

```bash
# Create plugin directory
mkdir my-block-plugin && cd my-block-plugin

# Initialize npm
npm init -y

# Install build tools
npm install @wordpress/scripts --save-dev
```

**package.json:**
```json
{
  "name": "my-block-plugin",
  "scripts": {
    "build": "wp-scripts build",
    "start": "wp-scripts start"
  },
  "devDependencies": {
    "@wordpress/scripts": "^26.0.0"
  }
}
```

### Directory Structure

```
my-block-plugin/
├── build/                    # Compiled output (gitignored)
│   ├── index.js
│   ├── index.asset.php
│   └── style-index.css
├── src/
│   ├── index.js              # Block registration
│   ├── edit.js               # Editor component
│   ├── save.js               # Save function (static blocks)
│   ├── editor.scss           # Editor-only styles
│   └── style.scss            # Frontend + editor styles
├── block.json                # Block metadata
├── my-block-plugin.php       # Plugin entry point
└── package.json
```

## block.json

The block metadata file is required since WordPress 5.8:

```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "my-plugin/my-block",
  "version": "1.0.0",
  "title": "My Custom Block",
  "category": "widgets",
  "icon": "smiley",
  "description": "A custom block for my plugin.",
  "keywords": ["custom", "example"],
  "supports": {
    "html": false,
    "align": ["wide", "full"]
  },
  "attributes": {
    "content": {
      "type": "string",
      "source": "html",
      "selector": "p"
    },
    "backgroundColor": {
      "type": "string",
      "default": "#ffffff"
    }
  },
  "textdomain": "my-plugin",
  "editorScript": "file:./index.js",
  "editorStyle": "file:./index.css",
  "style": "file:./style-index.css"
}
```

### Key Properties

| Property | Purpose |
|----------|---------|
| `name` | Unique identifier (namespace/block-name) |
| `title` | Display name in inserter |
| `category` | Group in inserter (text, media, design, widgets, embed) |
| `icon` | Dashicon name or custom SVG |
| `attributes` | Data stored with the block |
| `supports` | Features like alignment, colors, spacing |
| `editorScript` | JavaScript for editor |
| `style` | CSS for frontend and editor |
| `render` | PHP file for dynamic blocks |

## Static Block Example

### Plugin Entry Point

```php
<?php
/**
 * Plugin Name: My Block Plugin
 * Description: A custom Gutenberg block
 * Version: 1.0.0
 * Text Domain: my-block-plugin
 */

function my_block_plugin_init() {
    register_block_type( __DIR__ . '/build' );
}
add_action( 'init', 'my_block_plugin_init' );
```

### JavaScript: index.js

```javascript
import { registerBlockType } from '@wordpress/blocks';
import Edit from './edit';
import save from './save';
import metadata from './block.json';

import './style.scss';
import './editor.scss';

registerBlockType( metadata.name, {
    edit: Edit,
    save,
} );
```

### JavaScript: edit.js

```javascript
import { __ } from '@wordpress/i18n';
import { useBlockProps, RichText } from '@wordpress/block-editor';

export default function Edit( { attributes, setAttributes } ) {
    const { content } = attributes;

    return (
        <div { ...useBlockProps() }>
            <RichText
                tagName="p"
                value={ content }
                onChange={ ( newContent ) =>
                    setAttributes( { content: newContent } )
                }
                placeholder={ __( 'Enter text...', 'my-block-plugin' ) }
            />
        </div>
    );
}
```

### JavaScript: save.js

```javascript
import { useBlockProps, RichText } from '@wordpress/block-editor';

export default function save( { attributes } ) {
    const { content } = attributes;

    return (
        <div { ...useBlockProps.save() }>
            <RichText.Content tagName="p" value={ content } />
        </div>
    );
}
```

## Dynamic Block Example

Dynamic blocks render with PHP on the frontend, useful when content depends on database queries.

### block.json for Dynamic Block

```json
{
  "apiVersion": 3,
  "name": "my-plugin/recent-posts",
  "title": "Recent Posts",
  "category": "widgets",
  "attributes": {
    "numberOfPosts": {
      "type": "number",
      "default": 5
    }
  },
  "editorScript": "file:./index.js",
  "render": "file:./render.php"
}
```

### PHP Render Callback

**render.php:**
```php
<?php
/**
 * Renders the block on the frontend.
 *
 * @param array    $attributes Block attributes.
 * @param string   $content    Block content.
 * @param WP_Block $block      Block instance.
 */

$recent_posts = get_posts( array(
    'numberposts' => $attributes['numberOfPosts'],
    'post_status' => 'publish',
) );

if ( empty( $recent_posts ) ) {
    return '<p>' . esc_html__( 'No posts found.', 'my-plugin' ) . '</p>';
}
?>

<div <?php echo get_block_wrapper_attributes(); ?>>
    <ul>
        <?php foreach ( $recent_posts as $post ) : ?>
            <li>
                <a href="<?php echo esc_url( get_permalink( $post ) ); ?>">
                    <?php echo esc_html( get_the_title( $post ) ); ?>
                </a>
            </li>
        <?php endforeach; ?>
    </ul>
</div>
```

### Editor Component for Dynamic Block

```javascript
import { __ } from '@wordpress/i18n';
import { useBlockProps, InspectorControls } from '@wordpress/block-editor';
import { PanelBody, RangeControl, Spinner } from '@wordpress/components';
import { useSelect } from '@wordpress/data';
import { store as coreStore } from '@wordpress/core-data';

export default function Edit( { attributes, setAttributes } ) {
    const { numberOfPosts } = attributes;

    // Fetch posts in editor
    const posts = useSelect(
        ( select ) => {
            return select( coreStore ).getEntityRecords( 'postType', 'post', {
                per_page: numberOfPosts,
                status: 'publish',
            } );
        },
        [ numberOfPosts ]
    );

    return (
        <>
            <InspectorControls>
                <PanelBody title={ __( 'Settings', 'my-plugin' ) }>
                    <RangeControl
                        label={ __( 'Number of posts', 'my-plugin' ) }
                        value={ numberOfPosts }
                        onChange={ ( value ) =>
                            setAttributes( { numberOfPosts: value } )
                        }
                        min={ 1 }
                        max={ 10 }
                    />
                </PanelBody>
            </InspectorControls>

            <div { ...useBlockProps() }>
                { ! posts && <Spinner /> }
                { posts && posts.length === 0 && (
                    <p>{ __( 'No posts found.', 'my-plugin' ) }</p>
                ) }
                { posts && posts.length > 0 && (
                    <ul>
                        { posts.map( ( post ) => (
                            <li key={ post.id }>
                                <a href={ post.link }>
                                    { post.title.rendered }
                                </a>
                            </li>
                        ) ) }
                    </ul>
                ) }
            </div>
        </>
    );
}
```

## Attributes

### Attribute Sources

```json
{
  "attributes": {
    // From HTML content
    "content": {
      "type": "string",
      "source": "html",
      "selector": "p"
    },

    // From HTML attribute
    "url": {
      "type": "string",
      "source": "attribute",
      "selector": "a",
      "attribute": "href"
    },

    // From inner text
    "title": {
      "type": "string",
      "source": "text",
      "selector": "h2"
    },

    // Stored in comment delimiter (no source)
    "showDate": {
      "type": "boolean",
      "default": true
    },

    // Array from multiple elements
    "items": {
      "type": "array",
      "source": "query",
      "selector": "li",
      "query": {
        "text": {
          "type": "string",
          "source": "text"
        }
      }
    }
  }
}
```

### Using Attributes

```javascript
export default function Edit( { attributes, setAttributes } ) {
    const { title, showDate } = attributes;

    return (
        <div { ...useBlockProps() }>
            <RichText
                tagName="h2"
                value={ title }
                onChange={ ( value ) => setAttributes( { title: value } ) }
            />
            <ToggleControl
                label="Show date"
                checked={ showDate }
                onChange={ ( value ) => setAttributes( { showDate: value } ) }
            />
        </div>
    );
}
```

## Block Supports

Enable built-in features through `supports`:

```json
{
  "supports": {
    "align": true,
    "align": ["wide", "full"],
    "anchor": true,
    "className": true,
    "color": {
      "background": true,
      "text": true,
      "link": true
    },
    "spacing": {
      "margin": true,
      "padding": true
    },
    "typography": {
      "fontSize": true,
      "lineHeight": true
    },
    "html": false
  }
}
```

WordPress automatically:
- Adds UI controls to the sidebar
- Saves values as attributes
- Applies inline styles or classes

## InnerBlocks

Allow nested blocks:

```javascript
import { useBlockProps, InnerBlocks } from '@wordpress/block-editor';

export default function Edit() {
    const ALLOWED_BLOCKS = [ 'core/paragraph', 'core/image', 'core/heading' ];
    const TEMPLATE = [
        [ 'core/heading', { placeholder: 'Title' } ],
        [ 'core/paragraph', { placeholder: 'Content...' } ],
    ];

    return (
        <div { ...useBlockProps() }>
            <InnerBlocks
                allowedBlocks={ ALLOWED_BLOCKS }
                template={ TEMPLATE }
                templateLock={ false }
            />
        </div>
    );
}

export function save() {
    return (
        <div { ...useBlockProps.save() }>
            <InnerBlocks.Content />
        </div>
    );
}
```

## Common Components

### From @wordpress/block-editor

```javascript
import {
    useBlockProps,
    RichText,
    InnerBlocks,
    InspectorControls,
    BlockControls,
    MediaUpload,
    MediaUploadCheck,
    ColorPalette,
    AlignmentToolbar,
} from '@wordpress/block-editor';
```

### From @wordpress/components

```javascript
import {
    PanelBody,
    TextControl,
    TextareaControl,
    ToggleControl,
    SelectControl,
    RangeControl,
    Button,
    Spinner,
    Placeholder,
} from '@wordpress/components';
```

## Building and Development

```bash
# Development (watch mode)
npm run start

# Production build
npm run build

# Check for issues
npm run lint:js
npm run lint:css
```

### Build Output

The build creates:
- `build/index.js` - Compiled JavaScript
- `build/index.asset.php` - Dependencies and version
- `build/style-index.css` - Frontend styles
- `build/index.css` - Editor-only styles

## Debugging Tips

### Console Logging

```javascript
console.log( 'Attributes:', attributes );
console.log( 'Block props:', useBlockProps() );
```

### React DevTools

Install React DevTools browser extension to inspect block components.

### Block Recovery

When a block's save output changes:
1. Editor shows "This block contains unexpected content"
2. Options: Attempt recovery, Keep HTML, Convert to Classic

During development, blocks frequently need recovery. In production, avoid changing save output after blocks are in use.

## Best Practices

### Do

- Use `block.json` for all metadata
- Keep editor and save output consistent
- Use `useBlockProps()` for wrapper elements
- Leverage built-in supports before custom UI
- Test with different themes
- Handle empty/error states

### Don't

- Don't modify save output after production use
- Don't skip `useBlockProps()` - breaks editor features
- Don't use deprecated APIs
- Don't forget translations (`@wordpress/i18n`)
- Don't ignore accessibility

## When to Create Custom Blocks

**Create a block when:**
- Editors need structured content creation
- Content has specific layout requirements
- Re-use across multiple posts
- Block editor integration improves UX

**Use alternatives when:**
- Simple shortcode is sufficient
- Content is purely programmatic (use dynamic widget)
- Rarely used (meta box might be simpler)

## Further Reading

- [WordPress Block Editor Handbook](https://developer.wordpress.org/block-editor/) - Official documentation
- [Block API Reference](https://developer.wordpress.org/block-editor/reference-guides/block-api/) - Complete API docs
- [Create Block Tool](https://developer.wordpress.org/block-editor/reference-guides/packages/packages-create-block/) - Scaffolding tool
- [REST API](./06-rest-api.md) - Data fetching in blocks
- [Internationalization](./07-internationalization.md) - Translating blocks
