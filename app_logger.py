import logging
import os
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION ---
LOG_DIR = Path(r"e:\New_vision_AI\logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

def setup_logger(name="VisionAI"):
    """Configures a logger with both file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File Handler
        fh = logging.FileHandler(LOG_FILE)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        
        # Console Handler
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(sh)
        
    return logger

# Global logger instance
logger = setup_logger()

if __name__ == "__main__":
    logger.info("Logging system initialized.")
    logger.debug("Debug log test.")
    logger.error("Error log test.")
