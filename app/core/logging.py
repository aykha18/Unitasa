"""
Logging configuration for AI Marketing Agents
Uses structlog for structured logging with JSON output
"""

import logging
import sys
from typing import Any, Dict
try:
    import structlog
    from pythonjsonlogger import jsonlogger
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

from app.core.config import get_settings
settings = get_settings()


def setup_logging():
    """
    Configure structured logging for the application
    """
    # Default log level and format
    log_level = getattr(logging, "INFO")  # Default to INFO
    log_format = "text"  # Default to text

    # Try to get from settings if available
    try:
        log_level = getattr(logging, getattr(settings, 'log_level', 'INFO').upper())
        log_format = getattr(settings, 'log_format', 'text')
    except AttributeError:
        pass

    # Configure standard library logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    if STRUCTLOG_AVAILABLE:
        # Configure structlog
        if log_format == "json":
            # JSON logging for production
            structlog.configure(
                processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.JSONRenderer(),
                ],
                wrapper_class=structlog.make_filtering_bound_logger(log_level),
                context_class=dict,
                logger_factory=structlog.WriteLoggerFactory(),
                cache_logger_on_first_use=True,
            )
        else:
            # Human-readable logging for development
            structlog.configure(
                processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                    structlog.dev.ConsoleRenderer(colors=True),
                ],
                wrapper_class=structlog.make_filtering_bound_logger(log_level),
                context_class=dict,
                logger_factory=structlog.WriteLoggerFactory(),
                cache_logger_on_first_use=True,
            )


def get_logger(name: str):
    """
    Get a logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


# Global logger instance
logger = get_logger(__name__)


def log_request_middleware(request_id: str, method: str, path: str, status_code: int, duration: float):
    """
    Log HTTP request details

    Args:
        request_id: Unique request identifier
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration: Request duration in seconds
    """
    logger.info(
        "HTTP Request",
        request_id=request_id,
        method=method,
        path=path,
        status_code=status_code,
        duration=f"{duration:.3f}s",
        extra={
            "http": {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": duration,
            }
        }
    )


def log_error(error: Exception, context: Dict[str, Any] = None):
    """
    Log application errors with context

    Args:
        error: Exception instance
        context: Additional context information
    """
    error_context = context or {}
    error_context.update({
        "error_type": type(error).__name__,
        "error_message": str(error),
    })

    logger.error(
        "Application Error",
        exc_info=error,
        **error_context
    )


def log_performance(operation: str, duration: float, metadata: Dict[str, Any] = None):
    """
    Log performance metrics

    Args:
        operation: Operation name
        duration: Duration in seconds
        metadata: Additional metadata
    """
    log_data = {
        "operation": operation,
        "duration": f"{duration:.3f}s",
        "performance": True,
    }

    if metadata:
        log_data.update(metadata)

    logger.info("Performance Metric", **log_data)
