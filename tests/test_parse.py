import pytest


from pl_pipeline import parse
from pl_pipeline.config import ParseError, TableNotFoundError
from tests import fixtures




def test_parse_visible_table():
    df = parse.parse_table(fixtures.season_page(), r"^results.*_overall$")
    assert "Squad" in df.columns
    assert len(df) == 5  # includes repeated header + blank rows (cleaned later)




def test_parse_table_hidden_in_comment_flattens_headers():
    df = parse.parse_table(fixtures.season_page(hidden=True), r"^stats_squads_keeper_for$")
    assert "Playing Time_Min" in df.columns
    assert "Performance_GA" in df.columns
    assert "Squad" in df.columns




def test_missing_table_raises():
    with pytest.raises(TableNotFoundError):
        parse.parse_table("<html><body><p>nothing</p></body></html>", "nope")




def test_empty_html_raises():
    with pytest.raises(ParseError):
        parse.parse_table("   ", "x")




def test_comment_without_table_is_skipped():
    html = "<html><body><!-- just a comment --><!--<div>no table</div>--></body></html>"
    with pytest.raises(TableNotFoundError):
        parse.parse_table(html, "x")




def test_empty_table_raises():
    html = "<table id='t'><thead><tr><th>A</th></tr></thead><tbody></tbody></table>"
    with pytest.raises(ParseError):
        parse.parse_table(html, "t")




def test_unreadable_table_raises():
    with pytest.raises(ParseError):
        parse.parse_table("<table id='t'></table>", "t")




def test_parse_season_url():
    url = parse.parse_season_url(fixtures.HISTORY_HTML, "2024-2025")
    assert url == "https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats"




def test_parse_season_url_missing():
    with pytest.raises(ParseError):
        parse.parse_season_url(fixtures.HISTORY_HTML, "1999-2000")




def test_player_stats_url():
    url = parse.player_stats_url("https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats")
    assert url == "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"




def test_player_stats_url_bad_input():
    with pytest.raises(ParseError):
        parse.player_stats_url("https://fbref.com/en/comps/9/")



