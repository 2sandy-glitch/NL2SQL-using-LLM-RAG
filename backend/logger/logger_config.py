"""
Logging configuration for the Text-to-SQL Chatbot application.
Provides colored console output and rotating file handlers.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Try to import colorlog for colored console output
try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


class LoggerConfig:
    """Configuration class for logging settings."""
    
    def __init__(self, log_dir: str = None, log_level: str = "DEBUG"):
        self.log_dir = log_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'logs'
        )
        self.log_level = getattr(logging, log_level.upper(), logging.DEBUG)
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Log file paths
        self.app_log_file = os.path.join(self.log_dir, 'app.log')
        self.error_log_file = os.path.join(self.log_dir, 'error.log')
        self.debug_log_file = os.path.join(self.log_dir, 'debug.log')
        
        # Log formats
        self.file_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
        self.console_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        self.date_format = "%Y-%m-%d %H:%M:%S"
        
        # Color format for console
        self.color_format = "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s%(reset)s"


_logging_initialized = False


def setup_logging(log_dir: str = None, log_level: str = "DEBUG") -> None:
    """
    Set up the root logger with console and file handlers.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global _logging_initialized
    
    if _logging_initialized:
        return
    
    config = LoggerConfig(log_dir, log_level)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Create formatters
    file_formatter = logging.Formatter(config.file_format, datefmt=config.date_format)
    
    # Console Handler with colors
    if COLORLOG_AVAILABLE:
        console_formatter = colorlog.ColoredFormatter(
            config.color_format,
            datefmt=config.date_format,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    else:
        console_formatter = logging.Formatter(
            config.console_format, 
            datefmt=config.date_format
        )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # App Log File Handler (all levels)
    try:
        app_file_handler = RotatingFileHandler(
            config.app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        app_file_handler.setLevel(logging.DEBUG)
        app_file_handler.setFormatter(file_formatter)
        root_logger.addHandler(app_file_handler)
        
        # Error Log File Handler (ERROR and CRITICAL only)
        error_file_handler = RotatingFileHandler(
            config.error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_file_handler)
        
        # Debug Log File Handler
        debug_file_handler = RotatingFileHandler(
            config.debug_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=3,
            encoding='utf-8'
        )
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(file_formatter)
        root_logger.addHandler(debug_file_handler)
        
    except Exception as e:
        # If file handlers fail, just use console
        print(f"Warning: Could not set up file logging: {e}")
    
    _logging_initialized = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Name of the logger (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)