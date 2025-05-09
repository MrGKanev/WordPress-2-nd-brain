#!/usr/bin/env python3
"""
generate_summary.py - Automatically generate SUMMARY.md for mdBook
This script walks through your book's directory structure and creates
a SUMMARY.md file based on the markdown files it finds.
"""

import os
import re
from pathlib import Path
import argparse

def extract_title(file_path):
    """Extract the title from a markdown file (first # heading)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for the first heading
            match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if match:
                return match.group(1)
            
            # If no heading found, use the filename without extension
            return os.path.splitext(os.path.basename(file_path))[0].replace('-', ' ').title()
    except Exception as e:
        print(f"Warning: Could not extract title from {file_path}: {e}")
        return os.path.splitext(os.path.basename(file_path))[0].replace('-', ' ').title()

def is_excluded(path, exclude_patterns):
    """Check if the path matches any exclusion pattern."""
    for pattern in exclude_patterns:
        if re.search(pattern, str(path)):
            return True
    return False

def generate_summary(book_root, output_file, exclude=None, indent_level=0):
    """
    Generate SUMMARY.md content recursively by walking through the book's directory structure.
    """
    if exclude is None:
        exclude = [r'/\.', r'/_', r'node_modules', r'book$', r'SUMMARY\.md$']
    
    book_root = Path(book_root).resolve()
    chapters_dir = book_root / 'chapters'
    
    # Start with the title
    content = ["# Summary\n\n"]
    
    # Add README.md (introduction) if it exists
    readme_path = book_root / 'README.md'
    if readme_path.exists():
        title = extract_title(readme_path)
        content.append(f"* [{title}](README.md)\n")
    
    # If chapters directory exists, process it
    if chapters_dir.exists() and chapters_dir.is_dir():
        # Get all chapter directories sorted numerically
        chapter_dirs = sorted([d for d in chapters_dir.iterdir() if d.is_dir() and not is_excluded(d, exclude)])
        
        for chapter_dir in chapter_dirs:
            # Find the README.md or main chapter file
            chapter_readme = chapter_dir / 'README.md'
            if chapter_readme.exists():
                chapter_title = extract_title(chapter_readme)
                chapter_path = chapter_readme.relative_to(book_root)
                content.append(f"* [{chapter_title}]({chapter_path})\n")
                
                # Find all markdown files in this chapter directory, excluding README.md
                section_files = sorted([f for f in chapter_dir.glob('*.md') 
                                       if f.name != 'README.md' and not is_excluded(f, exclude)])
                
                for section_file in section_files:
                    section_title = extract_title(section_file)
                    section_path = section_file.relative_to(book_root)
                    content.append(f"  * [{section_title}]({section_path})\n")
            else:
                # If no README.md, use all markdown files as sections
                md_files = sorted([f for f in chapter_dir.glob('*.md') if not is_excluded(f, exclude)])
                if md_files:
                    # Use the directory name as the chapter title
                    chapter_title = chapter_dir.name.replace('-', ' ').title()
                    content.append(f"* [{chapter_title}]\n")
                    
                    for md_file in md_files:
                        section_title = extract_title(md_file)
                        section_path = md_file.relative_to(book_root)
                        content.append(f"  * [{section_title}]({section_path})\n")
    else:
        # If no chapters directory, just find all markdown files in the root
        md_files = sorted([f for f in book_root.glob('*.md') 
                           if f.name != 'README.md' and f.name != 'SUMMARY.md' and not is_excluded(f, exclude)])
        
        for md_file in md_files:
            title = extract_title(md_file)
            path = md_file.relative_to(book_root)
            content.append(f"* [{title}]({path})\n")
    
    # Write the content to the SUMMARY.md file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print(f"Successfully generated {output_file}")
    return content

def main():
    parser = argparse.ArgumentParser(description="Generate SUMMARY.md for mdBook")
    parser.add_argument('--book-root', type=str, default='.', 
                        help='Root directory of the book (default: current directory)')
    parser.add_argument('--output', type=str, default='SUMMARY.md',
                        help='Output file path (default: SUMMARY.md in book root)')
    parser.add_argument('--exclude', type=str, nargs='+', 
                        default=[r'/\.', r'/_', r'node_modules', r'book$', r'SUMMARY\.md$'],
                        help='Regex patterns to exclude from processing')
    
    args = parser.parse_args()
    
    book_root = Path(args.book_root).resolve()
    output_file = book_root / args.output
    
    generate_summary(book_root, output_file, args.exclude)

if __name__ == "__main__":
    main()