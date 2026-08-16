"""Polite HTTP fetcher with disk caching, custom User-Agent, and rate limiting."""

import os
import time

import requests


class PoliteFetcher:
    """Handles polite HTTP requests with local disk caching and timeout protection."""

    DEFAULT_USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/CodeJamjamzz/Backend_AI_Assignment5)"
    DEFAULT_TIMEOUT_SECONDS = 10.0
    DEFAULT_POLITE_DELAY_SECONDS = 0.5

    def __init__(
        self,
        cache_dir: str = "cache",
        user_agent: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        polite_delay: float = DEFAULT_POLITE_DELAY_SECONDS,
    ):
        self.cache_dir = cache_dir
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT
        self.timeout = timeout
        self.polite_delay = polite_delay
        self._last_request_time: float = 0.0

        os.makedirs(self.cache_dir, exist_ok=True)

    def _apply_polite_delay(self) -> None:
        """Enforces a polite delay between consecutive live HTTP network requests."""
        if self._last_request_time > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.polite_delay:
                time.sleep(self.polite_delay - elapsed)
        self._last_request_time = time.time()

    def fetch(
        self,
        url: str,
        cache_filename: str | None = None,
        force_refresh: bool = False,
    ) -> tuple[str, bool, int, int]:
        """
        Fetch HTML content from cache or live network.

        Returns:
            Tuple[content, is_cache_hit, status_code, size_in_bytes]
        """
        cache_path = os.path.join(self.cache_dir, cache_filename) if cache_filename else None

        # 1. Check disk cache
        if cache_path and os.path.exists(cache_path) and not force_refresh:
            with open(cache_path, "r", encoding="utf-8") as f:
                content = f.read()
            size = len(content.encode("utf-8"))
            print(f"[CACHE HIT] {cache_filename} ({size:,} bytes)")
            return content, True, 200, size

        # 2. Polite delay for live network request
        self._apply_polite_delay()

        # 3. Live network fetch
        headers = {"User-Agent": self.user_agent}
        max_retries = 1
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                # 4. Check status code
                if response.status_code != 200:
                    if response.status_code >= 500 and attempt < max_retries:
                        print(f"[FETCH RETRY] {url} returned HTTP {response.status_code}, retrying...")
                        time.sleep(1.0)
                        continue
                    print(f"[FETCH FAILED] {url} returned HTTP {response.status_code}")
                    raise ValueError(f"HTTP {response.status_code} received from {url}")
                break # Success
            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    print(f"[FETCH RETRY] {url} timed out, retrying...")
                    time.sleep(1.0)
                    continue
                raise RuntimeError(f"Network request timeout for {url}: {e}") from e
            except requests.RequestException as e:
                print(f"[FETCH ERROR] {url}: {e}")
                raise RuntimeError(f"Network request failed for {url}: {e}") from e

        content = response.text
        size = len(content.encode("utf-8"))

        # 5. Save to disk cache
        if cache_path:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(content)

        print(f"[FETCH] {url} -> {cache_filename or 'memory'} ({size:,} bytes)")
        return content, False, 200, size
