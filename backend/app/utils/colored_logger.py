"""
Colored logger utility for better backend logging with timestamps and colors
"""
import logging
import colorama
from colorama import Fore, Back, Style
from datetime import datetime
import sys

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors and better timestamps to log messages"""
    
    # Color mapping for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    def format(self, record):
        # Get the color for this log level
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Create colored level name
        colored_level = f"{log_color}{record.levelname:<8}{Style.RESET_ALL}"
        
        # Format the message with color
        if record.levelname in ['ERROR', 'CRITICAL']:
            message = f"{log_color}{record.getMessage()}{Style.RESET_ALL}"
        else:
            message = record.getMessage()
        
        # Create the final formatted message
        formatted = f"{Fore.WHITE}[{timestamp}]{Style.RESET_ALL} {colored_level} {Fore.BLUE}{record.name}:{Style.RESET_ALL} {message}"
        
        # Add extra context for errors
        if record.levelname in ['ERROR', 'CRITICAL'] and record.exc_info:
            formatted += f"\n{log_color}{self.formatException(record.exc_info)}{Style.RESET_ALL}"
            
        return formatted

def setup_colored_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a colored logger with the given name and level
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add multiple handlers if logger already exists
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create and set the colored formatter
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def get_websocket_logger() -> logging.Logger:
    """Get a logger specifically for WebSocket operations"""
    return setup_colored_logger("websocket", logging.INFO)

def get_scraper_logger() -> logging.Logger:
    """Get a logger specifically for scraping operations"""
    return setup_colored_logger("scraper", logging.INFO)

def get_api_logger() -> logging.Logger:
    """Get a logger specifically for API operations"""
    return setup_colored_logger("api", logging.INFO)

# Convenience functions for different log levels with context
def log_progress(logger: logging.Logger, message: str, step: str = "", repo: str = ""):
    """Log progress with consistent formatting"""
    context = ""
    if step:
        context += f"[{step.upper()}] "
    if repo:
        context += f"({repo}) "
    
    logger.info(f"🔄 {context}{message}")

def log_success(logger: logging.Logger, message: str, context: str = ""):
    """Log success with consistent formatting"""
    ctx = f"({context}) " if context else ""
    logger.info(f"✅ {ctx}{message}")

def log_warning(logger: logging.Logger, message: str, context: str = ""):
    """Log warning with consistent formatting"""
    ctx = f"({context}) " if context else ""
    logger.warning(f"⚠️  {ctx}{message}")

def log_error(logger: logging.Logger, message: str, context: str = "", exc_info=None):
    """Log error with consistent formatting"""
    ctx = f"({context}) " if context else ""
    logger.error(f"❌ {ctx}{message}", exc_info=exc_info)

def log_debug(logger: logging.Logger, message: str, context: str = ""):
    """Log debug with consistent formatting"""
    ctx = f"({context}) " if context else ""
    logger.debug(f"🔍 {ctx}{message}")