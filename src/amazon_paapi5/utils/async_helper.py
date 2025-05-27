import asyncio
import functools
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

def async_to_sync(func: Callable) -> Callable:
    """
    Decorator to convert async function to sync function.
    
    Args:
        func: Async function to convert
        
    Returns:
        Synchronous wrapper function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return asyncio.run(func(*args, **kwargs))
    return wrapper

async def run_async(func: Callable, *args, **kwargs) -> Any:
    """
    Helper to run async functions in a synchronous context.
    
    Args:
        func: Async function to run
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
        
    Returns:
        Result of the async function
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Async execution failed: {str(e)}", exc_info=True)
        raise

async def gather_with_concurrency(limit: int, *tasks) -> list:
    """
    Run tasks with concurrency limit.
    
    Args:
        limit: Maximum number of concurrent tasks
        *tasks: Tasks to run
        
    Returns:
        List of task results
    """
    semaphore = asyncio.Semaphore(limit)
    
    async def wrapped_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(
        *(wrapped_task(task) for task in tasks),
        return_exceptions=True
    )