# PDF Pattern Matcher

A powerful Python tool for recursively searching PDF files using regular expressions. Extract and report matches with configurable context, comprehensive error handling, and detailed job summaries.

## Features

- **Recursive Directory Scanning**: Search through entire directory trees
- **Flexible Regex Patterns**: Load search patterns from JSON or CSV files
- **Context Capture**: Include configurable characters before/after matches
- **Comprehensive Reporting**: JSON output with match details and job summaries
- **Error Handling**: Robust exception logging and error tracking
- **PyMuPDF Integration**: Fast and accurate PDF text extraction

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py -s ./pdfs -o ./results -t examples/terms.json
```

### Advanced Usage

```bash
python main.py \
  --scan-folder ./documents \
  --output-folder ./output \
  --term-list terms.csv \
  --extensions .pdf .docx \
  --recursive \
  --before 100 \
  --after 100 \
  --summary
```

### Command-Line Arguments

#### Required Arguments

- `-s, --scan-folder`: Path to folder to scan for files
- `-o, --output-folder`: Path to output folder for results
- `-t, --term-list`: Path to term list file (JSON or CSV)

#### Optional Arguments

- `-e, --extensions`: Target file extensions (default: `.pdf`)
- `-r, --recursive`: Enable recursive directory scanning
- `--before`: Characters to include before matched term (default: 50)
- `--after`: Characters to include after matched term (default: 50)
- `-S, --summary`: Generate job summary report
- `-v, --verbose`: Enable verbose logging

## Term List Format

### JSON Format

```json
{
  "email": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
  "phone": "\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}",
  "ssn": "\\d{3}-\\d{2}-\\d{4}"
}
```

Or array format:

```json
[
  {
    "name": "email",
    "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
  },
  {
    "name": "phone",
    "pattern": "\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}"
  }
]
```

### CSV Format

```csv
term_name,pattern
email,[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
phone,\(?\d{3}\)?[-.\\s]?\d{3}[-.\\s]?\d{4}
ssn,\d{3}-\d{2}-\d{4}
```

## Output Format

### Results File (JSON)

```json
{
  "metadata": {
    "total_matches": 42,
    "files_with_matches": 5,
    "context_before": 50,
    "context_after": 50,
    "generated_at": "2025-01-15T10:30:00"
  },
  "matches": [
    {
      "file_name": "document.pdf",
      "file_path": "/path/to/document.pdf",
      "page_number": 3,
      "term_name": "email",
      "matched_text": "example@example.com",
      "context_before": "Please contact us at ",
      "context_after": " for more information.",
      "position": 1234
    }
  ]
}
```

### Summary Report (JSON)

```json
{
  "job_summary": {
    "start_time": "2025-01-15T10:30:00",
    "end_time": "2025-01-15T10:32:15",
    "elapsed_time_seconds": 135.5,
    "elapsed_time_formatted": "2m 15.50s",
    "files_scanned": 50,
    "pages_processed": 423,
    "files_with_matches": 12,
    "total_matches": 156
  },
  "search_parameters": {
    "term_count": 8,
    "terms": ["email", "phone", "ssn", "credit_card", "url", "ip_address", "date_mmddyyyy", "zip_code"],
    "context_before": 50,
    "context_after": 50
  },
  "match_counts_by_term": {
    "email": 45,
    "phone": 32,
    "ssn": 8,
    "credit_card": 12,
    "url": 38,
    "ip_address": 15,
    "date_mmddyyyy": 6,
    "zip_code": 0
  }
}
```

## Project Structure

```
parse-pdfs/
├── main.py                 # Main entry point
├── src/
│   ├── __init__.py
│   ├── arg_parser.py       # Command-line argument parsing
│   ├── term_loader.py      # Load regex patterns from CSV/JSON
│   ├── file_scanner.py     # Directory scanning and file discovery
│   ├── pdf_processor.py    # PDF text extraction and pattern matching
│   ├── result_aggregator.py # Result collection and output generation
│   └── logger.py           # Logging and exception handling
├── examples/
│   ├── terms.json          # Example JSON term list
│   └── terms.csv           # Example CSV term list
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Error Handling

The application includes comprehensive error handling:

- **Exception Logging**: All exceptions are logged to `logs/exceptions_YYYYMMDD_HHMMSS.log`
- **Graceful Degradation**: Continues processing even if individual files fail
- **Detailed Error Reports**: Stack traces and context for debugging

## Examples

### Search for PII in PDFs

```bash
python main.py \
  -s ./sensitive_docs \
  -o ./pii_results \
  -t examples/terms.json \
  -r \
  --summary
```

### Search specific file types with custom context

```bash
python main.py \
  -s ./documents \
  -o ./results \
  -t custom_patterns.csv \
  -e .pdf .txt .docx \
  --before 200 \
  --after 200 \
  -r -S
```

## Requirements

- Python 3.7+
- PyMuPDF (fitz)

## License

This project is provided as-is for educational and professional use.

## Contributing

Contributions are welcome! Please ensure all code includes:
- Proper error handling
- Type hints
- Docstrings
- Unit tests (if applicable)
