"""
Logger Module

Handles logging and exception tracking.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# Global exception log file
EXCEPTION_LOG_FILE = None


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    exception_log: Optional[Path] = None
) -> logging.Logger:
    """
    Set up application logger.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for general logs
        exception_log: Optional file path for exception logs

    Returns:
        Configured logger instance
    """
    global EXCEPTION_LOG_FILE

    # Create logger
    logger = logging.getLogger('pdf_pattern_matcher')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Set exception log file path
    if exception_log:
        EXCEPTION_LOG_FILE = exception_log
        exception_log.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Default exception log location
        EXCEPTION_LOG_FILE = Path('logs') / f'exceptions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        EXCEPTION_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    return logger


def log_exception(message: str, exception: Exception) -> None:
    """
    Log an exception to the exception log file.

    Args:
        message: Descriptive message about the exception context
        exception: The exception object
    """
    global EXCEPTION_LOG_FILE

    # Ensure exception log is set up
    if EXCEPTION_LOG_FILE is None:
        EXCEPTION_LOG_FILE = Path('logs') / f'exceptions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        EXCEPTION_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Get logger
    logger = logging.getLogger('pdf_pattern_matcher')

    # Log to console/file
    logger.error(f"{message}: {str(exception)}")

    # Write detailed exception to exception log
    try:
        import traceback

        with open(EXCEPTION_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Message: {message}\n")
            f.write(f"Exception Type: {type(exception).__name__}\n")
            f.write(f"Exception: {str(exception)}\n")
            f.write(f"\nTraceback:\n")
            f.write(traceback.format_exc())
            f.write(f"\n{'=' * 80}\n")

    except Exception as e:
        # If we can't write to exception log, at least log to console
        logger.critical(f"Failed to write to exception log: {e}")


def get_exception_log_path() -> Optional[Path]:
    """
    Get the current exception log file path.

    Returns:
        Path to exception log file, or None if not set
    """
    return EXCEPTION_LOG_FILE


class ExceptionContext:
    """Context manager for automatic exception logging."""

    def __init__(self, message: str):
        """
        Initialize exception context.

        Args:
            message: Message to log if exception occurs
        """
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            log_exception(self.message, exc_val)
        return False  # Don't suppress the exception
