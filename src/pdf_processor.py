"""
PDF Processor Module

Extracts text from PDF files using PyMuPDF and searches for regex patterns.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import fitz  # PyMuPDF


class PDFMatch:
    """Represents a single regex match in a PDF."""

    def __init__(
        self,
        term_name: str,
        matched_text: str,
        page_number: int,
        context_before: str,
        context_after: str,
        position: int
    ):
        """
        Initialize a PDF match.

        Args:
            term_name: Name of the matched term
            matched_text: The actual matched text
            page_number: Page number where match was found (1-indexed)
            context_before: Text before the match
            context_after: Text after the match
            position: Character position of match in page text
        """
        self.term_name = term_name
        self.matched_text = matched_text
        self.page_number = page_number
        self.context_before = context_before
        self.context_after = context_after
        self.position = position

    def to_dict(self) -> dict:
        """Convert match to dictionary format."""
        return {
            'term_name': self.term_name,
            'matched_text': self.matched_text,
            'page_number': self.page_number,
            'context_before': self.context_before,
            'context_after': self.context_after,
            'position': self.position
        }


def extract_text_from_pdf(pdf_path: Path) -> Dict[int, str]:
    """
    Extract text from PDF file, organized by page.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary mapping page numbers (1-indexed) to page text

    Raises:
        Exception: If PDF cannot be opened or read
    """
    page_texts = {}

    try:
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            page_texts[page_num + 1] = text  # 1-indexed page numbers

        doc.close()

    except Exception as e:
        raise Exception(f"Failed to extract text from {pdf_path}: {e}")

    return page_texts


def search_text_for_patterns(
    text: str,
    term_dict: Dict[str, str],
    page_number: int,
    context_before: int,
    context_after: int
) -> List[PDFMatch]:
    """
    Search text for regex patterns.

    Args:
        text: Text to search
        term_dict: Dictionary mapping term names to regex patterns
        page_number: Page number for reporting
        context_before: Characters to include before match
        context_after: Characters to include after match

    Returns:
        List of PDFMatch objects
    """
    matches = []

    for term_name, pattern in term_dict.items():
        try:
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)

            for match in regex.finditer(text):
                start_pos = match.start()
                end_pos = match.end()

                # Extract context
                context_start = max(0, start_pos - context_before)
                context_end = min(len(text), end_pos + context_after)

                before_text = text[context_start:start_pos]
                after_text = text[end_pos:context_end]
                matched_text = match.group(0)

                pdf_match = PDFMatch(
                    term_name=term_name,
                    matched_text=matched_text,
                    page_number=page_number,
                    context_before=before_text,
                    context_after=after_text,
                    position=start_pos
                )

                matches.append(pdf_match)

        except re.error as e:
            # Log regex errors but continue processing
            print(f"Warning: Invalid regex for term '{term_name}': {e}")
            continue

    return matches


def process_pdf_file(
    file_path: Path,
    term_dict: Dict[str, str],
    context_before: int = 50,
    context_after: int = 50
) -> List[PDFMatch]:
    """
    Process a PDF file and search for patterns.

    Args:
        file_path: Path to PDF file
        term_dict: Dictionary of term names to regex patterns
        context_before: Characters to include before match
        context_after: Characters to include after match

    Returns:
        List of all matches found in the PDF

    Raises:
        Exception: If PDF processing fails
    """
    all_matches = []

    # Extract text from all pages
    page_texts = extract_text_from_pdf(file_path)

    # Search each page
    for page_num, page_text in page_texts.items():
        page_matches = search_text_for_patterns(
            page_text,
            term_dict,
            page_num,
            context_before,
            context_after
        )
        all_matches.extend(page_matches)

    return all_matches


def get_pdf_metadata(pdf_path: Path) -> dict:
    """
    Extract metadata from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary containing PDF metadata
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        page_count = len(doc)
        doc.close()

        return {
            'page_count': page_count,
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', '')
        }

    except Exception:
        return {'page_count': 0, 'error': 'Unable to read metadata'}
