# Building The Book

## Requirements

- [Rust](https://rustup.rs/) (for installing mdBook via cargo)
- Or download mdBook binary directly from [releases](https://github.com/rust-lang/mdBook/releases)

## Installation

```bash
# Option 1: Install via cargo (requires Rust)
cargo install mdbook

# Option 2: On macOS with Homebrew
brew install mdbook

# Option 3: Download binary from GitHub releases
# https://github.com/rust-lang/mdBook/releases
```

## Building HTML

```bash
# Build the book (outputs to /book directory)
mdbook build

# Serve locally with hot-reload (great for development)
mdbook serve
# Then open http://localhost:3000

# Serve on a specific port
mdbook serve -p 8080
```

## Building PDF

```bash
# Install PDF extension
cargo install mdbook-pdf

# Generate PDF (requires Chrome/Chromium installed)
mdbook-pdf

# The PDF will be created as book.pdf in the root directory
```

**Note:** mdbook-pdf uses headless Chrome for rendering. Make sure Chrome or Chromium is installed.

## Project Structure

```
wordpress-2nd-brain/
├── book.toml              # mdBook configuration
├── SUMMARY.md             # Table of contents (defines structure)
├── README.md              # Book introduction
├── chapters/              # All content
│   ├── 01-wordpress-fundamentals/
│   ├── 02-maintenance/
│   ├── 03-security/
│   ├── 04-performance/
│   ├── 05-seo/
│   ├── 06-e-commerce/
│   ├── 07-theme-development/
│   └── 08-plugin-development/
└── book/                  # Generated output (gitignored)
```

## Editing Content

1. **Add new page:** Create `.md` file in appropriate chapter folder
2. **Update navigation:** Add entry to `SUMMARY.md`
3. **Preview changes:** Run `mdbook serve` and check in browser
4. **Cross-references:** Use relative paths (`../other-chapter/file.md`)

## Common Issues

**"SUMMARY.md not found"**
- Make sure you're in the project root directory

**PDF generation fails**
- Ensure Chrome/Chromium is installed
- Try running with `--verbose` flag for more details

**Changes not appearing**
- Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
- Check SUMMARY.md includes the new file

## CI/CD Deployment

For GitHub Pages deployment, add to `.github/workflows/deploy.yml`:

```yaml
name: Deploy mdBook
on:
  push:
    branches: [master]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup mdBook
        uses: peaceiris/actions-mdbook@v1
        with:
          mdbook-version: 'latest'
      - run: mdbook build
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./book
```

## Useful mdBook Commands

```bash
mdbook build      # Build once
mdbook serve      # Build + serve + watch for changes
mdbook clean      # Remove generated files
mdbook test       # Test Rust code examples (if any)
mdbook init       # Initialize new book (not needed here)
```

## Further Reading

- [mdBook Documentation](https://rust-lang.github.io/mdBook/)
- [mdBook User Guide](https://rust-lang.github.io/mdBook/guide/creating.html)
