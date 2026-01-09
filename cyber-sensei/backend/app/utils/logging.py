"""
Logging and request tracking utilities
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps

# Create logger
logger = logging.getLogger("cyber_sensei")

class RequestLogger:
    """Logs HTTP requests with request ID tracking"""
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def log_request(
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        request_id: str,
        user_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log HTTP request
        
        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            duration_ms: Duration in milliseconds
            request_id: Unique request ID
            user_id: User ID (optional)
            error: Error message (optional)
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "user_id": user_id,
        }
        
        if error:
            log_data["error"] = error
            logger.error(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

class PerformanceLogger:
    """Logs performance metrics"""
    
    @staticmethod
    def log_slow_query(
        query: str,
        duration_ms: float,
        threshold_ms: float = 1000
    ) -> None:
        """
        Log slow database queries
        
        Args:
            query: SQL query
            duration_ms: Duration in milliseconds
            threshold_ms: Slow query threshold (default 1s)
        """
        if duration_ms > threshold_ms:
            logger.warning(
                f"Slow query detected ({duration_ms:.2f}ms > {threshold_ms}ms): {query[:200]}"
            )
    
    @staticmethod
    def log_function_performance(threshold_ms: float = 100):
        """
        Decorator to log function execution time
        
        Args:
            threshold_ms: Log if duration exceeds this (milliseconds)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                start = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.perf_counter() - start) * 1000
                    if duration_ms > threshold_ms:
                        logger.info(
                            f"Function {func.__name__} took {duration_ms:.2f}ms"
                        )
            return wrapper
        return decorator

class ErrorLogger:
    """Logs errors with context"""
    
    @staticmethod
    def log_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "error"
    ) -> None:
        """
        Log error with context
        
        Args:
            error: Exception object
            context: Additional context (optional)
            level: Log level (debug, info, warning, error, critical)
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        log_method = getattr(logger, level, logger.error)
        log_method(json.dumps(log_data), exc_info=True)
    
    @staticmethod
    def log_validation_error(
        field: str,
        error: str,
        value: Any
    ) -> None:
        """
        Log validation error
        
        Args:
            field: Field name
            error: Error message
            value: Field value
        """
        logger.warning(
            f"Validation error on field '{field}': {error} (value: {value})"
        )

def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def configure_logging(
    level: str = "INFO",
    log_file: Optional[str] = None
) -> None:
    """
    Configure logging
    
    Args:
        level: Log level
        log_file: Optional log file path
    """
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

__all__ = [
    "logger",
    "RequestLogger",
    "PerformanceLogger",
    "ErrorLogger",
    "get_logger",
    "configure_logging",
]
