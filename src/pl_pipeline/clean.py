"""Cleaning and feature engineering."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from . import config
from .config import ParseError

log = logging.getLogger(__name__)

# Columns that are text and must never be coerced to numbers.
TEXT_COLUMNS = {
    "Squad", "Player", "Nation", "Pos", "Notes", "Last 5",
    "Top Team Scorer", "Goalkeeper", "Matches",
}


def clean_frame(df: pd.DataFrame, key_column: str) -> pd.DataFrame:
    """Generic clean-up: whitespace, empty rows, repeated headers, dtypes."""
    if key_column not in df.columns:
        raise ParseError(f"Expected column '{key_column}' not found; got {list(df.columns)}")

    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # strip stray whitespace in text cells, turn blanks into NaN
    for col in [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]:
        df[col] = df[col].map(lambda v: v.strip() if isinstance(v, str) else v).replace({"": np.nan})

    df = df.dropna(how="all")
    df = df.dropna(subset=[key_column])
    # FBref repeats the header row every ~25 rows inside the table body
    df = df[df[key_column] != key_column]
    # Drop pure-padding columns (entirely empty)
    df = df.dropna(axis=1, how="all")

    for col in df.columns:
        if col in TEXT_COLUMNS:
            continue
        cleaned = df[col].astype(str).str.replace(",", "", regex=False).str.replace("+", "", regex=False)
        numeric = pd.to_numeric(cleaned, errors="coerce")
        non_null = df[col].notna().sum()
        # only convert if the column is predominantly numeric
        if non_null and numeric.notna().sum() >= 0.8 * non_null:
            df[col] = numeric

    return df.reset_index(drop=True)


def clean_standings(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the league table and add derived metrics."""
    df = clean_frame(df, "Squad")
    required = {"MP", "W", "D", "L", "GF", "GA", "Pts"}
    missing = required - set(df.columns)
    if missing:
        raise ParseError(f"Standings table missing columns: {sorted(missing)}")

    df["MP"] = df["MP"].astype(int)
    df["GD"] = df["GF"] - df["GA"]  # recomputed: source has '+' signs / text
    played = df["MP"].replace(0, np.nan)
    df["Pts_per_game"] = (df["Pts"] / played).round(2)
    df["Goals_per_game"] = (df["GF"] / played).round(2)
    df["Goals_conceded_per_game"] = (df["GA"] / played).round(2)
    df["Win_pct"] = (df["W"] / played * 100).round(1)
    if "Rk" in df.columns:
        df = df.sort_values("Rk")
    return df.reset_index(drop=True)


def clean_goalkeeping(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the squad goalkeeping table."""
    return clean_frame(df, "Squad")


def clean_players(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the player stats table."""
    return clean_frame(df, "Player")


def _find_col(df: pd.DataFrame, suffix: str) -> str:
    for col in df.columns:
        if col == suffix or col.endswith(f"_{suffix}"):
            return col
    raise ParseError(f"No '{suffix}' column in player table")


def top_scorers(players: pd.DataFrame, limit: int = config.TOP_SCORERS_LIMIT) -> pd.DataFrame:
    """Rank players by goals (ties broken by assists, then fewer minutes)."""
    if players.empty:
        raise ParseError("No player data to rank")
    goals = _find_col(players, "Gls")
    assists = _find_col(players, "Ast")
    minutes = next((c for c in players.columns if c.endswith("Min")), None)

    sort_cols, ascending = [goals, assists], [False, False]
    if minutes:
        sort_cols.append(minutes)
        ascending.append(True)

    ranked = players.sort_values(sort_cols, ascending=ascending).head(limit).copy()
    ranked.insert(0, "Rank", range(1, len(ranked) + 1))
    keep = ["Rank", "Player", "Squad", "Nation", "Pos", "Age", goals, assists]
    if minutes:
        keep.append(minutes)
    ranked = ranked[[c for c in keep if c in ranked.columns]]
    renames = {goals: "Goals", assists: "Assists"}
    if minutes:
        renames[minutes] = "Minutes"
    ranked = ranked.rename(columns=renames)
    if minutes:
        ranked["Goals_per_90"] = (ranked["Goals"] / ranked["Minutes"].replace(0, np.nan) * 90).round(2)
    return ranked.reset_index(drop=True)

