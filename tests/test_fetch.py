import pytest
import requests


from pl_pipeline import config
from pl_pipeline.config import FetchError, RobotsDisallowedError
from pl_pipeline.fetch import Fetcher




class FakeResp:
    def __init__(self, status=200, text="", headers=None):
        self.status_code, self.text, self.headers = status, text, headers or {}


    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))




class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.headers = {}
        self.calls = []


    def get(self, url, timeout=None):
        self.calls.append(url)
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item




def make(responses, **kw):
    sleeps = []
    f = Fetcher(FakeSession(responses), sleep=sleeps.append, check_robots=kw.pop("check_robots", False), **kw)
    return f, sleeps




def test_success():
    f, _ = make([FakeResp(200, "<html/>")])
    assert f.get("https://fbref.com/x") == "<html/>"




def test_retries_on_500_then_succeeds():
    f, sleeps = make([FakeResp(500), FakeResp(200, "ok")])
    assert f.get("https://fbref.com/x") == "ok"
    assert sleeps  # backed off




def test_429_uses_retry_after():
    f, sleeps = make([FakeResp(429, headers={"Retry-After": "12"}), FakeResp(200, "ok")])
    f.get("https://fbref.com/x")
    assert 12.0 in sleeps




def test_network_error_then_success():
    f, _ = make([requests.ConnectionError("boom"), FakeResp(200, "ok")])
    assert f.get("https://fbref.com/x") == "ok"




def test_gives_up_after_max_retries():
    f, _ = make([FakeResp(503)] * config.MAX_RETRIES)
    with pytest.raises(FetchError, match="Giving up"):
        f.get("https://fbref.com/x")




def test_404_not_retried():
    f, _ = make([FakeResp(404)])
    with pytest.raises(FetchError, match="404"):
        f.get("https://fbref.com/x")
    assert len(f.session.calls) == 1




def test_rate_limit_sleeps_between_requests():
    t = [0.0]
    sleeps = []
    f = Fetcher(FakeSession([FakeResp(200, "a"), FakeResp(200, "b")]), min_delay=6.0,
                sleep=sleeps.append, clock=lambda: t[0], check_robots=False)
    f.get("https://fbref.com/1")
    t[0] = 2.0
    f.get("https://fbref.com/2")
    assert sleeps == [4.0]




def test_robots_disallow():
    robots = FakeResp(200, "User-agent: *\nDisallow: /private/")
    f, _ = make([robots], check_robots=True)
    with pytest.raises(RobotsDisallowedError):
        f.get("https://fbref.com/private/page")




def test_robots_allow_and_cached():
    robots = FakeResp(200, "User-agent: *\nDisallow: /private/")
    f, _ = make([robots, FakeResp(200, "a"), FakeResp(200, "b")], check_robots=True)
    f.get("https://fbref.com/public")
    f.get("https://fbref.com/public2")
    assert f.session.calls.count(config.ROBOTS_URL) == 1




def test_robots_unreadable_fails_closed():
    f, _ = make([FakeResp(500)], check_robots=True)
    with pytest.raises(FetchError, match="robots"):
        f.get("https://fbref.com/x")
