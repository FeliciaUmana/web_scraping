"""Check our URLs against a copy of FBref's real robots.txt (no network)."""
import pytest

from pl_pipeline import config
from pl_pipeline.fetch import Fetcher

ROBOTS_TXT = """User-agent:*
Disallow: /fbref/
Disallow: /feedback/
Disallow: /linker/
Disallow: /my/

User-agent: GPTBot
Disallow: /

User-agent: AhrefsBot
Disallow: /
"""


class _Resp:
    status_code = 200
    text = ROBOTS_TXT

    def raise_for_status(self):
        pass


class _Session:
    headers = {}

    def get(self, url, timeout=None):
        return _Resp()


@pytest.fixture
def fetcher():
    return Fetcher(_Session(), sleep=lambda s: None)


@pytest.mark.parametrize("url", [
    config.HISTORY_URL,
    "https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats",
    "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats",
])
def test_pipeline_urls_are_allowed(fetcher, url):
    assert fetcher.allowed(url) is True


@pytest.mark.parametrize("path", ["/my/account", "/fbref/x", "/feedback/", "/linker/a"])
def test_disallowed_paths_are_blocked(fetcher, path):
    assert fetcher.allowed(f"https://fbref.com{path}") is False