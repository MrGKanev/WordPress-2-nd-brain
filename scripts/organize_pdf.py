#!/usr/bin/env python3
"""
organize_pdf.py - Organize the generated PDF by date
This script takes the generated PDF, renames it with the current date,
and moves it to an organized folder structure.
"""

import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path

def organize_pdf(pdf_path, output_dir="./published_pdfs", add_version=True):
    """
    Organize the generated PDF by date.
    
    Args:
        pdf_path: Path to the generated PDF
        output_dir: Directory to store organized PDFs
        add_version: Whether to add version number to filename
    """
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    
    # Create output directory if it doesn't exist
    current_date = datetime.now()
    year_dir = output_dir / str(current_date.year)
    month_dir = year_dir / f"{current_date.month:02d}"
    
    month_dir.mkdir(parents=True, exist_ok=True)
    
    # Get book title from the PDF filename or use default
    book_title = pdf_path.stem
    
    # Format date for filename
    date_str = current_date.strftime("%Y-%m-%d")
    
    # Get version number if requested
    version = ""
    if add_version:
        # Count existing PDFs in this month's directory with this date
        existing_files = list(month_dir.glob(f"{book_title}_{date_str}*.pdf"))
        version = f"_v{len(existing_files) + 1}"
    
    # Create new filename
    new_filename = f"{book_title}_{date_str}{version}.pdf"
    new_path = month_dir / new_filename
    
    # Copy PDF to new location
    shutil.copy2(pdf_path, new_path)
    
    print(f"PDF organized: {new_path}")
    return new_path

def main():
    parser = argparse.ArgumentParser(description="Organize generated PDF by date")
    parser.add_argument('pdf_path', type=str, help='Path to the generated PDF')
    parser.add_argument('--output-dir', type=str, default='./published_pdfs',
                        help='Directory to store organized PDFs')
    parser.add_argument('--no-version', action='store_true',
                        help='Do not add version number to filename')
    
    args = parser.parse_args()
    
    organize_pdf(args.pdf_path, args.output_dir, not args.no_version)

if __name__ == "__main__":
    main()