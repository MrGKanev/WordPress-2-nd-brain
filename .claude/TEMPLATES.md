# Content Templates

Copy these templates when creating new content.

---

## New Section Template

```markdown
# Section Title

## Overview

One paragraph explaining what this section covers and why it matters. Set expectations for what the reader will learn.

## Main Concept

Explain the core idea. Use tables for comparisons:

| Option | Pros | Cons |
|--------|------|------|
| First | Good things | Bad things |
| Second | Other goods | Other bads |

## Practical Application

How to actually use this knowledge. Keep code minimal:

\`\`\`php
// Brief example with comment explaining purpose
\`\`\`

## Common Mistakes

What to avoid:

**Mistake name.** Why it's wrong and what to do instead.

## Further Reading

- [Related Section](./related-section.md) - Brief description
- [External Resource](https://example.com) - What you'll find there
```

---

## New Chapter README Template

```markdown
# Chapter Title

## Overview

What this chapter covers and why it matters. 2-3 sentences setting context.

## Key Principles

Core ideas that apply throughout this chapter:

**Principle one.** Explanation.

**Principle two.** Explanation.

## What This Chapter Covers

### [Section One](./01-section-one.md)

Brief description of what this section covers and key takeaways.

### [Section Two](./02-section-two.md)

Brief description of what this section covers and key takeaways.

## Quick Reference

Optional: Summary table or checklist for the whole chapter.

## Further Reading

- [Related Chapter](../other-chapter/README.md) - How it connects
```

---

## Code Example Template

When code is necessary, use this format:

```markdown
### Purpose of This Code

Explain what problem this solves before showing code.

\`\`\`php
/**
 * Brief description of what this does.
 *
 * @param type $param Description
 * @return type Description
 */
function example_function($param) {
    // Comment explaining non-obvious logic
    return $result;
}
\`\`\`

**Key points:**
- What to customize
- When to use this
- What to watch out for
```

---

## Comparison Table Template

For comparing options, tools, or approaches:

```markdown
## Comparison: X vs Y

| Aspect | Option X | Option Y |
|--------|----------|----------|
| **Best for** | Use case | Different use case |
| **Pros** | Advantage 1, Advantage 2 | Other advantages |
| **Cons** | Disadvantage 1 | Other disadvantages |
| **Cost** | Free / $X/month | Free / $Y/month |
| **Recommendation** | When to choose | When to choose |
```

---

## Checklist Template

For actionable lists:

```markdown
## Task Checklist

Before doing X, verify:

- [ ] First thing to check
- [ ] Second thing to check
- [ ] Third thing to check

After doing X:

- [ ] Verify result
- [ ] Clean up
- [ ] Document changes
```

---

## Warning/Insight Block Template

```markdown
> **Warning**: Critical information that could cause problems if ignored.

> **Note**: Helpful context that's good to know but not critical.

> **Tip**: Shortcut or best practice that improves results.
```

---

## Attribution Template

When content is inspired by or sourced from elsewhere:

```markdown
## Further Reading

Sources and additional resources:

- [Source Title](https://url) - What you'll find there
- [Another Source](https://url) - Brief description

---

*Parts of this section are based on insights from [Author/Source](https://url).*
```
