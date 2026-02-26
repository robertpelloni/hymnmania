import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_request(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Decorator to retry a function call with exponential backoff.

    Args:
        max_retries (int): Maximum number of retries.
        delay (int): Initial delay in seconds.
        backoff (int): Multiplier for delay after each failure.
        exceptions (tuple): Tuple of exceptions to catch and retry on.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries. Error: {e}")
                        raise

                    logger.warning(f"Function {func.__name__} failed (attempt {attempt+1}/{max_retries}). Retrying in {current_delay}s... Error: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
