# Accessibility Quality Assurance

Accessibility is a product-quality practice, not a final visual review. Automated tools catch common markup problems, but keyboard and screen-reader tests reveal whether people can actually complete a task.

## Minimum Review

- Navigate every key flow using only a keyboard; focus must stay visible and predictable.
- Use semantic headings, labels, buttons and landmarks before adding ARIA.
- Check contrast, zoom/reflow and error messages on forms.
- Test menus, dialogs, search and checkout with a screen reader.
- Include accessibility checks in design review and browser-test coverage.

Prioritize the tasks that matter most: finding content, submitting a form, signing in and completing a purchase. Fix reusable components first so a single improvement benefits the entire site.

See [Accessibility Basics](../07-theme-development/04-accessibility.md).

## Build Accessibility into Components

Most accessibility defects are repeated component defects. A menu, modal, product card or form field should have one well-tested implementation that is reused across templates and blocks. Define the accessible name, focus behavior, keyboard interaction and error state before styling the component.

For custom Gutenberg blocks, verify the editor experience as well as the frontend. Controls need understandable labels, block settings must be operable with a keyboard, and preview content should not create misleading heading levels or duplicate labels.

## Test the Actual Task

Automated scans are useful regression checks, but they cannot tell whether a checkout confirmation is understandable or whether focus returns to the right trigger after a dialog closes. Use a short task-based script:

1. Start at the homepage with a keyboard only.
2. Find a product or article, use filtering or search, and open the detail page.
3. Complete the primary form or checkout with intentionally invalid values once.
4. Repeat key steps with a screen reader and at 200% browser zoom.

Record the browser, assistive technology and result. Fix blockers first, then add a regression test or component-level rule so the same mistake does not return.

## Content Is Part of Accessibility

Editors also affect the outcome. Provide guidance for heading order, descriptive link text, meaningful alternative text and captions. Do not require authors to solve complex markup in every post; make the accessible path the easiest path in block patterns and editorial templates.

## Forms, Errors and Feedback

Forms are where accessibility defects become task failures. Every input needs a programmatic label, instructions should be associated with the relevant field, and validation errors must be both visible and announced to assistive technology.

After a failed submission, move focus to a clear error summary or the first invalid field. Preserve entered values where safe, explain how to correct the error and avoid relying only on color or an icon. On successful submission, provide a confirmation that is visible, announced and not dependent on a transient animation.

Checkout deserves extra care: payment errors, coupon messages, shipping changes and order confirmation must not be silently updated in a way that a keyboard or screen-reader user misses.

## Automated Regression Checks

Add automated checks where they prevent repeated structural mistakes:

- a browser test can check that a modal traps and returns focus;
- an accessibility scanner can flag missing labels, invalid ARIA and contrast regressions;
- a component test can assert keyboard actions for menus, tabs and accordions.

Treat automated results as signals, not a conformance certificate. Keep a short manual test set for complex flows and perform it before major releases. When a production accessibility issue is found, add the smallest repeatable test that would have detected it.

## Measuring Progress

Maintain an accessibility backlog with severity based on blocked user tasks. Track recurring component issues separately from one-off content defects. The goal is not a perfect score from one tool; it is fewer barriers in the journeys people need to complete.
