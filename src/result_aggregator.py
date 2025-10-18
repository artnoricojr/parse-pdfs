"""
Result Aggregator Module

Aggregates search results and generates output in JSON format.
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from collections import defaultdict

from .pdf_processor import PDFMatch


class ResultAggregator:
    """Aggregates and manages search results."""

    def __init__(self, context_before: int = 50, context_after: int = 50):
        """
        Initialize result aggregator.

        Args:
            context_before: Characters included before matches
            context_after: Characters included after matches
        """
        self.context_before = context_before
        self.context_after = context_after
        self.results = []
        self.match_counts = defaultdict(int)
        self.file_count = 0
        self.total_pages = 0

    def add_results(self, file_path: Path, matches: List[PDFMatch], page_count: int = 0) -> None:
        """
        Add results from a file.

        Args:
            file_path: Path to the file that was processed
            matches: List of PDFMatch objects found in the file
            page_count: Number of pages in the file
        """
        if matches:
            self.file_count += 1

        if page_count > 0:
            self.total_pages += page_count

        for match in matches:
            result = {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'page_number': match.page_number,
                'term_name': match.term_name,
                'matched_text': match.matched_text,
                'context_before': match.context_before,
                'context_after': match.context_after,
                'position': match.position
            }

            self.results.append(result)
            self.match_counts[match.term_name] += 1

    def get_total_matches(self) -> int:
        """Get total number of matches found."""
        return len(self.results)

    def get_matches_by_term(self) -> Dict[str, int]:
        """Get count of matches by term name."""
        return dict(self.match_counts)

    def save_results(self, output_path: Path) -> None:
        """
        Save results to JSON file.

        Args:
            output_path: Path where results should be saved
        """
        output_data = {
            'metadata': {
                'total_matches': self.get_total_matches(),
                'files_with_matches': self.file_count,
                'context_before': self.context_before,
                'context_after': self.context_after,
                'generated_at': datetime.now().isoformat()
            },
            'matches': self.results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

    def save_summary(
        self,
        output_path: Path,
        start_time: datetime,
        end_time: datetime,
        elapsed_time: float,
        files_scanned: int,
        term_list: Dict[str, str]
    ) -> None:
        """
        Save job summary report.

        Args:
            output_path: Path where summary should be saved
            start_time: Job start time
            end_time: Job end time
            elapsed_time: Elapsed time in seconds
            files_scanned: Total number of files scanned
            term_list: Dictionary of search terms used
        """
        # Format elapsed time as minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        elapsed_formatted = f"{minutes}m {seconds:.2f}s"

        summary = {
            'job_summary': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'elapsed_time_seconds': elapsed_time,
                'elapsed_time_formatted': elapsed_formatted,
                'files_scanned': files_scanned,
                'pages_processed': self.total_pages,
                'files_with_matches': self.file_count,
                'total_matches': self.get_total_matches()
            },
            'search_parameters': {
                'term_count': len(term_list),
                'terms': list(term_list.keys()),
                'context_before': self.context_before,
                'context_after': self.context_after
            },
            'match_counts_by_term': self.get_matches_by_term()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    def get_results_by_file(self) -> Dict[str, List[dict]]:
        """
        Group results by file name.

        Returns:
            Dictionary mapping file names to their matches
        """
        by_file = defaultdict(list)

        for result in self.results:
            by_file[result['file_name']].append(result)

        return dict(by_file)

    def get_results_by_term(self) -> Dict[str, List[dict]]:
        """
        Group results by term name.

        Returns:
            Dictionary mapping term names to their matches
        """
        by_term = defaultdict(list)

        for result in self.results:
            by_term[result['term_name']].append(result)

        return dict(by_term)

    def export_csv(self, output_path: Path) -> None:
        """
        Export results to CSV format.

        Args:
            output_path: Path where CSV should be saved
        """
        import csv

        if not self.results:
            return

        fieldnames = [
            'file_name',
            'file_path',
            'page_number',
            'term_name',
            'matched_text',
            'context_before',
            'context_after',
            'position'
        ]

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
