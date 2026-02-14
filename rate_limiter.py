"""
Rate Limiter for API Calls
Prevents exceeding API quotas during batch operations.
"""

import time
from collections import deque
from threading import Lock
from functools import wraps


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    Usage:
        limiter = RateLimiter(calls_per_minute=60)
        limiter.wait()  # Call before each API request
    """

    def __init__(self, calls_per_minute: int = 60, calls_per_second: int = None):
        """
        Initialize rate limiter.

        Args:
            calls_per_minute: Maximum calls allowed per minute
            calls_per_second: Maximum calls per second (overrides calls_per_minute if set)
        """
        if calls_per_second:
            self.min_interval = 1.0 / calls_per_second
        else:
            self.min_interval = 60.0 / calls_per_minute

        self.last_call = 0
        self.lock = Lock()

    def wait(self):
        """
        Wait if necessary to respect rate limit.
        Call this before making an API request.
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_call
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
            self.last_call = time.time()

    def __call__(self, func):
        """Decorator to rate-limit a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper


class BurstRateLimiter:
    """
    Sliding window rate limiter that allows bursts.

    Usage:
        limiter = BurstRateLimiter(max_calls=10, window_seconds=60)
        limiter.wait()  # Call before each API request
    """

    def __init__(self, max_calls: int, window_seconds: float):
        """
        Initialize burst rate limiter.

        Args:
            max_calls: Maximum calls allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = deque()
        self.lock = Lock()

    def wait(self):
        """
        Wait if necessary to respect rate limit.
        """
        with self.lock:
            now = time.time()

            # Remove calls outside the window
            while self.calls and self.calls[0] < now - self.window_seconds:
                self.calls.popleft()

            # If at capacity, wait until oldest call exits window
            if len(self.calls) >= self.max_calls:
                sleep_time = self.calls[0] + self.window_seconds - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Clean up again after sleeping
                    now = time.time()
                    while self.calls and self.calls[0] < now - self.window_seconds:
                        self.calls.popleft()

            self.calls.append(time.time())


# Pre-configured rate limiters for different APIs
# Adjust these based on your API tier limits

# Claude API: 60 requests/minute for most tiers
claude_limiter = RateLimiter(calls_per_minute=50)  # Leave some headroom

# Runware API: ~2 requests/second recommended
runware_limiter = RateLimiter(calls_per_second=2)

# YouTube API: 10,000 quota units/day, search = 100 units each
# Conservative: 100 searches/day = ~4/hour = 1 every 15 minutes in batches
youtube_limiter = BurstRateLimiter(max_calls=5, window_seconds=300)  # 5 calls per 5 minutes


def rate_limited(limiter: RateLimiter):
    """
    Decorator to apply rate limiting to a function.

    Usage:
        @rate_limited(claude_limiter)
        def call_claude_api(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait()
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Convenience functions for direct use
def wait_for_claude():
    """Call before making a Claude API request."""
    claude_limiter.wait()


def wait_for_runware():
    """Call before making a Runware API request."""
    runware_limiter.wait()


def wait_for_youtube():
    """Call before making a YouTube API request."""
    youtube_limiter.wait()


if __name__ == "__main__":
    # Test the rate limiters
    print("Testing RateLimiter (5 calls/second)...")
    limiter = RateLimiter(calls_per_second=5)

    start = time.time()
    for i in range(10):
        limiter.wait()
        print(f"  Call {i+1} at {time.time() - start:.2f}s")

    print(f"\n10 calls took {time.time() - start:.2f}s (expected ~2s)")

    print("\nTesting BurstRateLimiter (3 calls per 2 seconds)...")
    burst_limiter = BurstRateLimiter(max_calls=3, window_seconds=2)

    start = time.time()
    for i in range(6):
        burst_limiter.wait()
        print(f"  Call {i+1} at {time.time() - start:.2f}s")

    print(f"\n6 calls took {time.time() - start:.2f}s (expected ~4s)")
