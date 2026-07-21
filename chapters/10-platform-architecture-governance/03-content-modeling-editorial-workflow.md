# Content Modeling & Editorial Workflow

Content modeling defines the information a site needs before it defines the page that displays it. A clear model prevents a single "Page" type from becoming an inconsistent mixture of articles, locations, products, team members and campaigns.

## Model the Domain

For each content type, document its purpose, owner, fields, relationships, URL and lifecycle:

| Type | Required fields | Relationships | Owner |
|------|-----------------|---------------|-------|
| Article | Title, author, publish date, category | Related articles | Editorial team |
| Location | Address, hours, contact details | Services | Operations team |
| Case study | Client permission, outcome, sector | Services, people | Marketing team |

Use a custom post type when the item has a distinct lifecycle, permissions, template or API meaning. Use taxonomy for a controlled classification used across many items. Do not create a custom post type merely to add a visual section to one landing page.

## Editorial States and Roles

Define how content moves from draft to publication:

```text
Draft → editorial review → legal/subject review (if needed) → scheduled → published → reviewed/retired
```

Map capabilities to this workflow. An author may create and edit drafts; an editor may publish; a specialist may approve a regulated claim without receiving full administrator access. Document emergency publishing and correction paths too.

## Quality Controls

Use templates, block patterns and field validation to make correct content easy to create. Create a pre-publish checklist for title, summary, taxonomy, accessibility, links, media rights and SEO metadata. For high-value content, schedule a review date so outdated claims and contact details are found before visitors report them.

See [Custom Post Types & Taxonomies](../08-plugin-development/04-custom-post-types.md) and [Technical SEO Fundamentals](../05-seo/01-technical-seo-fundamentals.md).

## Change the Model Safely

Content models change as an organization learns. Before changing a field, post type or taxonomy, inventory existing content and API consumers. Prefer adding a new field, migrating values in batches and updating templates to read both forms before removing the old field.

For a large editorial change, create a migration sample: move a representative set of pages, have authors review it, then automate the remaining work. Preserve the old URL and redirects where public links or search rankings depend on them. The correct content model is one that editors can maintain consistently, not merely one that looks elegant in the database.

## Editorial Metrics

Track workflow health with simple evidence: drafts awaiting review, overdue content reviews, broken-link rate, time from draft to publish and repeated support requests about a pattern or field. These signals show where the model or permissions need improvement.
