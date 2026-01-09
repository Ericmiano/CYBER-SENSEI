"""
Custom error classes and error handling utilities
"""

from fastapi import HTTPException, status
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

class AppException(HTTPException):
    """Base application exception"""
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        
        detail = {
            "error": error_code,
            "message": message,
            **self.details
        }
        
        super().__init__(status_code=status_code, detail=detail)

class ValidationError(AppException):
    """Validation error"""
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        detail_dict = details or {}
        if field:
            detail_dict["field"] = field
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="validation_error",
            message=message,
            details=detail_dict
        )

class NotFoundError(AppException):
    """Resource not found error"""
    def __init__(
        self,
        resource: str,
        resource_id: Optional[Any] = None
    ):
        message = f"{resource} not found"
        details = {"resource": resource}
        if resource_id:
            message = f"{resource} with id {resource_id} not found"
            details["resource_id"] = str(resource_id)
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="not_found",
            message=message,
            details=details
        )

class ConflictError(AppException):
    """Conflict error (e.g., duplicate resource)"""
    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        detail_dict = details or {}
        if resource:
            detail_dict["resource"] = resource
        
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="conflict",
            message=message,
            details=detail_dict
        )

class UnauthorizedError(AppException):
    """Unauthorized access error"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="unauthorized",
            message=message
        )

class ForbiddenError(AppException):
    """Forbidden access error"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="forbidden",
            message=message
        )

class RateLimitError(AppException):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="rate_limit",
            message=message
        )

class InternalServerError(AppException):
    """Internal server error"""
    def __init__(
        self,
        message: str = "Internal server error",
        log_error: Optional[Exception] = None
    ):
        if log_error:
            logger.error(f"Internal error: {log_error}", exc_info=True)
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="internal_error",
            message=message
        )

class BadRequestError(AppException):
    """Bad request error"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="bad_request",
            message=message,
            details=details
        )

def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        status_code: HTTP status code
        error_code: Error code identifier
        message: Error message
        **kwargs: Additional error details
    
    Returns:
        Error response dict
    """
    return {
        "error": error_code,
        "message": message,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        **kwargs
    }

__all__ = [
    "AppException",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
    "RateLimitError",
    "InternalServerError",
    "BadRequestError",
    "create_error_response",
]
