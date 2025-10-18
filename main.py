#!/usr/bin/env python3
"""
PDF Pattern Matcher - Main Entry Point

Recursively searches PDF files for regex patterns and outputs results in JSON format.
"""

import sys
from pathlib import Path
from datetime import datetime

from src.arg_parser import parse_arguments
from src.term_loader import load_term_list
from src.file_scanner import scan_directory
from src.pdf_processor import process_pdf_file
from src.result_aggregator import ResultAggregator
from src.logger import setup_logger, log_exception


def main():
    """Main execution function."""
    start_time = datetime.now()
    logger = setup_logger()

    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Load regex term list
        logger.info(f"Loading term list from: {args.term_list_path}")
        term_list = load_term_list(args.term_list_path)

        if not term_list:
            logger.error("No search terms loaded. Exiting.")
            sys.exit(1)

        logger.info(f"Loaded {len(term_list)} search terms")

        # Initialize result aggregator
        aggregator = ResultAggregator(
            context_before=args.context_before,
            context_after=args.context_after
        )

        # Scan directory for files
        logger.info(f"Scanning directory: {args.scan_folder}")
        files_to_process = scan_directory(
            args.scan_folder,
            args.file_extensions,
            args.recursive
        )

        logger.info(f"Found {len(files_to_process)} files to process")

        # Process each file
        for file_path in files_to_process:
            try:
                logger.info(f"Processing: {file_path}")
                results = process_pdf_file(
                    file_path,
                    term_list,
                    args.context_before,
                    args.context_after
                )
                aggregator.add_results(file_path, results)
            except Exception as e:
                log_exception(f"Error processing {file_path}", e)

        # Generate outputs
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        # Save results
        output_path = Path(args.output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        results_file = output_path / f"results_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        aggregator.save_results(results_file)
        logger.info(f"Results saved to: {results_file}")

        # Generate summary report if requested
        if args.summary_report:
            summary_file = output_path / f"summary_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
            aggregator.save_summary(
                summary_file,
                start_time=start_time,
                end_time=end_time,
                elapsed_time=elapsed_time,
                files_scanned=len(files_to_process),
                term_list=term_list
            )
            logger.info(f"Summary report saved to: {summary_file}")

        logger.info("Processing complete!")
        logger.info(f"Total files scanned: {len(files_to_process)}")
        logger.info(f"Total matches found: {aggregator.get_total_matches()}")
        logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")

    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        log_exception("Fatal error in main execution", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
