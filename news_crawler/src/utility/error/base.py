
from news_crawler.src.utility.logger import LogHandler

logger = LogHandler("./logs/errors.txt")


class BaseError(Exception):
    """
    Base class for all errors in this package.
    """
    def __init__(self,
                 error_root='base',
                 message='An error occurred'):
        self.error_root = error_root
        self.message = message
        
        error_message = f"Error with {error_root} | with {message}"
        logger.error(error_message)
        
        # Truyền lỗi trên Exception
        super().__init__(error_message)