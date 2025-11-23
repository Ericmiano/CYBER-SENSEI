"""
Centralized logging configuration for Cyber-Sensei.
"""

import logging
import logging.handlers
import os
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logging():
    """
    Configure logging with both file and console handlers.
    
    Creates:
        - Console handler: INFO level for immediate feedback
        - File handler: DEBUG level for detailed troubleshooting
        - Rotating file handler: Prevents log files from growing too large
    """
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Log format
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # File handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "cyber_sensei.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5  # Keep 5 backups
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Celery logger
    celery_logger = logging.getLogger("celery")
    celery_logger.setLevel(logging.INFO)
    celery_file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "celery.log",
        maxBytes=10_000_000,
        backupCount=3
    )
    celery_file_handler.setFormatter(log_format)
    celery_logger.addHandler(celery_file_handler)
    
    # SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.WARNING)  # Only show warnings/errors
    
    logging.info(f"Logging initialized at level {LOG_LEVEL}")
    logging.info(f"Log files: {LOG_DIR.absolute()}")


# Initialize logging on module load
setup_logging()
