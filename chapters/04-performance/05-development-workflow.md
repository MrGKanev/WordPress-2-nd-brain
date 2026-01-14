# Development Workflow

## Overview

Professional WordPress development requires more than writing code—it demands a systematic approach to moving changes safely from idea to production. A mature workflow prevents the "it works on my machine" problem, catches bugs before users see them, and enables confident deployments.

The core insight: **the cost of fixing a bug increases exponentially the later you find it**. A typo caught in your editor costs seconds. The same typo found after deployment might cost hours of troubleshooting, customer complaints, and emergency fixes.

## The Environment Problem

### Why Multiple Environments?

WordPress stores configuration, content, and code in the same installation. This creates a fundamental tension: you need to experiment and break things to develop effectively, but you can't break your live site.

The solution is environment separation—maintaining distinct copies of your site for different purposes:

**Development** is your sandbox. Here you write code, test ideas, and intentionally break things. When something goes wrong (and it will), only you are affected. Development environments should mirror production closely enough that code working here will work there too, but be isolated enough that mistakes have no real consequences.

**Staging** bridges development and production. It's where you verify that changes work in an environment nearly identical to production, where clients can review changes before they go live, and where you can catch integration issues that didn't appear in development. Staging should have production-like data (anonymized if necessary) and identical server configuration.

**Production** is the live site. Changes here affect real users and real revenue. Production should receive only tested, approved changes, and those changes should be deployed through a repeatable, reversible process—never through manual edits.

### The "Works On My Machine" Problem

Without environment separation, developers often work directly on production or on setups that differ significantly from production. This leads to surprises: code that runs perfectly locally fails in production because PHP versions differ, extensions are missing, or server configurations conflict.

The fix is environment parity—making your development environment match production as closely as practical. Modern tools like Docker-based solutions (DDEV, Lando) and services like Local by Flywheel make this straightforward by packaging the entire server stack in a reproducible way.

### Choosing Local Development Tools

The WordPress ecosystem offers several approaches to local development:

**Local by Flywheel** dominates among general WordPress developers for good reason: it provides a polished GUI, handles SSL certificates automatically, and "just works" for most projects. Its limitations appear when you need non-standard configurations or have complex requirements.

**Docker-based tools** (DDEV, Lando, wp-env) offer flexibility at the cost of initial learning investment. They excel when you need to match specific production environments, work on multiple projects with conflicting requirements, or collaborate with teams who need identical setups. Once configured, they reproduce environments perfectly.

**Traditional stacks** (MAMP, XAMPP) still work but represent an older approach. They're fine for learning but lack the reproducibility and isolation that professional development demands.

Choose based on your constraints: Local for simplicity, Docker-based tools for precision and collaboration, traditional stacks only if you're already comfortable with them.

## Version Control Fundamentals

### Why Git Matters for WordPress

WordPress's file-based architecture makes version control particularly valuable. Without it, you're reduced to manual backups, "file-final-v2-FINAL.php" naming schemes, and no reliable way to understand what changed when something breaks.

Git provides:

**History**: Every change is recorded with who made it, when, and why. When something breaks, you can trace exactly what changed. When you need to understand why code works a certain way, the commit history explains the evolution.

**Collaboration**: Multiple developers can work simultaneously without overwriting each other's changes. Git's branching model lets people work independently and merge when ready.

**Reversibility**: Any change can be undone. Deployed a broken update? Revert to the previous commit. Need to remove a feature that was added months ago? Git makes it possible.

**Deployment**: Git enables automated deployment. Push to a branch, and servers can automatically pull changes—no FTP, no manual file copying, no forgetting to upload that one crucial file.

### What Belongs in Git

Not everything in a WordPress installation should be tracked. The principle: **track what you create, ignore what you can regenerate**.

**Track** custom themes, custom plugins, mu-plugins, and configuration files (with secrets removed). These represent your unique work that can't be recreated from elsewhere.

**Ignore** WordPress core (it can be downloaded), vendor dependencies (Composer reinstalls them), node_modules (npm reinstalls them), uploads (they're user content, not code), and cache files. Also ignore environment-specific files like `.env` that contain secrets or local configuration.

For most projects, you're tracking perhaps 5% of the files in a WordPress installation—but it's the 5% that matters most.

### Branching Strategy

How you organize branches depends on your team size and release cadence.

**Solo developers** can keep it simple: work on `main`, commit frequently, deploy when ready. The overhead of complex branching isn't worth it when you're the only contributor.

**Small teams** benefit from a develop/main split. The `develop` branch accumulates changes, `main` always reflects what's deployed. Feature branches keep work-in-progress separate from stable code.

**Larger teams or regulated environments** may need formal release branches, mandatory code reviews before merging, and staging branches that mirror pre-production environments. The complexity is justified when coordination costs exceed branching overhead.

Don't adopt complex workflows because they're "best practice"—adopt them when your actual problems require them.

### Git Submodules for Themes

When a theme becomes complex enough to warrant its own development lifecycle, Git submodules let you manage it as a separate repository while still including it in your main project. This is particularly useful when multiple WordPress installations share the same theme, or when the theme team works independently from the main site team.

Submodules work like pointers—your main repository doesn't contain the theme files directly, but instead references a specific commit in the theme's repository. When you clone the main project, Git fetches the theme from its own repository at the specified version.

**Why use submodules?** They solve the problem of having shared code that evolves independently. Without submodules, you'd either duplicate theme code across projects (making updates painful) or use some external synchronization system. Submodules make Git itself handle the coordination.

**The tradeoff:** Submodules add complexity. Team members must learn additional Git commands, and forgetting to update submodules is a common source of confusion. For simple projects with a single WordPress installation, keeping everything in one repository is usually simpler.

To extract an existing theme into its own repository, Git's filter-branch command rewrites history to include only the theme directory:

```bash
git filter-branch --prune-empty --subdirectory-filter wp-content/themes/yourtheme -- --all
git remote set-url origin git@github.com:yourorg/theme-repo.git
git push -u origin main
```

To add a theme repository as a submodule in your main project:

```bash
git submodule add git@github.com:yourorg/theme-repo.git wp-content/themes/yourtheme
git commit -m "Add theme as submodule"
```

When cloning a project that uses submodules, you need the `--recursive` flag to also fetch submodule contents. Otherwise you'll get empty directories where submodules should be:

```bash
git clone --recursive git@github.com:yourorg/main-repo.git
```

If you already cloned without `--recursive`, initialize and fetch submodules manually:

```bash
git submodule init && git submodule update
```

### Commit Message Standards

When you look back at a project's Git history months later, commit messages are your only guide to understanding what changed and why. Vague messages like "fixed stuff" or "updates" make the history useless. Consistent, descriptive messages transform the commit log into valuable documentation.

The Conventional Commits standard provides a structured format that both humans and automated tools can parse. Each commit message starts with a type (what kind of change), an optional scope (what part of the codebase), and a subject (what specifically changed). This consistency enables automated changelog generation, semantic versioning, and easier code review.

**Format:**

```
type(scope): subject

body (optional - explains the "why")

footer (optional - references issues, breaking changes)
```

**Types indicate the nature of the change:**

| Type | When to Use |
|------|-------------|
| `feat` | Adding new functionality users will notice |
| `fix` | Correcting broken behavior |
| `docs` | Documentation changes only |
| `style` | Code formatting, whitespace, missing semicolons—no logic changes |
| `refactor` | Restructuring code without changing its behavior |
| `perf` | Performance improvements |
| `test` | Adding or modifying tests |
| `chore` | Build process, dependencies, tooling |

**The scope** narrows down which part of the codebase changed. For WordPress themes, you might use scopes like `header`, `checkout`, `api`, or `admin`. This helps when scanning history for changes to a specific feature.

**Good commit messages:**

```
feat(checkout): add guest checkout option

fix(header): resolve mobile menu overlap on iOS

perf(images): implement lazy loading for product galleries
```

Tools like commitlint can enforce these standards automatically, rejecting commits that don't follow the format. This is especially valuable on teams where consistent habits vary.

## CSS Build Pipeline

Writing CSS directly in large projects becomes unwieldy—you end up repeating colors and spacing values, duplicating media queries, and struggling to organize thousands of lines of styles. CSS preprocessors like SCSS solve these problems by adding variables, nesting, mixins, and file organization to your stylesheet workflow.

The tradeoff is a build step. Your browser doesn't understand SCSS; it needs plain CSS. You write SCSS, a compiler transforms it to CSS, and optionally a minifier compresses the output. This pipeline runs during development and before deployment.

### Why SCSS?

SCSS (Sassy CSS) extends CSS with programming-like features while remaining syntactically similar to regular CSS. Any valid CSS is also valid SCSS, so you can adopt it gradually without rewriting existing styles.

**Variables** eliminate repetition. Define a color once, reference it everywhere. Change the variable, and every usage updates automatically:

```scss
$primary-color: #3a7bd5;
$spacing-unit: 8px;

.button {
    background: $primary-color;
    padding: $spacing-unit * 2;
}
```

**Nesting** mirrors HTML structure, making stylesheets more readable. Instead of repeating parent selectors, nest child styles within them:

```scss
.nav {
    background: white;

    .nav-item {
        padding: 1rem;

        &:hover {
            background: #f0f0f0;
        }
    }
}
```

**Partials and imports** split styles into logical files. A `_buttons.scss` partial contains only button styles. The main `style.scss` imports all partials, and the compiler combines them into one CSS file.

### SCSS Workflow

A typical project structure separates source files from compiled output. Files starting with underscore (like `_variables.scss`) are partials—they don't compile to separate CSS files but get included into the main stylesheet. This convention helps organize styles by purpose: variables in one file, mixins in another, component styles in their own folder.

```
theme/
├── scss/
│   ├── _variables.scss      (colors, fonts, spacing)
│   ├── _mixins.scss         (reusable patterns)
│   ├── _base.scss           (resets, typography)
│   ├── components/
│   │   ├── _header.scss
│   │   └── _footer.scss
│   └── style.scss           (imports all partials)
├── css/
│   ├── style.css            (compiled, human-readable)
│   └── style.min.css        (minified for production)
└── package.json
```

NPM scripts automate the build process. The `build:css` script compiles SCSS to CSS. The `build:min` script runs PostCSS to minify the output. The `watch` script recompiles automatically when files change—essential during development.

```json
{
  "scripts": {
    "build:css": "sass scss/style.scss:css/style.css",
    "build:min": "postcss css/style.css --use cssnano -o css/style.min.css",
    "build": "npm run build:css && npm run build:min",
    "watch": "sass --watch scss/style.scss:css/style.css"
  },
  "devDependencies": {
    "sass": "^1.50.0",
    "postcss-cli": "^10.0.0",
    "cssnano": "^5.1.0",
    "postcss-combine-media-query": "^1.0.1"
  }
}
```

Run `npm run build` before deployment. Run `npm run watch` during development to see changes immediately without manual compilation.

### PostCSS Processing

PostCSS is a tool for transforming CSS with JavaScript plugins. Unlike SCSS which extends CSS syntax, PostCSS works on standard CSS and modifies it programmatically. You can chain multiple plugins to achieve different optimizations.

Common PostCSS plugins for WordPress themes:
- **cssnano** minifies CSS by removing whitespace, shortening colors, and eliminating redundant rules
- **autoprefixer** adds vendor prefixes for browser compatibility (so you write standard CSS and it adds `-webkit-`, `-moz-` etc. where needed)
- **postcss-combine-media-query** merges duplicate media queries that appear throughout your stylesheet into single blocks, reducing file size

PostCSS plugins transform compiled CSS:

**postcss.config.js:**

```javascript
module.exports = {
    plugins: [
        require('postcss-combine-media-query'),  // Combine duplicate media queries
        require('cssnano')({                     // Minification
            preset: ['default', {
                discardComments: { removeAll: true }
            }]
        })
    ]
};
```

**Processing command:**

```bash
postcss css/style.css --no-map --use postcss-combine-media-query --use cssnano -o css/style.min.css
```

### IDE File Watchers

PhpStorm/WebStorm can compile automatically on save:

**SCSS watcher:**
- Program: `sass`
- Arguments: `$FileName$:$FileNameWithoutExtension$.css`
- Output paths: `$FileNameWithoutExtension$.css:$FileNameWithoutExtension$.css.map`

**PostCSS watcher (on .css files):**
- Program: `postcss`
- Arguments: `--no-map --use cssnano -o $FileNameWithoutExtension$.min.css $FileName$`
- Output paths: `$FileNameWithoutExtension$.min.css`

### .gitignore for Build Files

Don't track generated files:

```gitignore
# Compiled CSS (track SCSS source instead)
/css/*.css
/css/*.css.map

# Node
/node_modules/

# But DO track minified production file if needed for deployment without build step
# !/css/style.min.css
```

## Code Quality Tools

Code quality tools catch mistakes before they become bugs. They examine your code without running it, looking for common errors, style inconsistencies, and potential problems. Running these tools regularly—especially before committing—prevents technical debt from accumulating.

Two tools dominate PHP quality checking: **PHP_CodeSniffer** enforces coding standards (consistent formatting, naming conventions), while **PHPStan** performs static analysis (finds bugs, type errors, unreachable code). They complement each other—CodeSniffer focuses on style, PHPStan focuses on correctness.

### PHP_CodeSniffer (PHPCS)

PHP_CodeSniffer reads your code and reports violations of coding standards. The WordPress coding standards define how WordPress core and community plugins should be formatted: spaces vs tabs, brace placement, naming conventions, and hundreds of other rules.

Why bother? Consistent code is easier to read, review, and maintain. When everyone follows the same standards, you spend less mental energy parsing unfamiliar formatting and more time understanding logic.

Install PHPCS globally so it's available across all projects. The WordPress Coding Standards ruleset (WPCS) teaches PHPCS WordPress-specific rules:

```bash
composer global require squizlabs/php_codesniffer
composer global require wp-coding-standards/wpcs
composer global require phpcsstandards/phpcsextra
composer global require dealerdirect/phpcodesniffer-composer-installer
```

Run PHPCS against your theme or plugin directory. It reports each violation with file, line number, and explanation:

```bash
phpcs --standard=WordPress wp-content/themes/yourtheme/
```

Many violations can be fixed automatically. PHPCBF (PHP Code Beautifier and Fixer) reformats code to match standards:

```bash
phpcbf --standard=WordPress wp-content/themes/yourtheme/
```

Not everything can be auto-fixed—logical issues and some formatting decisions require human judgment. Run PHPCS again after PHPCBF to see what remains.

**Custom ruleset (phpcs.xml):**

```xml
<?xml version="1.0"?>
<ruleset name="Theme Standards">
    <description>Custom coding standards for theme</description>

    <file>.</file>
    <exclude-pattern>/vendor/</exclude-pattern>
    <exclude-pattern>/node_modules/</exclude-pattern>

    <arg name="extensions" value="php"/>
    <arg value="ps"/>

    <rule ref="WordPress">
        <exclude name="WordPress.Files.FileName.InvalidClassFileName"/>
    </rule>
</ruleset>
```

### PHPStan (Static Analysis)

While PHPCS checks how your code looks, PHPStan checks what your code does. It performs static analysis—examining code without executing it—to find bugs that would otherwise appear only at runtime.

PHPStan catches errors like: calling methods on potentially null values, passing wrong argument types, using undefined variables, unreachable code branches, and hundreds of other patterns that indicate bugs. The stricter your PHPStan level (1-9), the more issues it reports.

WordPress's dynamic nature complicates static analysis. Functions like `apply_filters()` accept variable arguments, global variables appear throughout, and hooks make control flow hard to trace. The phpstan-wordpress extension teaches PHPStan about WordPress-specific patterns, reducing false positives.

```bash
composer global require phpstan/phpstan
composer global require szepeviktor/phpstan-wordpress
```

Configuration lives in `phpstan.neon`. The `level` setting controls strictness—start at level 5 and increase as you fix issues. The `paths` setting specifies what to analyze. The `scanDirectories` setting tells PHPStan about external code (like WooCommerce) that your code references, so it understands those function signatures.

```yaml
includes:
    - vendor/szepeviktor/phpstan-wordpress/extension.neon

parameters:
    level: 5
    paths:
        - wp-content/themes/yourtheme
        - wp-content/plugins/yourplugin

    scanDirectories:
        - wp-content/plugins/woocommerce

    ignoreErrors:
        - '#^Function apply_filters invoked with \d+ parameters, 2 required\.$#'
```

The `ignoreErrors` section handles WordPress patterns that PHPStan misunderstands. WordPress's `apply_filters()` accepts unlimited arguments, but PHPStan sees the function signature showing only two required parameters. The regex pattern tells PHPStan to ignore this specific false positive.

Run analysis with:

```bash
phpstan analyse
```

Fix reported issues iteratively. Some represent real bugs you'll be grateful to catch before production.

### Pre-commit Hooks

Quality tools only help if you actually run them. Pre-commit hooks automate this by running checks every time you try to commit. If checks fail, the commit is rejected until you fix the problems.

This shifts bug detection earlier—catching issues when you're still focused on the code rather than days later during code review or (worse) after deployment. The few seconds spent on each commit saves hours of debugging later.

**Husky** is a popular Node.js tool for managing Git hooks. It integrates well with npm scripts:

```bash
npm install husky --save-dev
npx husky install
npx husky add .husky/pre-commit "npm run lint"
```

For projects without Node.js, write Git hooks directly as shell scripts. Git looks for executable files in `.git/hooks/`. Create `.git/hooks/pre-commit` with your checks:

```bash
#!/bin/bash

# Only check PHP files being committed (not entire project)
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep ".php$")

if [ -n "$STAGED_FILES" ]; then
    phpcs --standard=WordPress $STAGED_FILES
    if [ $? -ne 0 ]; then
        echo "PHPCS errors found. Fix them before committing."
        exit 1
    fi
fi
```

Make the hook executable with `chmod +x .git/hooks/pre-commit`. Now every commit runs PHPCS on changed PHP files.
```

### Composer Scripts for Development

**composer.json:**

```json
{
    "scripts": {
        "lint": "phpcs --standard=phpcs.xml",
        "lint:fix": "phpcbf --standard=phpcs.xml",
        "analyse": "phpstan analyse",
        "test": "phpunit",
        "check": [
            "@lint",
            "@analyse"
        ]
    }
}
```

**Usage:**

```bash
composer check  # Run all quality checks
composer lint   # Just coding standards
composer analyse # Just static analysis
```

## Database Synchronization

### The Database Challenge

Code lives in files that Git tracks beautifully. But WordPress stores content, settings, and configuration in the database. This creates synchronization headaches: your local site has test content, staging has client-approved content, production has real content. Keeping them aligned is genuinely hard.

The challenge compounds because WordPress serializes PHP arrays and objects into database fields. A simple search-and-replace to change URLs breaks serialized data because string lengths are stored alongside content. Tools like WP-CLI's `search-replace` command handle this correctly; manual SQL doesn't.

### Synchronization Strategies

**Pull production down** works for most projects. Periodically export production's database, import it locally, run search-replace to fix URLs. This keeps your development data realistic. The downside: you may overwrite local test configurations you wanted to keep.

**Push content up** works when staging is the source of truth during development. Build the site on staging with client input, then push that database to production at launch. This reverses the normal flow but makes sense for new site builds.

**Merge selectively** handles active sites where you can't overwrite production content but need configuration changes. Export specific tables (like `wp_options` for settings), import only those. This requires understanding WordPress's database schema.

**Avoid bidirectional sync** if possible. Trying to merge changes from both directions leads to conflicts and data loss. Establish one environment as the source of truth for content at any given time.

### Content Workflow Decisions

Before starting a project, decide: where does content get created? During development, staging often makes sense—clients can add real content while developers build features. After launch, production becomes the source, and content flows downward for testing.

Trying to create content in multiple places simultaneously causes pain. The database isn't designed for merge conflicts the way Git is.

## Deployment Methods

### The Deployment Spectrum

Deployment approaches range from simple to sophisticated:

**Manual deployment** means connecting via FTP/SFTP, uploading changed files, and running any necessary commands. It's simple and works for small sites with infrequent changes. The risks: forgetting files, uploading to wrong directories, no automatic rollback, no audit trail.

**Git-based deployment** uses Git as both version control and deployment mechanism. Push to a branch, the server pulls changes. This adds audit trails and repeatability but still requires manual steps (pull, run migrations, clear cache).

**Automated CI/CD** takes Git-based deployment further. Push triggers a pipeline that runs tests, builds assets, deploys to staging automatically, and (after approval) to production. This is the professional standard for serious projects but requires initial investment to configure.

The right choice depends on project scale, team size, and how often you deploy. A simple blog updated monthly doesn't need CI/CD. An e-commerce site with daily deploys absolutely does.

### Deployment Safety Practices

Regardless of method, certain practices reduce deployment risk:

**Never edit production directly**. Changes should flow through your development process, not through the WordPress admin editor or direct file edits. Direct edits bypass all your safety measures.

**Deploy small changes frequently** rather than large changes rarely. Small deployments are easier to test, easier to understand, and easier to rollback. If something breaks, you know exactly what changed.

**Have a rollback plan** before you deploy. Know exactly how to revert if something goes wrong. For Git-based deploys, this might be `git checkout` to a previous commit. For other methods, ensure you have recent backups.

**Deploy during low-traffic periods** when possible. If something does go wrong, fewer users are affected, and you have more time to fix it.

### Maintenance Mode

For changes that might briefly break the site—database migrations, significant file changes—WordPress's maintenance mode prevents users from seeing partial updates or errors.

WP-CLI's `wp maintenance-mode activate` creates the `.maintenance` file that triggers WordPress's built-in "briefly unavailable" message. Activate it before risky operations, deactivate when complete. Automated deployments should handle this automatically.

Don't leave sites in maintenance mode longer than necessary. Users encountering it repeatedly lose trust.

## Testing Approaches

### The Testing Pyramid

Testing isn't optional for professional development. The question is what to test and how.

**Manual testing**—clicking through features, checking layouts, trying edge cases—remains essential. Humans catch usability issues, visual bugs, and "this feels wrong" problems that automated tests miss. But manual testing is slow, expensive, and doesn't scale.

**Automated tests** complement manual testing by catching regressions—things that worked before but broke with recent changes. Unit tests verify individual functions work correctly. Integration tests verify components work together. End-to-end tests verify complete user flows work in real browsers.

For WordPress projects, focus automated testing effort where it provides the most value: custom code with complex logic, critical user flows (checkout, registration, form submissions), and integrations with external services.

### WordPress-Specific Testing Considerations

WordPress's plugin architecture complicates testing. Your code runs within WordPress, using WordPress functions, potentially conflicting with other plugins. Testing in isolation may miss issues that only appear in the full environment.

The WP_UnitTestCase class provides a test harness that boots WordPress, sets up a test database, and resets between tests. It's heavier than pure unit tests but catches WordPress-specific issues.

For critical flows like e-commerce checkout, browser-based testing tools (Playwright, Cypress) simulate real user interactions. They're slower to write and run but catch problems that nothing else can.

### Testing Reality

Most WordPress projects have little or no automated testing. This is unfortunate but understandable—the ecosystem developed before testing was common, and retrofitting tests is hard.

For new projects, start with tests for critical paths. For existing projects, add tests when fixing bugs (prevent regressions) and when adding complex features. Gradual improvement beats no improvement.

## Risk-Based Workflow

### Not All Changes Are Equal

Applying the same process to every change wastes time and creates bottlenecks. A typo fix doesn't need the same scrutiny as a payment system rewrite.

Assess changes by risk:

**Low-risk changes** (typos, minor CSS tweaks, content updates) can often go straight to production with basic verification. The cost of a mistake is minimal, and extensive process adds more burden than protection.

**Medium-risk changes** (plugin updates, template modifications, configuration changes) benefit from staging verification but don't require exhaustive testing. Quick smoke tests on critical functionality suffice.

**High-risk changes** (major features, database changes, integrations with external services, anything touching payments) deserve full process: development, testing, staging verification, client approval, documented rollback plan, deployment during low-traffic period.

The key is honest assessment. If you're uncertain about risk, err toward more caution. Confidence comes from experience with specific codebases and changes.

### Recovery Preparation

No amount of process guarantees error-free deployments. What matters is recovering quickly when things go wrong.

Before any significant deployment:
- Verify backups are current and restorable
- Document exact rollback steps
- Know who to contact if you can't fix it alone
- Have access credentials ready (don't discover your SSH key expired mid-crisis)

The goal isn't preventing all failures—it's minimizing their impact when they occur.

## Plugin and Theme Updates

### The Update Dilemma

WordPress's ecosystem depends on regular updates for security and functionality. But updates also introduce risk: new bugs, compatibility breaks, changed behavior. Both updating and not updating carry risk.

**Delaying updates** increases security exposure. Known vulnerabilities in outdated plugins are actively exploited. The longer you wait, the more vulnerable you become.

**Immediate updates** may introduce bugs before they're discovered and patched. Being first to update means being first to hit new problems.

A balanced approach: update regularly but not immediately. For most sites, weekly update reviews strike a good balance. Security patches warrant faster attention—within days, not weeks.

### Safe Update Process

Before updating:
1. Create a database backup you've verified you can restore
2. Check the plugin/theme changelog for breaking changes
3. If available, test updates on staging first

During updates:
1. Update one thing at a time (isolates problems to specific updates)
2. Verify basic functionality after each update
3. Check for error messages in debug logs

After updates:
1. Clear caches (old cached code may conflict with updates)
2. Monitor for errors over the following hours/days
3. Keep backups until you're confident in stability

### Handling Update Failures

When an update breaks something:
1. Don't panic—you have backups
2. Identify the problem (error logs, visual inspection)
3. If serious, rollback immediately (restore backup or reinstall previous version)
4. Report the issue to plugin developers
5. Wait for a fix or find an alternative

Most update problems are compatibility issues between plugins or with specific PHP versions. The WordPress ecosystem is large and not always perfectly coordinated.

## Team Collaboration

### Working with Non-Developers

WordPress projects often involve people with different technical backgrounds: developers, designers, content creators, project managers, clients. Your workflow must accommodate them.

**Content creators** need access to production to publish, but shouldn't be able to install plugins or modify code. WordPress's role system handles this.

**Clients** reviewing work should use staging, not production. Give them limited accounts that can view and comment but not change configurations.

**External developers** (freelancers, agencies) need enough access to do their work but not so much they can cause irreversible damage. Separate accounts, limited permissions, and monitoring what they change.

Clear communication about what environment to use and what actions are acceptable prevents accidents.

### Documentation Requirements

Workflows only help if people follow them. Document:

- How to set up a local development environment
- How to deploy changes (step by step)
- Who approves changes before deployment
- How to handle emergencies
- Who to contact when something breaks

Documentation doesn't need to be elaborate. A single markdown file in the repository, kept current, serves most projects.

## Further Reading

- [WP-CLI Essentials](../02-maintenance/03-wp-cli-essentials.md) - Command-line tools for deployment and maintenance
- [Database Optimization](./07-database-optimizations.md) - Understanding WordPress's database for safer migrations
- [Debugging and Profiling](./10-debugging-profiling.md) - Finding problems when deployments go wrong
