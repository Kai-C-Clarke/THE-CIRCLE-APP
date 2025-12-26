# logging_config.py - Centralized logging configuration
import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(app_name="the_circle_app", log_level=None):
    """
    Configure application logging.

    Args:
        app_name: Name of the application for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  If None, uses LOG_LEVEL env var or defaults to INFO
    """
    # Determine log level from environment or parameter
    if log_level is None:
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []

    # Console handler (simple format for console output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # File handler (detailed format for file logs)
    # Rotating file handler: max 10MB per file, keep 5 backup files
    log_file = os.path.join(log_dir, f"{app_name}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Error file handler (only errors and above)
    error_log_file = os.path.join(log_dir, f"{app_name}_error.log")
    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_file_handler)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {logging.getLevelName(log_level)}")
    logger.info(f"Log file: {log_file}")

    return root_logger


def get_logger(name):
    """
    Get a logger instance for a module.

    Args:
        name: Usually __name__ from the calling module

    Returns:
        logging.Logger instance
    """
    return logging.getLogger(name)
