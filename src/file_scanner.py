"""
File Scanner Module

Recursively scans directories for files matching target extensions.
"""

from pathlib import Path
from typing import List


def scan_directory(
    root_path: str,
    extensions: List[str],
    recursive: bool = False
) -> List[Path]:
    """
    Scan directory for files matching target extensions.

    Args:
        root_path: Root directory to scan
        extensions: List of file extensions to match (e.g., ['.pdf', '.txt'])
        recursive: Whether to scan subdirectories recursively

    Returns:
        List of Path objects for matching files

    Raises:
        FileNotFoundError: If root_path doesn't exist
        NotADirectoryError: If root_path is not a directory
    """
    root = Path(root_path)

    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root_path}")

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    # Normalize extensions to lowercase
    extensions = [ext.lower() for ext in extensions]

    matching_files = []

    if recursive:
        # Recursive search
        for ext in extensions:
            # Use glob pattern **/* for recursive search
            matching_files.extend(root.glob(f"**/*{ext}"))
    else:
        # Non-recursive search (only immediate children)
        for ext in extensions:
            matching_files.extend(root.glob(f"*{ext}"))

    # Filter out directories and sort by name
    files = [f for f in matching_files if f.is_file()]
    files.sort()

    return files


def get_file_info(file_path: Path) -> dict:
    """
    Get metadata about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary containing file metadata
    """
    stat = file_path.stat()

    return {
        'path': str(file_path),
        'name': file_path.name,
        'size': stat.st_size,
        'modified': stat.st_mtime,
        'extension': file_path.suffix
    }
