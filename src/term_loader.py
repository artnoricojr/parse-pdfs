"""
Term Loader Module

Loads regex patterns from CSV or JSON files.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List


def load_term_list(file_path: str) -> Dict[str, str]:
    """
    Load regex term list from CSV or JSON file.

    Args:
        file_path: Path to the term list file

    Returns:
        Dictionary mapping term names to regex patterns

    Raises:
        ValueError: If file format is unsupported
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Term list file not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == '.json':
        return _load_json_terms(path)
    elif suffix == '.csv':
        return _load_csv_terms(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .json or .csv")


def _load_json_terms(file_path: Path) -> Dict[str, str]:
    """
    Load terms from JSON file.

    Expected formats:
    1. Object with key-value pairs: {"term_name": "regex_pattern", ...}
    2. Array of objects: [{"name": "term_name", "pattern": "regex_pattern"}, ...]

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary mapping term names to regex patterns
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict):
        # Format 1: Direct key-value pairs
        return data
    elif isinstance(data, list):
        # Format 2: Array of objects
        term_dict = {}
        for item in data:
            if isinstance(item, dict):
                if 'name' in item and 'pattern' in item:
                    term_dict[item['name']] = item['pattern']
                elif 'term' in item and 'regex' in item:
                    term_dict[item['term']] = item['regex']
                else:
                    # Try to use first two values
                    keys = list(item.keys())
                    if len(keys) >= 2:
                        term_dict[item[keys[0]]] = item[keys[1]]
        return term_dict
    else:
        raise ValueError("JSON file must contain an object or array")


def _load_csv_terms(file_path: Path) -> Dict[str, str]:
    """
    Load terms from CSV file.

    Expected format:
    - First column: term name
    - Second column: regex pattern
    - First row may be header (auto-detected)

    Args:
        file_path: Path to CSV file

    Returns:
        Dictionary mapping term names to regex patterns
    """
    term_dict = {}

    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        # Try to detect if file has headers
        sample = f.read(1024)
        f.seek(0)

        sniffer = csv.Sniffer()
        has_header = sniffer.has_header(sample)

        reader = csv.reader(f)

        if has_header:
            next(reader)  # Skip header row

        for row_num, row in enumerate(reader, start=1):
            if len(row) < 2:
                continue  # Skip rows with insufficient columns

            term_name = row[0].strip()
            pattern = row[1].strip()

            if term_name and pattern:
                term_dict[term_name] = pattern

    return term_dict


def validate_term_list(term_dict: Dict[str, str]) -> List[str]:
    """
    Validate regex patterns in term list.

    Args:
        term_dict: Dictionary of term names to patterns

    Returns:
        List of error messages (empty if all valid)
    """
    import re

    errors = []

    for name, pattern in term_dict.items():
        try:
            re.compile(pattern)
        except re.error as e:
            errors.append(f"Invalid regex for '{name}': {e}")

    return errors
