import pandas as pd


from pl_pipeline import config, pipeline
from tests import fixtures




class StubFetcher:
    def __init__(self, fail=False):
        self.fail, self.urls = fail, []


    def get(self, url):
        self.urls.append(url)
        if self.fail:
            from pl_pipeline.config import FetchError
            raise FetchError("down")
        if url == config.HISTORY_URL:
            return fixtures.HISTORY_HTML
        if "/stats/" in url:
            return fixtures.players_page()
        return fixtures.season_page()




def test_run_end_to_end(tmp_path):
    out = tmp_path / "pl.xlsx"
    pipeline.run(output=str(out), fetcher=StubFetcher())
    book = pd.read_excel(out, sheet_name=None)
    assert set(book) == {"Standings", "Top Scorers", "Squad Goalkeeping", "Player Stats"}
    assert book["Standings"].loc[0, "Squad"] == "Alpha FC"




def test_main_success(monkeypatch, tmp_path):
    monkeypatch.setattr(pipeline, "Fetcher", lambda: StubFetcher())
    assert pipeline.main(["--output", str(tmp_path / "o.xlsx"), "-v"]) == 0




def test_main_failure_returns_1(monkeypatch, tmp_path):
    monkeypatch.setattr(pipeline, "Fetcher", lambda: StubFetcher(fail=True))
    assert pipeline.main(["--output", str(tmp_path / "o.xlsx")]) == 1


