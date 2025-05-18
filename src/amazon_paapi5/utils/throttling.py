import time
import asyncio
from contextlib import contextmanager, asynccontextmanager
from collections import deque
import random

class Throttler:
    def __init__(self, delay: float = 1.0, max_retries: int = 3, max_queue_size: int = 10):
        self.delay = delay
        self.max_retries = max_retries
        self.last_request = 0
        self.request_queue = deque(maxlen=max_queue_size)
        self.base_backoff = 0.5  # Base backoff time in seconds

    def _calculate_backoff(self, retry: int) -> float:
        """Calculate exponential backoff with jitter."""
        return self.base_backoff * (2 ** retry) + random.uniform(0, 0.1)

    @contextmanager
    def __enter__(self):
        retry = 0
        while retry <= self.max_retries:
            elapsed = time.time() - self.last_request
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)

            if len(self.request_queue) < self.request_queue.maxlen:
                self.request_queue.append(time.time())
                try:
                    yield
                    self.last_request = time.time()
                    break
                except Exception as e:
                    if retry == self.max_retries:
                        raise
                    backoff = self._calculate_backoff(retry)
                    time.sleep(backoff)
                    retry += 1
            else:
                time.sleep(self.delay)  # Wait if queue is full

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @asynccontextmanager
    async def __aenter__(self):
        retry = 0
        while retry <= self.max_retries:
            elapsed = time.time() - self.last_request
            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)

            if len(self.request_queue) < self.request_queue.maxlen:
                self.request_queue.append(time.time())
                try:
                    yield
                    self.last_request = time.time()
                    break
                except Exception as e:
                    if retry == self.max_retries:
                        raise
                    backoff = self._calculate_backoff(retry)
                    await asyncio.sleep(backoff)
                    retry += 1
            else:
                await asyncio.sleep(self.delay)  # Wait if queue is full

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass