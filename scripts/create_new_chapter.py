#!/usr/bin/env python3
"""
create_new_chapter.py - Create a new chapter with the proper structure
This script helps you create a new chapter or section with the proper structure
for your mdBook project.
"""

import os
import argparse
from pathlib import Path

def create_chapter(book_root, chapter_name, chapter_number=None, sections=None):
    """
    Create a new chapter directory with README.md and optional section files.
    
    Args:
        book_root: Root directory of the book
        chapter_name: Name of the chapter (will be used in the title)
        chapter_number: Chapter number (for ordering)
        sections: List of section names to create
    """
    book_root = Path(book_root).resolve()
    chapters_dir = book_root / 'chapters'
    
    # Create chapters directory if it doesn't exist
    if not chapters_dir.exists():
        chapters_dir.mkdir(parents=True)
        print(f"Created chapters directory at {chapters_dir}")
    
    # Determine chapter number if not provided
    if chapter_number is None:
        existing_chapters = [d for d in chapters_dir.iterdir() if d.is_dir()]
        if existing_chapters:
            # Extract numbers from existing chapter directories
            numbers = []
            for chapter in existing_chapters:
                try:
                    # Extract number from directory name (e.g., "01-introduction" → 1)
                    num = int(chapter.name.split('-')[0])
                    numbers.append(num)
                except (ValueError, IndexError):
                    pass
            
            chapter_number = max(numbers) + 1 if numbers else 1
        else:
            chapter_number = 1
    
    # Format chapter number with leading zeros
    formatted_number = f"{chapter_number:02d}"
    
    # Format chapter name for directory (lowercase, replace spaces with hyphens)
    formatted_name = chapter_name.lower().replace(' ', '-')
    
    # Create chapter directory
    chapter_dir = chapters_dir / f"{formatted_number}-{formatted_name}"
    chapter_dir.mkdir(exist_ok=True)
    print(f"Created chapter directory at {chapter_dir}")
    
    # Create images directory for this chapter if it doesn't exist
    images_dir = book_root / 'images' / f"chapter-{formatted_number}"
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created images directory at {images_dir}")
    
    # Create README.md with chapter title
    readme_path = chapter_dir / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"# {chapter_name}\n\n")
        f.write(f"This is the content for Chapter {chapter_number}: {chapter_name}.\n\n")
        f.write("## Overview\n\n")
        f.write("Write your chapter overview here.\n")
    
    print(f"Created chapter README at {readme_path}")
    
    # Create section files if provided
    if sections:
        for i, section_name in enumerate(sections, 1):
            # Format section name for filename
            formatted_section_name = section_name.lower().replace(' ', '-')
            section_path = chapter_dir / f"{i:02d}-{formatted_section_name}.md"
            
            with open(section_path, 'w', encoding='utf-8') as f:
                f.write(f"# {section_name}\n\n")
                f.write(f"This is a section in Chapter {chapter_number}: {chapter_name}.\n\n")
                f.write("Write your section content here.\n")
            
            print(f"Created section file at {section_path}")
    
    print(f"\nChapter {formatted_number}-{formatted_name} successfully created!")
    print("Don't forget to run the generate_summary.py script to update your SUMMARY.md")

def main():
    parser = argparse.ArgumentParser(description="Create a new chapter for mdBook")
    parser.add_argument('chapter_name', type=str, help='Name of the chapter')
    parser.add_argument('--book-root', type=str, default='.', 
                        help='Root directory of the book (default: current directory)')
    parser.add_argument('--chapter-number', type=int, 
                        help='Chapter number (default: automatically determined)')
    parser.add_argument('--sections', type=str, nargs='+', 
                        help='Names of sections to create within the chapter')
    
    args = parser.parse_args()
    
    create_chapter(args.book_root, args.chapter_name, args.chapter_number, args.sections)

if __name__ == "__main__":
    main()