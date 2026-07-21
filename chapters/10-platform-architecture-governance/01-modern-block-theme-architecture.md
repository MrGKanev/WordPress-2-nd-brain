# Modern Block Theme Architecture

A block theme is a design system and editorial interface, not just a collection of templates. The architecture should define which choices are global, which are reusable patterns and which are intentionally left to editors.

## Core Building Blocks

| Layer | Responsibility |
|-------|----------------|
| `theme.json` | Global design tokens, typography, spacing and allowed controls |
| Templates | Page-level layout for content types and archives |
| Template parts | Reusable header, footer and shared layout regions |
| Patterns | Curated, repeatable editorial sections |
| Blocks | Focused interactive or data-driven components |

Put system-wide color, type and spacing decisions in `theme.json` rather than duplicating CSS in individual blocks. This keeps the editor controls aligned with the public site and makes a brand refresh a controlled change.

```json
{
  "version": 3,
  "settings": {
    "color": { "palette": [{ "slug": "brand", "color": "#1b4d3e", "name": "Brand" }] },
    "spacing": { "spacingSizes": [{ "slug": "m", "size": "1.5rem", "name": "Medium" }] }
  }
}
```

## Editorial Guardrails

Give editors flexible patterns for common content, but constrain choices that can damage accessibility, consistency or performance. Use block locking where layout must remain stable, restrict arbitrary colors and font sizes when brand consistency matters, and provide patterns instead of asking authors to assemble complex columns manually.

Test the Site Editor as an editor would: create a new page, use a pattern, replace media, edit navigation and preview on a small screen. A technically valid theme is incomplete if everyday editing requires custom HTML or support requests.

## Design-System Review

When adding a block, first decide whether it is a one-page composition, a reusable pattern or a true component with unique behavior. Prefer patterns and core blocks before creating a custom block. Custom blocks have a long-term API, accessibility and migration cost.

See [Block Themes](../07-theme-development/03-block-themes.md) and [Gutenberg Block Development](../08-plugin-development/08-block-development.md).

## Implementation Checklist

- [ ] Design tokens in `theme.json` cover the approved colors, typography and spacing scale.
- [ ] Page templates use semantic landmarks and work without a page-specific CSS override.
- [ ] Common page sections are patterns with clear names and preview content.
- [ ] Locked layouts protect critical content structure without blocking ordinary editorial work.
- [ ] Header, footer, navigation, search, 404 and archive templates are tested at narrow and wide widths.
- [ ] A block/theme update has a visual regression or manual review plan.

Keep an inventory of custom blocks and patterns. For each one, record its owner, expected content shape and migration path. A block attribute that becomes stored content is an API: renaming it later needs an explicit deprecation or migration strategy.
