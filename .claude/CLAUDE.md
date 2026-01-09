# Claude Instructions for WordPress Second Brain

This document defines how Claude should work on this knowledge base project.

## Project Overview

This is a "second brain" - a personal knowledge repository for WordPress development. It's built with mdBook and meant to be:
- Searchable reference material
- Evergreen (content should remain useful over time)
- Practical (focus on what works, not theory)
- Well-sourced (credit where credit is due)

## Content Philosophy

### What Makes Good Content Here

1. **Practical over theoretical** - Real solutions to real problems
2. **Concise over comprehensive** - Link to external resources instead of duplicating
3. **Opinionated over neutral** - State recommendations clearly
4. **Evergreen over timely** - Avoid dates in content, focus on principles

### Content Hierarchy

When adding new content, prioritize:
1. **Why** - Explain the reasoning first
2. **What** - Then the concept/solution
3. **How** - Finally the implementation (minimal code)
4. **Further reading** - Links for deeper exploration

## Writing Style

### Voice and Tone

- Second person ("you") for instructions
- Direct and confident, not hedging
- Professional but not formal
- Assume the reader is a competent developer

### Formatting Standards

```markdown
# Page Title (H1 - only one per file)

## Major Section (H2)

### Subsection (H3)

**Bold for emphasis** on key terms
`code` for inline technical terms
> Blockquotes for insights or warnings

| Tables | For | Comparisons |
|--------|-----|-------------|
```

### Code Blocks

- Use sparingly - this is a knowledge base, not a code repository
- Always specify language for syntax highlighting
- Add comments explaining the "why", not the "what"
- Prefer short, focused snippets over complete implementations

```php
// BAD - Too much code, no explanation
function my_function($param) {
    $result = do_something($param);
    if ($result) {
        return process($result);
    }
    return false;
}

// GOOD - Minimal code, clear purpose
// Disable XML-RPC to reduce attack surface
add_filter('xmlrpc_enabled', '__return_false');
```

## Research and Sources

### When Adding New Content

1. **Search first** - Check if the topic exists elsewhere in the book
2. **Verify accuracy** - Cross-reference with official documentation
3. **Note the source** - Add attribution when using external insights

### Citation Format

For inline references:
```markdown
According to [Google's documentation](https://developers.google.com/...), this approach...
```

For section sources:
```markdown
## Further Reading

- [Official WordPress Plugin Handbook](https://developer.wordpress.org/plugins/)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
```

### Source Quality Hierarchy

1. **Official documentation** (WordPress Codex, PHP docs)
2. **Established experts** (core contributors, recognized developers)
3. **Reputable publications** (Smashing Magazine, CSS-Tricks)
4. **Community consensus** (Stack Overflow with many upvotes)
5. **Personal experience** (mark clearly as opinion)

## Quality Checklist

Before considering content complete, verify:

### Structure
- [ ] Single H1 at the top
- [ ] Logical heading hierarchy (no skipped levels)
- [ ] Sections are focused and not too long
- [ ] Cross-references to related content

### Content
- [ ] Explains "why" before "how"
- [ ] Uses tables for comparisons
- [ ] Avoids unnecessary code
- [ ] Includes practical recommendations
- [ ] Notes outdated information if present

### Language
- [ ] No spelling errors (especially technical terms)
- [ ] Consistent terminology throughout
- [ ] Clear, direct sentences
- [ ] No unnecessary jargon

### Links
- [ ] Internal links use relative paths (`./file.md` or `../folder/file.md`)
- [ ] External links are to authoritative sources
- [ ] No broken links
- [ ] "Further Reading" section where appropriate

## Common Tasks

### Adding a New Section

1. Create file with correct naming: `XX-descriptive-name.md`
2. Start with H1 title matching the topic
3. Add overview paragraph explaining what this covers
4. Structure content with H2/H3 sections
5. End with "Further Reading" links to related sections
6. Update parent README.md to reference new section
7. Regenerate SUMMARY.md: `python scripts/generate_summary.py`

### Updating Existing Content

1. Read the full section first
2. Make minimal changes to preserve voice
3. Update any affected cross-references
4. Check that changes don't contradict other sections
5. Note if content is now outdated elsewhere

### Reviewing for Errors

1. **Spelling**: Pay attention to technical terms
   - WordPress (not Wordpress)
   - JavaScript (not Javascript)
   - PHP (all caps)
   - MySQL/MariaDB (capitalization matters)

2. **Markdown**: Check for common issues
   - Unclosed code blocks
   - Missing blank lines around lists
   - Broken table formatting
   - Missing language specifiers on code blocks

3. **Links**: Verify paths are correct
   - Same directory: `./file.md`
   - Parent directory: `../folder/file.md`
   - Never use absolute paths

## Content Ideas to Explore

These topics would strengthen the book:

### Plugin Architecture
- [ ] AJAX handling patterns
- [ ] Settings API usage
- [ ] Custom post types and taxonomies
- [ ] Gutenberg block development basics

### Security
- [ ] Input sanitization and output escaping
- [ ] Nonce verification
- [ ] Capability checks
- [ ] Common vulnerability patterns

### Performance
- [ ] Query optimization patterns
- [ ] Lazy loading implementations
- [ ] Asset optimization strategies
- [ ] Profiling and debugging tools

### Maintenance
- [ ] WP-CLI essentials
- [ ] Automated testing basics
- [ ] Deployment strategies
- [ ] Multisite considerations

## Workflow Commands

```bash
# Generate SUMMARY.md from current structure
python scripts/generate_summary.py

# Build HTML version (requires mdbook installed)
mdbook build

# Check for broken internal links
# (manual: grep for .md links and verify files exist)
grep -r "](.*\.md)" chapters/ | grep -v node_modules
```

## Sources and Inspiration

This approach is informed by:

- [Google Developer Documentation Style Guide](https://developers.google.com/style) - Industry standard for technical writing
- [Write the Docs](https://www.writethedocs.org/guide/) - Community best practices
- [mdBook Documentation](https://rust-lang.github.io/mdBook/) - Tool-specific guidance
- [Second Brain methodology](https://www.buildingasecondbrain.com/) - Knowledge management principles
- [BladeDocs - Documentation Version Control](https://bladedocs.com/dev-tools/best-practices-for-documentation-version-control-in-2024/) - Versioning best practices
