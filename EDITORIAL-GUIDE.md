# Editorial Guide

This book is a practical reference. Each page should help a reader make a safer decision or complete a real task, not merely list concepts.

## Review Metadata

Add review metadata to new or substantially revised pages when the topic is version-sensitive or high-risk:

```md
> Last reviewed: YYYY-MM
> Tested with: WordPress x.x, PHP x.x, WooCommerce x.x (when relevant)
> Risk: Low | Medium | High
```

Do not invent tested versions. If a command is untested in the repository, state its assumptions and label the validation the reader must perform.

## Writing Pattern

Use this sequence when it fits:

1. State the desired outcome and when the approach applies.
2. Explain the important constraint or trade-off.
3. Show the smallest safe implementation or checklist.
4. Explain how to validate and, for risky changes, roll back.
5. Link to the next related chapter rather than repeating it.

Commands that can change production data, permissions, cache state or availability need a warning and a recovery path. Prefer generic domains, placeholder credentials and idempotent examples.

## Consistency Rules

- Use sentence-case headings and descriptive link text.
- Explain abbreviations at their first use on a page.
- Keep a table only when readers need to compare more than two repeated attributes.
- Use a diagram for a request path, hierarchy or multi-step failure flow; otherwise prefer concise prose.
- Link to primary documentation for version-sensitive vendor behavior, law or security requirements.

## Editorial Review

Before merging a significant page, check correctness, readability, internal links, code safety, accessibility of examples and overlap with existing content. Update [CHANGELOG.md](CHANGELOG.md) for material reader-facing changes.
