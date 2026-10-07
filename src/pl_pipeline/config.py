from __future__ import annotations

BASE_URL = "https://fbref.com"
HISTORY_URL = f"{BASE_URL}/en/comps/9/history/Premier-League-Seasons"
ROBOTS_URL = f"{BASE_URL}/robots.txt"
DEFAULT_SEASON = "2024-2025"
DEFAULT_OUTPUT = "output/premier_league_2024_2025.xlsx"

USER_AGENT = "pl-pipeline-student-project/0.1 (educational use)"

MIN_DELAY_SECONDS = 6.0
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
BACKOFF_SECONDS = 5.0
TOP_SCORERS_LIMIT = 20

class PipelineError(Exception):
    """Base class for pipeline errors."""
    
class FetchError(PipelineError):
    """A page could not be downloaded."""
    
class RobotsDisallowedError(FetchError):
    """robots.txt forbids fetching the URL."""
    
class ParseError(PipelineError):
    """HTML could not be parsed into the expected structure."""

class TableNotFoundError(ParseError):
     """The requested table is not on the page."""

class ExportError(PipelineError):
     """The Excel workbook could not be written.""" 


    
    