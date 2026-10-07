"""Orchestration and command-line entry point."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import clean, config, export, parse
from .config import FetchError, PipelineError
from .fetch import Fetcher

log = logging.getLogger(__name__)

# Regexes for FBref table ids
STANDINGS_ID = r"^results.*_overall$"
KEEPER_ID = r"^stats_squads_keeper_for$"
PLAYER_ID = r"^stats_standard$"

# File names expected inside --html-dir (pages saved from a browser)
HISTORY_FILE = "history.html"
SEASON_FILE = "season.html"
PLAYERS_FILE = "players.html"


def fetch_pages(season: str, fetcher: Fetcher | None = None) -> tuple[str, str]:
    """Download the season page and the player stats page from FBref."""
    fetcher = fetcher or Fetcher()
    history_html = fetcher.get(config.HISTORY_URL)
    season_url = parse.parse_season_url(history_html, season)
    season_html = fetcher.get(season_url)
    players_html = fetcher.get(parse.player_stats_url(season_url))
    return season_html, players_html


def read_saved_pages(html_dir: str | Path) -> tuple[str, str]:
    """Read the season page and player stats page saved from a browser."""
    folder = Path(html_dir)
    pages = []
    for name in (SEASON_FILE, PLAYERS_FILE):
        path = folder / name
        try:
            pages.append(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise FetchError(f"Could not read saved page {path}: {exc}") from exc
    log.info("Loaded saved pages from %s", folder)
    return pages[0], pages[1]


def run(
    season: str = config.DEFAULT_SEASON,
    output: str = config.DEFAULT_OUTPUT,
    fetcher: Fetcher | None = None,
    html_dir: str | None = None,
):
    """Run fetch -> parse -> clean -> export and return the output path.

    If `html_dir` is given, pages are read from disk instead of downloaded.
    """
    if html_dir:
        season_html, players_html = read_saved_pages(html_dir)
    else:
        season_html, players_html = fetch_pages(season, fetcher)

    standings = clean.clean_standings(parse.parse_table(season_html, STANDINGS_ID))
    keepers = clean.clean_goalkeeping(parse.parse_table(season_html, KEEPER_ID))
    players = clean.clean_players(parse.parse_table(players_html, PLAYER_ID))
    scorers = clean.top_scorers(players)

    return export.export_to_excel(
        {
            "Standings": standings,
            "Top Scorers": scorers,
            "Squad Goalkeeping": keepers,
            "Player Stats": players,
        },
        output,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scrape Premier League data from FBref into Excel")
    ap.add_argument("--season", default=config.DEFAULT_SEASON)
    ap.add_argument("--output", default=config.DEFAULT_OUTPUT)
    ap.add_argument("--html-dir", default=None, help="folder with pages saved from a browser (season.html, players.html)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        path = run(args.season, args.output, html_dir=args.html_dir)
    except PipelineError as exc:
        log.error("Pipeline failed: %s", exc)
        return 1
    log.info("Done: %s", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())