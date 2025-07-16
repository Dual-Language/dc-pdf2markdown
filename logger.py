import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

class StorageLogger:
    """Logger that writes logs to both console and files in storage directory."""
    
    def __init__(self, storage_root: Path, service_name: str = "PDF2MarkdownService", log_level: str = "INFO"):
        self.storage_root = storage_root
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper())
        
        # Create logger
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Service-wide file handler (only ERROR and WARN)
        service_log_path = self.storage_root / f"{service_name}.log"
        service_handler = logging.FileHandler(service_log_path)
        service_handler.setLevel(logging.WARNING)  # Only WARNING and above (WARNING, ERROR, CRITICAL)
        service_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
        service_handler.setFormatter(service_formatter)
        self.logger.addHandler(service_handler)
    
    def _write_to_book_log(self, message: str, level: str, book_id: Optional[str] = None):
        """Write log entry to book-specific log file."""
        # Only write ERROR and WARN messages to files
        if level not in ['ERROR', 'WARN', 'WARNING']:
            return
            
        if not book_id:
            return
            
        # Skip empty messages
        if not message or message.strip() == '':
            return
            
        try:
            book_log_dir = self.storage_root / book_id
            book_log_dir.mkdir(exist_ok=True)
            
            book_log_path = book_log_dir / f"{self.service_name}-book.log"
            timestamp = datetime.now().isoformat()
            
            with open(book_log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {level} [{self.service_name}] [{book_id}] {message}\n")
        except Exception as e:
            # Fallback to console if file writing fails
            print(f"[Logger] Failed to write to book log file: {e}")
            print(f"[{datetime.now().isoformat()}] {level} [{self.service_name}] [{book_id}] {message}")
    
    def debug(self, message: str, book_id: Optional[str] = None):
        """Log debug message."""
        if not message or message.strip() == '':
            return
        self.logger.debug(message)
        self._write_to_book_log(message, "DEBUG", book_id)
    
    def info(self, message: str, book_id: Optional[str] = None):
        """Log info message."""
        if not message or message.strip() == '':
            return
        self.logger.info(message)
        self._write_to_book_log(message, "INFO", book_id)
    
    def warning(self, message: str, book_id: Optional[str] = None):
        """Log warning message."""
        if not message or message.strip() == '':
            return
        self.logger.warning(message)
        self._write_to_book_log(message, "WARNING", book_id)
    
    def error(self, message: str, book_id: Optional[str] = None, error: Optional[Exception] = None):
        """Log error message with optional exception details."""
        if not message or message.strip() == '':
            message = "Empty error message"
        if error:
            error_details = f"{message}\nError: {str(error)}\nStack: {getattr(error, '__traceback__', 'No traceback available')}"
            self.logger.error(error_details)
            self._write_to_book_log(error_details, "ERROR", book_id)
        else:
            self.logger.error(message)
            self._write_to_book_log(message, "ERROR", book_id)
    
    def error_with_error(self, message: str, error: Exception, book_id: Optional[str] = None):
        """Convenience method for logging errors with automatic error extraction."""
        self.error(message, book_id, error)

# Global logger instance
_global_logger: Optional[StorageLogger] = None

def get_logger(storage_root: Optional[Path] = None) -> StorageLogger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        if storage_root is None:
            storage_root = Path(os.environ.get("STORAGE_ROOT", "../storage")).resolve()
        _global_logger = StorageLogger(storage_root, "PDF2MarkdownService", "INFO")
    return _global_logger

def set_logger(logger: StorageLogger):
    """Set custom logger instance."""
    global _global_logger
    _global_logger = logger 