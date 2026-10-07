"""Parsing: turn FBref HTML into raw DataFrames."""
from __future__ import annotations

import logging
import re
from io import StringIO
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup, Comment

from . import config
from .config import ParseError, TableNotFoundError

log = logging.getLogger(__name__)


def _soup(html: str) -> BeautifulSoup:
    if not html or not html.strip():
        raise ParseError("Empty HTML document")
    return BeautifulSoup(html, "lxml")


def find_table(html: str, table_id: str):
    """Locate a <table>. `table_id` is a regex matched against the id.

    FBref hides many tables inside HTML comments, so comments are searched too.
    """
    soup = _soup(html)
    pattern = re.compile(table_id)
    table = soup.find("table", id=pattern)
    if table is not None:
        return table
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        if "<table" not in comment:
            continue
        inner = BeautifulSoup(comment, "lxml")
        table = inner.find("table", id=pattern)
        if table is not None:
            return table
    raise TableNotFoundError(f"No table matching id '{table_id}'")


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten FBref's two-level headers, e.g. ('Performance','Gls') -> 'Performance_Gls'."""
    if isinstance(df.columns, pd.MultiIndex):
        names = []
        for group, col in df.columns:
            group, col = str(group).strip(), str(col).strip()
            if group.startswith("Unnamed") or not group:
                names.append(col)
            else:
                names.append(f"{group}_{col}")
        df = df.copy()
        df.columns = names
    return df


def parse_table(html: str, table_id: str) -> pd.DataFrame:
    """Return the matching table as a DataFrame with flat column names."""
    table = find_table(html, table_id)
    try:
        df = pd.read_html(StringIO(str(table)), flavor="lxml")[0]
    except (ValueError, IndexError) as exc:
        raise ParseError(f"Table '{table_id}' could not be read: {exc}") from exc
    df = flatten_columns(df)
    if df.empty:
        raise ParseError(f"Table '{table_id}' has no rows")
    log.info("Parsed table %s: %d rows x %d cols", table_id, *df.shape)
    return df


def parse_season_url(history_html: str, season: str = config.DEFAULT_SEASON) -> str:
    """Find the link to a season's page in the Premier League history table."""
    soup = _soup(history_html)
    pattern = re.compile(rf"/en/comps/9/{re.escape(season)}/")
    link = soup.find("a", href=pattern)
    if link is None:
        raise ParseError(f"Season {season} not found on history page")
    return urljoin(config.BASE_URL, link["href"])


def player_stats_url(season_url: str) -> str:
    """Derive the player-stats page URL from the season overview URL."""
    m = re.search(r"/(\d{4}-\d{4})/", season_url)
    if not m:
        raise ParseError(f"Cannot derive player stats URL from {season_url}")
    season = m.group(1)
    return season_url.replace(f"/{season}/", f"/{season}/stats/", 1)