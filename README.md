# Premier League Web Scraping & Data Pipeline

Scrapes 2024/25 Premier League data from [FBref](https://fbref.com/en/comps/9/history/Premier-League-Seasons),
cleans it, derives extra metrics and exports everything to one Excel workbook (one sheet per dataset).

## Pipeline

```
fetch.py  ->  parse.py  ->  clean.py  ->  export.py        (orchestrated by pipeline.py)
```

| Stage  | Module        | What it does |
|--------|---------------|--------------|
| Fetch  | `fetch.py`    | Checks `robots.txt` (fails closed), enforces a 6 s gap between requests (FBref allows 10/min), retries on network errors / 429 / 5xx with back-off, honours `Retry-After`. |
| Parse  | `parse.py`    | Finds the season URL on the history page, locates tables by id (**including tables hidden inside HTML comments**, which FBref does a lot), flattens two-level headers. |
| Clean  | `clean.py`    | Strips whitespace, drops empty rows / repeated header rows / empty columns, converts types (`+45`, `3,420` -> numbers), adds metrics. |
| Export | `export.py`   | Writes each DataFrame to its own sheet with frozen header row and sized columns; validates sheet names and non-empty data. |

### Output sheets (`output/premier_league_2024_2025.xlsx`)
- **Standings** – final table plus `Pts_per_game`, `Goals_per_game`, `Goals_conceded_per_game`, `Win_pct`, recomputed `GD`
- **Top Scorers** – top 20 by goals (tie-break: assists, then fewer minutes) with `Goals_per_90`
- **Squad Goalkeeping** – squad goalkeeping table
- **Player Stats** – full cleaned player standard stats

## Setup

```bash
poetry install
# or add the dependencies manually, as in the task:
poetry add requests beautifulsoup4 pandas openpyxl lxml pytest
poetry add --group dev pytest-cov
```

## Run

```bash
poetry run pl-pipeline                       # default: season 2024-2025
poetry run pl-pipeline --season 2023-2024 --output output/pl_2023_24.xlsx -v
```
The run makes only 4 requests (robots.txt, history, season page, player stats page) and takes ~20 s because of the rate limit.

## Tests

```bash
poetry run pytest          # coverage is configured in pyproject.toml (fails below 80%)
```
Tests run fully offline using small HTML fixtures in `tests/fixtures.py` and fake HTTP sessions; nothing hits fbref.com.
Current result: **43 passed, 99% coverage** (see `coverage_report.txt`).

## Sample output
`output/sample_output.xlsx` was generated from the **synthetic test fixtures** (3 made-up teams) to show the workbook layout.
Running the pipeline against the live site produces `output/premier_league_2024_2025.xlsx` with real data.

## Known limitations / future improvements
- Table ids and header names reflect FBref's current layout; a site redesign would require updating the regexes in `pipeline.py`.
- Top scorers are derived from the player-stats table rather than FBref's "Top Scorers" leaderboard widget.
- Only the standard-stats and goalkeeping tables are scraped; shooting, passing, defensive and xG tables could be added the same way.
- No response caching: each run re-downloads pages. Caching raw HTML to disk would reduce load on FBref and speed up development.
- No Excel charts or conditional formatting; could be added with openpyxl.
- Possible extension: multiple seasons in one run, and a scheduled refresh (cron/GitHub Actions).

## Data access note (HTTP 403)

FBref's `robots.txt` permits the pages this pipeline needs (the history page, the
season page and the player stats page); only paths such as `/my/`, `/fbref/`,
`/feedback/` and `/linker/` are disallowed. However, automated requests to
fbref.com were rejected with **HTTP 403 Forbidden** by the site's bot protection.
The pipeline handles this by failing safely with a clear error message.

To produce the final workbook, the three pages were saved manually from a browser
("Webpage, HTML only") into `saved_pages/` as `history.html`, `season.html` and
`players.html`, and the pipeline was run in offline mode:

    poetry run pl-pipeline --html-dir saved_pages

Live fetching is still implemented (`poetry run pl-pipeline`) and works whenever
the site allows automated access. No attempt is made to bypass the block.

## Known limitations
- The `Nation` column keeps FBref's raw format (e.g. `eg EGY`).
- Top scorers are derived from the player stats table, not FBref's leaderboard widget.
- Table ids and header names follow FBref's current layout; a redesign would need
  the regexes in `pipeline.py` updated.