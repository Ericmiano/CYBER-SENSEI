"""
File upload validation and security utilities.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration from environment
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 5242880))  # 5MB default
ALLOWED_FILE_TYPES = os.getenv(
    "ALLOWED_FILE_TYPES", 
    "mp4,avi,mov,mkv,pdf,docx,txt,jpg,png,gif"
).split(",")

# Dangerous patterns in filenames
DANGEROUS_PATTERNS = ["..", "~", "$", "`", "|", ";", "&", "\\"]


def validate_filename(filename: str) -> bool:
    """
    Validate filename for security issues.
    
    Args:
        filename: Original filename to validate
        
    Returns:
        True if filename is safe, False otherwise
    """
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern in filename:
            logger.warning(f"Dangerous pattern '{pattern}' in filename: {filename}")
            return False
    
    # Ensure filename is not empty after validation
    if not filename or len(filename) == 0:
        logger.warning("Empty filename rejected")
        return False
    
    # Reject files starting with dot
    if filename.startswith("."):
        logger.warning(f"Hidden file rejected: {filename}")
        return False
    
    return True


def validate_file_type(filename: str) -> bool:
    """
    Validate file type based on extension.
    
    Args:
        filename: Filename to validate
        
    Returns:
        True if file type is allowed, False otherwise
    """
    # Get file extension
    _, ext = os.path.splitext(filename)
    ext = ext.lstrip(".").lower()
    
    if ext not in ALLOWED_FILE_TYPES:
        logger.warning(f"File type '{ext}' not allowed for {filename}")
        return False
    
    return True


def validate_file_size(size: int) -> bool:
    """
    Validate file size.
    
    Args:
        size: File size in bytes
        
    Returns:
        True if size is within limits, False otherwise
    """
    if size > MAX_FILE_SIZE:
        logger.warning(f"File too large: {size} bytes (max: {MAX_FILE_SIZE})")
        return False
    
    if size == 0:
        logger.warning("Empty file rejected")
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem storage
    """
    # Replace dangerous characters with underscores
    sanitized = filename
    for char in DANGEROUS_PATTERNS:
        sanitized = sanitized.replace(char, "_")
    
    # Remove multiple consecutive underscores
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    
    # Ensure filename isn't too long (255 chars is typical fs limit)
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:250] + ext
    
    return sanitized


def validate_upload(filename: str, size: int) -> tuple[bool, Optional[str]]:
    """
    Comprehensive file upload validation.
    
    Args:
        filename: Filename to validate
        size: File size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate filename
    if not validate_filename(filename):
        return False, f"Invalid filename: {filename}"
    
    # Validate file type
    if not validate_file_type(filename):
        _, ext = os.path.splitext(filename)
        return False, f"File type {ext} not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
    
    # Validate file size
    if not validate_file_size(size):
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File too large. Maximum size: {max_mb:.1f}MB"
    
    return True, None


def ensure_upload_directory(directory: str) -> Path:
    """
    Ensure upload directory exists and is writable.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object for directory
        
    Raises:
        ValueError: If directory cannot be created/accessed
    """
    path = Path(directory)
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        
        # Test write permission
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
        
        return path
    except Exception as e:
        logger.error(f"Cannot access upload directory {directory}: {e}")
        raise ValueError(f"Upload directory not accessible: {directory}") from e
