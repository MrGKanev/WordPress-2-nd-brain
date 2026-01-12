# Accessibility Basics

## Overview

Accessibility means building websites that everyone can use, including people with visual, auditory, motor, or cognitive disabilities. This isn't just ethical—it's increasingly legal, affects a significant portion of your audience, and often improves experience for everyone.

The web was designed to be accessible. HTML is inherently accessible when used correctly. Most accessibility problems come from overriding sensible defaults or using the wrong elements for the job.

## Why Accessibility Matters

### The Numbers

- **15-20% of people** have some form of disability
- **8% of men** have color vision deficiency
- **Everyone** benefits from accessible design (situational disabilities, aging, temporary impairments)

A site that works only for fully-abled users with perfect vision, hearing, and motor control excludes a massive audience.

### Legal Requirements

Accessibility lawsuits have increased dramatically:

- **ADA (US)**: Websites are increasingly considered "places of public accommodation"
- **Section 508**: US government sites must be accessible
- **EN 301 549 (EU)**: Public sector websites must meet WCAG 2.1 AA
- **EAA (EU, 2025)**: European Accessibility Act extends to private sector e-commerce

Many WooCommerce stores are legally required to be accessible. Even where not legally mandated, inaccessible sites face reputation risk.

### SEO Benefits

Accessible sites often rank better:
- Proper heading structure helps search engines understand content
- Alt text provides image context for indexing
- Transcript/caption content is searchable
- Good accessibility correlates with good technical SEO

### Business Impact

- **Larger audience**: Accessible sites reach more potential customers
- **Better UX for everyone**: Accessibility improvements help all users
- **Reduced legal risk**: Proactive accessibility is cheaper than lawsuits
- **Brand reputation**: Demonstrates social responsibility

## Understanding WCAG

The Web Content Accessibility Guidelines (WCAG) are the international standard for web accessibility. Current version is WCAG 2.2, with 2.1 still widely referenced.

### WCAG Principles (POUR)

| Principle | Meaning |
|-----------|---------|
| **Perceivable** | Users must be able to perceive content (see, hear, or otherwise sense it) |
| **Operable** | Users must be able to operate the interface (navigate, interact) |
| **Understandable** | Users must be able to understand content and interface |
| **Robust** | Content must work with assistive technologies now and in the future |

### Conformance Levels

| Level | Description | Target |
|-------|-------------|--------|
| **A** | Minimum accessibility | Bare minimum |
| **AA** | Acceptable accessibility | Standard target for most sites |
| **AAA** | Highest accessibility | Specialized needs, rarely required |

**Target WCAG 2.1 Level AA** for most sites. This is the legal standard in most jurisdictions and provides good accessibility without extreme constraints.

## Common WordPress Accessibility Issues

### 1. Missing or Poor Alt Text

Images without alt text are invisible to screen readers. Users hear nothing, or worse, the filename ("IMG_20240115_143052.jpg").

**The problem**: WordPress requires alt text in the media library, but many users leave it blank. Themes may display images without checking for alt text.

**Best practices for alt text:**
- Describe what the image shows, not what it is
- Be concise but specific ("Woman using laptop at cafe" not "Image")
- Decorative images should have empty alt (`alt=""`) not missing alt
- Don't start with "Image of" or "Photo of"—screen readers already announce it's an image

**For WooCommerce products:**
- Product images need descriptive alt text
- Include relevant details (color, size, variant)
- Gallery images should each be unique and descriptive

### 2. Color Contrast Problems

Low contrast text is hard to read for everyone and impossible for users with low vision. WCAG requires:

| Text Size | Minimum Contrast Ratio |
|-----------|------------------------|
| Normal text | 4.5:1 |
| Large text (18pt+) | 3:1 |
| UI components | 3:1 |

**Common violations:**
- Light gray text on white backgrounds
- Colored text on colored backgrounds
- Placeholder text with insufficient contrast
- Links that only differ by color (no underline)

**Testing**: Use browser developer tools or [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/).

### 3. Missing Focus Indicators

Keyboard users navigate by pressing Tab. They need visible focus indicators to know where they are.

**The problem**: Many themes remove the default focus outline for aesthetic reasons:
```css
/* DON'T DO THIS */
*:focus { outline: none; }
```

This makes keyboard navigation impossible.

**The fix**: If you remove the default outline, replace it with something visible:
```css
*:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
}
```

Or use `:focus-visible` to show focus only for keyboard users, not mouse clicks.

### 4. Poor Heading Structure

Screen reader users navigate by headings. They expect a logical hierarchy:
- One H1 per page (usually the title)
- H2 for major sections
- H3 for subsections within H2s
- Never skip levels (H1 → H3)

**Common problems:**
- Multiple H1s (theme adds one, content adds another)
- Skipping from H2 to H4
- Using headings for styling rather than structure
- Widgets using H2 when H3 would be appropriate

**Check your hierarchy**: Use browser extensions like HeadingsMap or the WAVE tool.

### 5. Form Accessibility Issues

Forms are interaction points—they must be accessible.

**Common issues:**
- Inputs without labels (or labels not associated with inputs)
- Error messages that aren't announced to screen readers
- Required fields indicated only by color
- Submit buttons that say only "Submit" (context unclear)

**Proper form structure:**
```html
<label for="email">Email address (required)</label>
<input type="email" id="email" name="email" required aria-describedby="email-help">
<span id="email-help">We'll never share your email.</span>
```

Key points:
- Every input needs a `<label>` with matching `for`/`id`
- Use `aria-describedby` for help text
- Indicate required fields in the label text, not just with asterisks
- Error messages should be associated with the field using `aria-describedby`

### 6. Inaccessible Navigation Menus

WordPress navigation menus can be tricky for accessibility:

**Mobile menus**: Hamburger menus must:
- Be keyboard accessible
- Have proper ARIA states (expanded/collapsed)
- Trap focus when open
- Be closeable with Escape key

**Dropdown menus**: Must:
- Open on Enter/Space, not just hover
- Allow keyboard navigation within
- Close when focus leaves

Many themes get this wrong. Test with keyboard-only navigation.

### 7. Auto-Playing Media

Videos or audio that play automatically are problematic:
- Disruptive for screen reader users
- Can cause seizures (flashing content)
- Annoying for everyone

**WCAG requirement**: No auto-playing audio longer than 3 seconds unless there's a control to stop it.

**Best practice**: Never auto-play. If you must, provide visible controls and pause on focus.

### 8. Missing Skip Links

Keyboard users must Tab through every element. On pages with complex navigation, this means dozens of Tab presses before reaching main content.

**Skip links** let users jump directly to main content:
```html
<a href="#main-content" class="skip-link">Skip to content</a>
```

Many themes include this but hide it poorly (making it inaccessible) or omit it entirely.

## WordPress Accessibility Features

WordPress has built-in accessibility features you should leverage:

### Core Features

- **Skip links**: Most modern themes include them
- **ARIA landmarks**: Block themes add proper landmarks
- **Focus management**: Core handles focus in modals
- **Alt text field**: Media library includes alt text input

### Theme Support

Add accessibility support in your theme:
```php
add_theme_support('html5', [
    'search-form',
    'comment-form',
    'comment-list',
    'gallery',
    'caption',
]);
```

This outputs semantic HTML5 elements instead of divs.

### Accessibility-Ready Themes

WordPress.org has an "Accessibility Ready" tag for themes that meet baseline requirements:
- Skip links present and functional
- Keyboard navigation works
- Proper heading structure
- Color contrast meets WCAG AA
- Form labels properly associated
- No automatic media playback

Choosing an Accessibility Ready theme provides a solid foundation.

## Testing Accessibility

### Automated Testing Tools

Automated tools catch 30-40% of issues. Use them as a starting point, not the final word.

**Browser Extensions:**
- **WAVE** (WebAIM): Highlights issues directly on page
- **axe DevTools**: Detailed accessibility testing
- **Lighthouse** (Chrome): Includes accessibility audit

**Online Tools:**
- **WebAIM WAVE**: web-based version
- **Pa11y**: Command-line testing for CI/CD
- **Tenon**: API-based testing

### Manual Testing

Automated tools miss many issues. Manual testing catches them:

**Keyboard Testing:**
1. Unplug your mouse
2. Navigate the entire site using only Tab, Enter, Space, and arrow keys
3. Can you reach everything? See where you are? Use all functionality?

**Screen Reader Testing:**
- **NVDA** (Windows, free): Most common screen reader
- **VoiceOver** (Mac/iOS, built-in): Apple's screen reader
- **JAWS** (Windows, paid): Corporate standard

Even a few minutes with a screen reader reveals issues automated tools miss.

**Color/Vision Testing:**
- Grayscale your screen: Is content still understandable?
- Use browser extensions to simulate color blindness
- Zoom to 200%: Does content still work?

### Testing Checklist

| Test | Method | Pass Criteria |
|------|--------|---------------|
| Keyboard navigation | Tab through site | All interactive elements reachable and visible |
| Focus indicators | Keyboard navigation | Always visible where you are |
| Headings | HeadingsMap extension | Logical hierarchy, no skipped levels |
| Alt text | WAVE tool | All meaningful images have descriptions |
| Color contrast | Contrast checker | 4.5:1 for text, 3:1 for large text |
| Forms | Screen reader | Labels announced, errors perceivable |
| Zoom | Browser zoom to 200% | Content readable, nothing cut off |

## Accessibility Plugins

Plugins can help, but they're not magic fixes:

| Plugin | Purpose | Notes |
|--------|---------|-------|
| [WP Accessibility](https://wordpress.org/plugins/wp-accessibility/) | Fix common issues | Adds skip links, toolbar, fixes themes |
| [Starter](https://developer.wordpress.org/plugins/starter/) | Accessibility toolbar | User controls for font size, contrast |
| [One Click Accessibility](https://developer.wordpress.org/plugins/one-click-accessibility/) | Accessibility features | Similar toolbar approach |

**Warning about overlay widgets**: Some services offer "accessibility overlay" widgets that claim to fix accessibility automatically. These are controversial and often ineffective:
- They don't fix underlying code issues
- Screen reader users typically disable them
- They may create legal liability (false compliance claims)
- Some actively interfere with assistive technology

**Fix your actual code** rather than overlaying widgets.

## Building Accessible Custom Features

When building custom functionality:

### JavaScript Interactions

Make interactive elements accessible:
- Use semantic HTML first (buttons for actions, links for navigation)
- Add ARIA states (`aria-expanded`, `aria-selected`, etc.)
- Manage focus appropriately
- Ensure keyboard operability

### Custom Components

For complex UI components (tabs, accordions, modals):
- Follow WAI-ARIA Authoring Practices
- Use established patterns, don't reinvent
- Test with actual assistive technology

### Content Considerations

Train content creators:
- Write meaningful link text ("Read the report" not "Click here")
- Use headings for structure, not styling
- Provide alt text for images
- Caption videos
- Keep language simple when possible

## Quick Wins for Accessibility

If you're starting from zero, these improvements give the biggest return:

1. **Add alt text** to all meaningful images
2. **Fix heading hierarchy** to be logical and sequential
3. **Ensure sufficient contrast** (especially on text)
4. **Check forms** have proper labels
5. **Test keyboard navigation** and fix focus issues
6. **Add skip link** if missing
7. **Choose an Accessibility Ready theme** for new projects

These address the most common issues and provide the foundation for deeper accessibility work.

## Further Reading

- [WebAIM](https://webaim.org/) - Accessibility education and resources
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/) - Patterns for accessible components
- [WordPress Accessibility Handbook](https://make.wordpress.org/accessibility/handbook/) - Official WordPress guidance
- [Theme Development](./README.md) - Building accessible themes
- [WCAG Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/) - Full WCAG criteria
