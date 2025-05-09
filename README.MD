# Second Brain Book Template

A GitHub template for creating and publishing books as PDFs using Markdown and mdBook. This template is designed to be used as a second brain concept, making it easy to organize your knowledge into books.

## Features

- **Markdown-Based**: Write your content in simple Markdown
- **Automated PDF Generation**: Automatically generate PDFs when you push changes
- **Version Control**: Keep track of your book's evolution with Git
- **Organized Structure**: Chapters and sections are neatly organized
- **Automated Table of Contents**: Automatically generate a table of contents (SUMMARY.md)
- **Customizable Styling**: Easily adjust the appearance of your PDF

## Getting Started

### 1. Create a New Repository

Use this repository as a template to create your own book repository:

1. Click the "Use this template" button
2. Name your new repository
3. Clone your new repository to your local machine

### 2. Customize Your Book

1. Edit `book.toml` to set your book's title, author, and other metadata
2. Edit `src/_markdown_pdf_config.yml` to set additional PDF metadata
3. Customize `theme/pdf.css` if you want to change the styling

### 3. Create Your First Chapter

```bash
python scripts/create_new_chapter.py "My First Chapter" --sections "Introduction" "Main Content" "Conclusion"
```

This will create:

- A new chapter directory with the proper numbering
- A README.md file for the chapter introduction
- Individual files for each section
- An images directory for this chapter

### 4. Generate the Table of Contents

After adding or modifying chapters, generate the SUMMARY.md file:

```bash
python scripts/generate_summary.py
```

### 5. Preview Your Book Locally

To preview your book locally, install mdBook and run:

```bash
mdbook serve
```

### 6. Build PDF Manually

To build the PDF manually:

```bash
mdbook-pdf
```

The PDF will be generated in the root directory as `book.pdf`.

### 7. Commit and Push

When you commit and push your changes to GitHub, the GitHub Actions workflow will automatically:

1. Generate the SUMMARY.md file
2. Build the PDF
3. Create a new release with the PDF attached
4. Organize the PDFs by date

## Directory Structure

```
your-book/
├── .github/workflows/     # GitHub Actions workflow
├── chapters/              # Book chapters
│   ├── 01-chapter-name/   # Chapter directory
│   │   ├── README.md      # Chapter introduction
│   │   └── 01-section.md  # Section file
├── images/                # Images used in the book
│   └── chapter-01/        # Images for chapter 1
├── scripts/               # Utility scripts
├── src/                   # Source files
├── theme/                 # Custom styling
├── book.toml              # mdBook configuration
└── SUMMARY.md             # Table of contents (auto-generated)
```

## Helpful Scripts

### Create New Chapter

```bash
python scripts/create_new_chapter.py "Chapter Name" --sections "Section 1" "Section 2"
```

### Generate SUMMARY.md

```bash
python scripts/generate_summary.py
```

### Organize PDFs

```bash
python scripts/organize_pdf.py book.pdf
```

## Customization

### Changing the PDF Appearance

Edit `theme/pdf.css` to customize the appearance of your PDF.

### Adding a Cover Image

Add a cover image at `images/cover.png` and it will be automatically used as your book cover.

