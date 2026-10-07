from __future__ import annotations

import logging
import time
from urllib import robotparser

import requests

from . import config
from .config import FetchError, RobotsDisallowedError

log = logging.getLogger(__name__)

class Fetcher:
    """Downloads pages while respecting robots.txt and a minimum delay."""
    def __init__(self, session: requests.Session | None = None,
                 min_delay: float = config.MIN_DELAY_SECONDS, 
                 sleep=time.sleep, 
                 clock=time.monotonic, 
                 check_robots: bool = True,) -> None:
                 self.session = session or requests.Session()
                 self.session.headers.update({"User-Agent": config.USER_AGENT})
                 self.min_delay = min_delay
                 self._sleep = sleep
                 self._clock = clock
                 self.check_robots = check_robots
                 self._last_request: float | None =None
                 self._robots: robotparser.RobotFileParser | None = None
                 
    def _load_robots(self) -> robotparser.RobotFileParser:
            if self._robots is None:
                parser = robotparser.RobotFileParser()
                try:
                    resp = self.session.get(config.ROBOTS_URL, timeout=config.REQUEST_TIMEOUT)
                    resp.raise_for_status()
                    parser.parse(resp.text.splitlines())
                except requests.RequestException as exc:
                    raise FetchError(f"Could not read robots.txt: {exc}") from exc
                self._robots = parser
            return self._robots

    def allowed(self, url: str) -> bool:
            if not self.check_robots:
                return True
            return self._load_robots().can_fetch(config.USER_AGENT, url)
        
        #rate limiting
    def _throttle(self) -> None:
            if self._last_request is not None:
                wait = self.min_delay - (self._clock() - self._last_request)
                if wait > 0:
                    log.debug("sleeping %.1fs to respect rate limit", wait)
                    self._sleep(wait)
            self._last_request = self._clock()
            
            
        #public API
    def get(self, url: str) -> str:
             """Return page HTML or raise FetchError / RobotsDisallowedError."""
             if not self.allowed(url):
                raise RobotsDisallowedError(f'robots.txt disallows {url}')
             last_error: Exception | None = None
             for attempt in range (1, config.MAX_RETRIES + 1):
                 self._throttle()
                 try:
                     log.info("GET %s (attempt %d)", url, attempt)
                     resp = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                 except requests.RequestException as exc:
                     last_error = exc
                     log.warning("Network error for %s: %s", url, exc)
                     self._sleep(config.BACKOFF_SECONDS * attempt)
                     continue
                 if resp.status_code ==200:
                     return resp.text
                 if resp.status_code == 429 or resp.status_code >= 500:
                     last_error = FetchError(f"HTTP {resp.status_code}")
                     retry_after = resp.headers.get("Retry-After", "")
                     delay = float(retry_after) if retry_after.isdigit() else config.BACKOFF_SECONDS * attempt
                     log.warning("HTTP %s for %s, retrying in %.0fs", resp.status_code, url, delay)
                     self._sleep(delay)
                     continue
                 raise FetchError(f"HTTP{resp.status_code} for {url}")
             
             raise FetchError(f"Giving up on {url} after {config.MAX_RETRIES} attempts: {last_error}")
            
            
            
                
                
    
        