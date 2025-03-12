import sys
from typing import Optional

from loguru import logger


class LogHandler:
    """
    Class to handle logging
    """
    def __init__(self, log_dir: str = "./logs/app.txt"):
        self.log_dir = log_dir
        
        logger.remove()
        logger.add(
            sys.stderr,
            format="<level>{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}</level>",
            colorize=True,
            level="DEBUG",
            
        )

        logger.add(
            self.log_dir, format="{time} | {level} | {message}", level="DEBUG"
        )

    @staticmethod
    def get_logger():
        return logger

    def info(self, message: Optional[str] = None, **kwargs):
        extra_message = " | ".join(f"{key}={value}" for key, value in kwargs.items())
        full_message = f"✅ {message}" + (f" | {extra_message}" if extra_message else "")
        return LogHandler.get_logger().info(full_message)
    
    def warning(self, message: Optional[str] = None, **kwargs):
        extra_message = " | ".join(f"{key}={value}" for key, value in kwargs.items())
        full_message = f"⚠️ {message}" + (f" | {extra_message}" if extra_message else "")
        return LogHandler.get_logger().warning(full_message)
    
    def error(self, message: Optional[str] = None, **kwargs):
        extra_message = " | ".join(f"{key}={value}" for key, value in kwargs.items())
        full_message = f"❌ {message}" + (f" | {extra_message}" if extra_message else "")
        return LogHandler.get_logger().error(full_message, backtrace=True, diagnose = True)
    
    def debug(self, message: Optional[str] = None, **kwargs):
        extra_message = " | ".join(f"{key}={value}" for key, value in kwargs.items())
        full_message = f"🔍 {message}" + (f" | {extra_message}" if extra_message else "")
        return LogHandler.get_logger().debug(full_message)