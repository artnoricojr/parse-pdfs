"""
Argument Parser Module

Handles command-line argument parsing for the PDF pattern matcher.
"""

import argparse
from pathlib import Path


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Recursively search PDF files for regex patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -s ./pdfs -o ./results -t terms.json
  python main.py -s ./docs -o ./output -t terms.csv -r --before 50 --after 50
  python main.py -s ./files -o ./results -t patterns.json -e .pdf .docx -S
        """
    )

    # Required arguments
    parser.add_argument(
        "-s", "--scan-folder",
        type=str,
        required=True,
        dest="scan_folder",
        help="Path to the folder to scan for files"
    )

    parser.add_argument(
        "-o", "--output-folder",
        type=str,
        required=True,
        dest="output_folder",
        help="Path to the output folder for results"
    )

    parser.add_argument(
        "-t", "--term-list",
        type=str,
        required=True,
        dest="term_list_path",
        help="Path to term list file (CSV or JSON)"
    )

    # Optional arguments
    parser.add_argument(
        "-e", "--extensions",
        nargs="+",
        default=[".pdf"],
        dest="file_extensions",
        help="Target file extensions to process (default: .pdf)"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        dest="recursive",
        help="Enable recursive directory scanning"
    )

    parser.add_argument(
        "--before",
        type=int,
        default=50,
        dest="context_before",
        help="Number of characters to include before matched term (default: 50)"
    )

    parser.add_argument(
        "--after",
        type=int,
        default=50,
        dest="context_after",
        help="Number of characters to include after matched term (default: 50)"
    )

    parser.add_argument(
        "-S", "--summary",
        action="store_true",
        dest="summary_report",
        help="Generate job summary report"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        dest="verbose",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Validate paths
    scan_path = Path(args.scan_folder)
    if not scan_path.exists():
        parser.error(f"Scan folder does not exist: {args.scan_folder}")

    if not scan_path.is_dir():
        parser.error(f"Scan folder is not a directory: {args.scan_folder}")

    term_list_path = Path(args.term_list_path)
    if not term_list_path.exists():
        parser.error(f"Term list file does not exist: {args.term_list_path}")

    if not term_list_path.is_file():
        parser.error(f"Term list path is not a file: {args.term_list_path}")

    # Validate file extensions format
    args.file_extensions = [
        ext if ext.startswith('.') else f'.{ext}'
        for ext in args.file_extensions
    ]

    # Validate context parameters
    if args.context_before < 0:
        parser.error("Context before must be non-negative")

    if args.context_after < 0:
        parser.error("Context after must be non-negative")

    return args
