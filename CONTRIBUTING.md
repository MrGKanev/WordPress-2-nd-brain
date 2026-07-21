# Contributing

This is a practical reference book. Changes should make a reader's next action
safer, clearer or easier to verify.

## Before opening a pull request

1. Keep each topic in the most specific existing chapter.
2. Add the page to `SUMMARY.md` (or regenerate it with `python3 scripts/generate_summary.py`).
3. Use relative Markdown links for internal references.
4. Test commands and code on a disposable local or staging environment.
5. Run the checks below.

```bash
python3 scripts/check_markdown_links.py
mdbook build
```

## Page structure

New practical pages should follow this shape when it fits the topic:

```md
# Clear task-oriented title

> Last reviewed: YYYY-MM
> Tested with: WordPress x.x, PHP x.x, WooCommerce x.x (when relevant)
> Risk: Low | Medium | High

Briefly state the outcome and when this approach is appropriate.

## Prerequisites

## Implementation

## Validation

## Rollback or recovery

## Common mistakes

## Further reading
```

Do not add metadata that has not been verified. Existing pages will be migrated
incrementally, starting with high-risk or fast-changing topics.

## Writing rules

- Prefer an explanation of *why* before a command or configuration block.
- State environment assumptions: operating system, web server, WordPress and PHP versions.
- Mark commands that can alter production data, permissions or availability.
- Link to an official source for version-sensitive, legal, security or vendor-specific claims.
- Keep examples generic: never include real domains, credentials or personal data.
