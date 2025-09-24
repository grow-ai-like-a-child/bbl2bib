"""
Logging utilities for bbl2bib
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = 'bbl2bib', verbose: bool = False) -> logging.Logger:
    """
    Set up and configure logger.
    
    Args:
        name: Logger name
        verbose: Enable verbose (DEBUG) logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Set level
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    if verbose:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = 'bbl2bib') -> logging.Logger:
    """
    Get existing logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
