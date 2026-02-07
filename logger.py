import logging
import sys
from typing import Any
import json

class AsyncJSONFormatter(logging.Formatter):
    """Async-safe JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "agent": getattr(record, 'agent', 'unknown'),
            "duration_ms": getattr(record, 'duration_ms', None),
        }
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logger():
    """Configure async-safe logger"""
    logger = logging.getLogger("teaching_agent")
    logger.setLevel(logging.INFO)
    
    # Console handler with async-safe formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(AsyncJSONFormatter())
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

# Global logger instance
logger = setup_logger()