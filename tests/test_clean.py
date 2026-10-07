import pandas as pd
import pytest

from pl_pipeline import clean, parse
from pl_pipeline.config import ParseError
from tests import fixtures

@pytest.fixture
def raw_standings():
    return parse.parse_table(fixtures.season_page(), r"^results.*_overall$")


@pytest.fixture
def raw_players():
    return parse.parse_table(fixtures.players_page(), r"^stats_standard$")

def test_standings_removes_junk_rows(raw_standings):
    df = clean.clean_standings(raw_standings)
    assert list(df["Squad"]) == ["Alpha FC", "Beta United", "Gamma Town"]
    
    
def test_standings_types_and_gd(raw_standings):
    df = clean.clean_standings(raw_standings)
    assert pd.api.types.is_integer_dtype(df["MP"])
    assert pd.api.types.is_numeric_dtype(df["GF"])
    assert df.loc[0, "GD"] == 45  # '+45' handled / recomputed
    
    
def test_standings_derived_metrics(raw_standings):
    df = clean.clean_standings(raw_standings)
    assert df.loc[0, "Pts_per_game"] == round(84/38, 2)
    assert df.loc[0, "Goals_per_game"] == round(86/38, 2)
    assert df.loc[0, "Win_pct"] == round(25/38 * 100, 1)
    
    
def test_standings_zero_matches_gives_nan():
    df = pd.DataFrame({"Squad": ["X"], "MP": [0], "W": [0], "D": [0], "L": [0], "GF": [0], "GA": [0], "Pts": [0]})
    out = clean.clean_standings(df)
    assert pd.isna(out.loc[0, "Pts_per_game"])


def test_standings_missing_columns():
    with pytest.raises(ParseError):
        clean.clean_standings(pd.DataFrame({"Squad": ["X"], "MP": [1]}))




def test_clean_frame_missing_key():
    with pytest.raises(ParseError):
        clean.clean_frame(pd.DataFrame({"a": [1]}), "Squad")




def test_goalkeeping_thousands_separator():
    raw = parse.parse_table(fixtures.season_page(), r"^stats_squads_keeper_for$")
    df = clean.clean_goalkeeping(raw)
    assert df.loc[0, "Playing Time_Min"] == 3420




def test_players_drop_repeated_header(raw_players):
    df = clean.clean_players(raw_players)
    assert "Player" not in set(df["Player"])
    assert len(df) == 4




def test_top_scorers_ranking_and_tiebreak(raw_players):
    scorers = clean.top_scorers(clean.clean_players(raw_players), limit=3)
    assert list(scorers["Player"]) == ["Ann Striker", "Bob Winger", "Cal Mid"]  # tie on 29 -> assists
    assert list(scorers["Rank"]) == [1, 2, 3]
    assert scorers.loc[0, "Goals_per_90"] == round(29 / 3100 * 90, 2)




def test_top_scorers_without_minutes():
    df = pd.DataFrame({"Player": ["A", "B"], "Gls": [3, 5], "Ast": [0, 1]})
    out = clean.top_scorers(df)
    assert out.loc[0, "Player"] == "B"
    assert "Goals_per_90" not in out.columns




def test_top_scorers_empty():
    with pytest.raises(ParseError):
        clean.top_scorers(pd.DataFrame())




def test_top_scorers_missing_goals_column():
    with pytest.raises(ParseError):
        clean.top_scorers(pd.DataFrame({"Player": ["A"]}))


