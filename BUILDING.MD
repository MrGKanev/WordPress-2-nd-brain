## Building The Book

To generate a PDF version:

```bash
# Install mdBook and the PDF extension if you haven't already
cargo install mdbook
cargo install mdbook-pdf

# Generate the PDF
mdbook-pdf
```

The PDF will be created as `book.pdf` in the root directory.
