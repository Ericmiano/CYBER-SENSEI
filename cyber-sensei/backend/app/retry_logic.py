"""
Advanced retry logic with exponential backoff for async operations.

Features:
- Exponential backoff with jitter
- Configurable retry strategies
- Dead letter queue for failed tasks
- Retry metrics and monitoring
- Circuit breaker pattern
"""

import asyncio
import logging
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        backoff_factor: float = 1.5,
        retry_on: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delay
            backoff_factor: Multiplier for exponential backoff
            retry_on: Tuple of exception types to retry on
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.backoff_factor = backoff_factor
        self.retry_on = retry_on


class RetryMetrics:
    """Track retry metrics for monitoring."""
    
    def __init__(self):
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
        self.total_retries = 0
        self.last_error = None
        self.last_error_time = None
    
    def record_attempt(self, success: bool, error: Optional[Exception] = None):
        """Record a single attempt."""
        self.total_attempts += 1
        if success:
            self.successful_attempts += 1
        else:
            self.failed_attempts += 1
            self.last_error = error
            self.last_error_time = datetime.utcnow()
    
    def record_retry(self):
        """Record a retry attempt."""
        self.total_retries += 1
    
    def get_stats(self) -> dict:
        """Get current metrics."""
        return {
            "total_attempts": self.total_attempts,
            "successful": self.successful_attempts,
            "failed": self.failed_attempts,
            "total_retries": self.total_retries,
            "success_rate": (
                self.successful_attempts / self.total_attempts 
                if self.total_attempts > 0 else 0
            ),
            "last_error": str(self.last_error),
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None
        }


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds before attempting to half-open
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def record_success(self):
        """Record a successful call."""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
    
    def can_attempt(self) -> bool:
        """Check if we can attempt the call."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed > self.timeout:
                    self.state = "half_open"
                    return True
            return False
        
        # Half-open: allow one attempt
        return True
    
    def get_state(self) -> dict:
        """Get circuit breaker state."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class DeadLetterQueue:
    """Store failed operations for later processing."""
    
    def __init__(self, max_queue_size: int = 1000):
        self.queue = []
        self.max_queue_size = max_queue_size
    
    def add_failed_task(self, task_name: str, args: tuple, kwargs: dict, 
                       error: Exception, attempt: int):
        """Add a failed task to the queue."""
        if len(self.queue) >= self.max_queue_size:
            # Remove oldest item
            self.queue.pop(0)
        
        self.queue.append({
            "task_name": task_name,
            "args": args,
            "kwargs": kwargs,
            "error": str(error),
            "attempt": attempt,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.error(
            f"Task '{task_name}' failed after {attempt} attempts: {error}"
        )
    
    def get_failed_tasks(self, limit: int = 100) -> list:
        """Get recent failed tasks."""
        return self.queue[-limit:]
    
    def clear(self):
        """Clear the queue."""
        self.queue.clear()


# Global instances
_dead_letter_queue = DeadLetterQueue()
_circuit_breaker = CircuitBreaker()
_retry_metrics = RetryMetrics()


def get_retry_metrics() -> RetryMetrics:
    """Get global retry metrics."""
    return _retry_metrics


def get_dead_letter_queue() -> DeadLetterQueue:
    """Get global dead letter queue."""
    return _dead_letter_queue


def get_circuit_breaker() -> CircuitBreaker:
    """Get global circuit breaker."""
    return _circuit_breaker


def calculate_backoff_delay(attempt: int, config: RetryConfig) -> float:
    """
    Calculate delay for exponential backoff.
    
    Args:
        attempt: Current attempt number (0-based)
        config: Retry configuration
        
    Returns:
        Delay in seconds
    """
    # Exponential backoff: initial_delay * (base ^ attempt)
    delay = config.initial_delay * (config.exponential_base ** attempt)
    
    # Cap at max delay
    delay = min(delay, config.max_delay)
    
    # Add jitter if enabled
    if config.jitter:
        jitter = random.uniform(0, delay * 0.1)  # Add up to 10% jitter
        delay += jitter
    
    return delay


def retry_with_backoff(config: Optional[RetryConfig] = None):
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        config: RetryConfig instance (uses defaults if not provided)
        
    Example:
        @retry_with_backoff(RetryConfig(max_retries=3))
        async def fetch_data():
            ...
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics = get_retry_metrics()
            dlq = get_dead_letter_queue()
            breaker = get_circuit_breaker()
            
            last_error = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    # Check circuit breaker
                    if not breaker.can_attempt():
                        raise RuntimeError("Circuit breaker is open")
                    
                    # Attempt the call
                    result = await func(*args, **kwargs)
                    
                    metrics.record_attempt(True)
                    breaker.record_success()
                    
                    logger.debug(
                        f"Function '{func.__name__}' succeeded on attempt {attempt + 1}"
                    )
                    
                    return result
                
                except config.retry_on as e:
                    last_error = e
                    metrics.record_attempt(False, e)
                    
                    if attempt < config.max_retries:
                        metrics.record_retry()
                        breaker.record_failure()
                        
                        delay = calculate_backoff_delay(attempt, config)
                        
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        await asyncio.sleep(delay)
                    else:
                        # Final failure - add to dead letter queue
                        dlq.add_failed_task(
                            func.__name__, args, kwargs, e, attempt + 1
                        )
                        breaker.record_failure()
            
            # All retries exhausted
            raise last_error or RuntimeError(f"Failed to execute {func.__name__}")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Synchronous wrapper for non-async functions."""
            metrics = get_retry_metrics()
            dlq = get_dead_letter_queue()
            breaker = get_circuit_breaker()
            
            last_error = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    if not breaker.can_attempt():
                        raise RuntimeError("Circuit breaker is open")
                    
                    result = func(*args, **kwargs)
                    
                    metrics.record_attempt(True)
                    breaker.record_success()
                    
                    return result
                
                except config.retry_on as e:
                    last_error = e
                    metrics.record_attempt(False, e)
                    
                    if attempt < config.max_retries:
                        metrics.record_retry()
                        breaker.record_failure()
                        
                        delay = calculate_backoff_delay(attempt, config)
                        
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        asyncio.run(asyncio.sleep(delay))
                    else:
                        dlq.add_failed_task(
                            func.__name__, args, kwargs, e, attempt + 1
                        )
                        breaker.record_failure()
            
            raise last_error or RuntimeError(f"Failed to execute {func.__name__}")
        
        # Return appropriate wrapper based on async status
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Pre-configured retry decorators for common scenarios

def retry_api_call():
    """Retry decorator for API calls (3 attempts, 1-10s delays)."""
    config = RetryConfig(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        retry_on=(ConnectionError, TimeoutError, IOError)
    )
    return retry_with_backoff(config)


def retry_database_operation():
    """Retry decorator for database operations (5 attempts, 0.5-30s delays)."""
    config = RetryConfig(
        max_retries=5,
        initial_delay=0.5,
        max_delay=30.0,
        retry_on=(Exception,)  # Retry all exceptions
    )
    return retry_with_backoff(config)


def retry_external_service():
    """Retry decorator for external services (4 attempts, 2-60s delays)."""
    config = RetryConfig(
        max_retries=4,
        initial_delay=2.0,
        max_delay=60.0,
        exponential_base=2.5,
        retry_on=(ConnectionError, TimeoutError, Exception)
    )
    return retry_with_backoff(config)
