"""
Logging configuration and setup.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(
    log_dir: str = "logs",
    app_log: str = "logs/app.log",
    level: str = "INFO",
    max_size_mb: int = 10,
    backup_count: int = 5,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None
):
    """
    Set up application logging.
    
    Args:
        log_dir: Directory for log files
        app_log: Path to main application log
        level: Logging level
        max_size_mb: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        log_format: Custom log format
        date_format: Custom date format
    """
    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Set up log format
    if log_format is None:
        log_format = "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s] %(message)s"
    
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"
    
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    max_bytes = max_size_mb * 1024 * 1024
    file_handler = logging.handlers.RotatingFileHandler(
        app_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Log initial message
    logging.info("=" * 80)
    logging.info("Application logging initialized")
    logging.info(f"Log level: {level}")
    logging.info(f"Log file: {app_log}")
    logging.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
