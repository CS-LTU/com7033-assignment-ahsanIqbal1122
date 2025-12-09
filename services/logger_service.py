"""
Logger Service

Centralized logging configuration for the application.
Implements structured logging with file rotation and different log levels.

Features:
- File-based logging with rotation (10MB per file, 5 backups)
- Console logging for development
- Structured log format with timestamps
- Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Separate loggers for different modules

Author: Ahsan Iqbal
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name: str = 'stroke_app', 
                log_dir: str = 'logs',
                level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger instance with file and console handlers.
    
    Args:
        name (str): Logger name
        log_dir (str): Directory to store log files
        level (int): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
        
    Usage:
        >>> from services import setup_logger
        >>> logger = setup_logger('my_module')
        >>> logger.info('Application started')
        >>> logger.error('An error occurred')
    
    Log Format:
        2025-12-09 10:30:45,123 - stroke_app - INFO - User logged in successfully
        [timestamp] - [logger_name] - [level] - [message]
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler with rotation (10MB per file, keep 5 backups)
    log_file = os.path.join(log_dir, f'{name}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Error file handler (only errors and critical)
    error_log_file = os.path.join(log_dir, f'{name}_errors.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    # Log initial setup
    logger.info(f"Logger '{name}' initialized - Log files: {log_file}")
    
    return logger


def log_request(logger: logging.Logger, method: str, endpoint: str, 
                user_id: int = None, status_code: int = None):
    """
    Log HTTP request with details.
    
    Args:
        logger (logging.Logger): Logger instance
        method (str): HTTP method (GET, POST, etc.)
        endpoint (str): Request endpoint
        user_id (int, optional): User ID making the request
        status_code (int, optional): Response status code
    """
    user_info = f"user_id={user_id}" if user_id else "anonymous"
    status_info = f"status={status_code}" if status_code else ""
    
    logger.info(f"{method} {endpoint} - {user_info} {status_info}")


def log_security_event(logger: logging.Logger, event_type: str, details: str, 
                       user_id: int = None, severity: str = 'WARNING'):
    """
    Log security-related events for audit trail.
    
    Args:
        logger (logging.Logger): Logger instance
        event_type (str): Type of security event (LOGIN_FAILED, ACCESS_DENIED, etc.)
        details (str): Event details
        user_id (int, optional): User ID involved
        severity (str): Log severity (INFO, WARNING, ERROR, CRITICAL)
    """
    user_info = f"user_id={user_id}" if user_id else "unknown_user"
    message = f"SECURITY_EVENT: {event_type} - {details} - {user_info}"
    
    if severity == 'CRITICAL':
        logger.critical(message)
    elif severity == 'ERROR':
        logger.error(message)
    elif severity == 'WARNING':
        logger.warning(message)
    else:
        logger.info(message)


# Example usage and testing
if __name__ == '__main__':
    # Create test logger
    test_logger = setup_logger('test', level=logging.DEBUG)
    
    # Test different log levels
    test_logger.debug('This is a debug message')
    test_logger.info('This is an info message')
    test_logger.warning('This is a warning message')
    test_logger.error('This is an error message')
    test_logger.critical('This is a critical message')
    
    # Test request logging
    log_request(test_logger, 'POST', '/login', user_id=123, status_code=200)
    
    # Test security event logging
    log_security_event(test_logger, 'LOGIN_FAILED', 'Invalid password', user_id=456)
    
    print("Logger test complete. Check logs/ directory for output files.")
