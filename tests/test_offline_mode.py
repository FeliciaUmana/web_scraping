import pandas as pd
import pytest

from pl_pipeline import config, pipeline
from pl_pipeline.config import FetchError
from tests import fixtures


@pytest.fixture
def saved_dir(tmp_path):
    folder = tmp_path / "saved_pages"
    folder.mkdir()
    (folder / "history.html").write_text(fixtures.HISTORY_HTML, encoding="utf-8")
    (folder / "season.html").write_text(fixtures.season_page(), encoding="utf-8")
    (folder / "players.html").write_text(fixtures.players_page(), encoding="utf-8")
    return folder


def test_run_from_saved_pages(saved_dir, tmp_path):
    out = tmp_path / "pl.xlsx"
    pipeline.run(output=str(out), html_dir=str(saved_dir))
    book = pd.read_excel(out, sheet_name=None)
    assert set(book) == {"Standings", "Top Scorers", "Squad Goalkeeping", "Player Stats"}
    assert book["Standings"].loc[0, "Squad"] == "Alpha FC"


def test_missing_saved_page_raises(saved_dir):
    (saved_dir / "players.html").unlink()
    with pytest.raises(FetchError, match="saved page"):
        pipeline.read_saved_pages(saved_dir)


def test_main_with_html_dir(saved_dir, tmp_path):
    code = pipeline.main(["--html-dir", str(saved_dir), "--output", str(tmp_path / "o.xlsx")])
    assert code == 0


def test_main_with_bad_html_dir_returns_1(tmp_path):
    code = pipeline.main(["--html-dir", str(tmp_path / "nope"), "--output", str(tmp_path / "o.xlsx")])
    assert code == 1