import asyncio

async def run_async(func, *args, **kwargs):
    """Helper to run async functions in a synchronous context."""
    return await func(*args, **kwargs)