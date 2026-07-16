# WordPress Second Brain

A personal knowledge repository containing everything I've learned about WordPress development, organized as a searchable reference book.

## Guidelines

**Test before you deploy.** The code and configurations in this book are meant for learning and reference. Always test on a staging environment before applying changes to production sites. We can't be responsible for broken sites - but we can help you avoid that by encouraging safe practices.

**Attribution matters.** When content, insights, or code examples come from external sources, we do our best to credit the original authors. If you notice something that should be attributed, please open an issue.

**Context is everything.** What works for one WordPress site may not work for another. Server configurations, plugin combinations, and traffic patterns all affect outcomes. Treat recommendations as starting points, not universal truths.

**Outdated doesn't mean wrong.** Some content dates back to 2017. While WordPress evolves, many fundamentals remain valid. We mark known outdated sections, but always check version compatibility for code examples.

**Contributions welcome.** Found an error? Have a better approach? Know something we don't? Pull requests and issues are appreciated. This is a living document.


## About This Book

This book serves as my "second brain" for WordPress maintenance, development and mostly everything else. It contains:

- Plugin development best practices
- WordPress API reference notes
- Code snippets and solutions to common problems
- Architecture patterns and decisions
- Security considerations and implementation techniques
- Performance optimization strategies
- Hack tips and tricks
- Deployment and hosting considerations
- SEO and marketing strategies
- Theme development guidelines
- Customization techniques
- Troubleshooting and debugging tips
- Community resources and links
- And much more!

## How To Use This Book

This repository uses the mdBook system to organize content into chapters and sections. You can:

1. Browse chapters in the `chapters` directory
2. Search for specific topics using the search function
3. Generate a PDF version for offline reference
4. Contribute additions by creating a pull request

## Choose Your Path

The book is a reference, so you do not need to read it cover to cover. Start
with the path closest to the work you are doing.

### I maintain a WordPress site

Start with [WordPress Fundamentals](chapters/01-wordpress-fundamentals/README.md), then read [Maintenance](chapters/02-maintenance/README.md) and [Security](chapters/03-security/README.md). Use the Performance and SEO chapters when a measured problem or goal requires them.

### I build client sites

Read Fundamentals, [Theme Development](chapters/07-theme-development/README.md), Maintenance, Security and [WordPress Optimization](chapters/04-performance/README.md). Before launch, use the checklists in the maintenance and security introductions.

### I build plugins or integrations

Read Fundamentals, [WordPress Plugin Architecture](chapters/08-plugin-development/README.md) and Security first. Add [E-commerce with WordPress](chapters/06-e-commerce/README.md) when the plugin touches WooCommerce.

### I need to improve an existing site

Measure before changing anything. Begin with the debugging and profiling material in [WordPress Optimization](chapters/04-performance/README.md), then make the smallest targeted change and test it on staging.

## Reliability Notes

WordPress, PHP, WooCommerce and browser APIs change continually. Treat version-sensitive advice as a starting point, verify the linked official documentation, and test every production-impacting change on staging. New and substantially revised pages should include a review date, tested versions and a risk level; see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This repository is licensed under the MIT License - see the LICENSE file for details.
