"""
Logger package initialization.
Provides easy access to the logging functionality.
"""

from .logger_config import get_logger, setup_logging

__all__ = ['get_logger', 'setup_logging']