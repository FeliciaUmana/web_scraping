from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .config import ExportError

log = logging.getLogger(__name__)

MAX_SHEET_NAME = 31

def export_to_excel(sheets: dict[str, pd.DataFrame], path: str | Path) ->Path:
     """Write each DataFrame to its own sheet; returns the output path."""
     if not sheets:
         raise ExportError("No sheets to export")
     for name, df in sheets.items():
         if len(name) > MAX_SHEET_NAME or any(ch in name for ch in "[]:*?/\\"):
             raise ExportError(f"Invalid Excel sheet name: {name!r}")
         if df is None or df.empty:
             raise ExportError (f"sheet '{name}' is empty")
     path = Path(path)
     try:
         path.parent.mkdir(parents=True, exist_ok=True)
         with pd.ExcelWriter(path, engine="openpyxl") as writer:
             for name, df in sheets.items():
                 df.to_excel(writer, sheet_name=name, index=False)
                 ws =writer.sheets[name]
                 ws.freeze_panes = "A2"
                 for idx, col in enumerate(df.columns, start=1):
                     longest = max([len(str(col))] + [len(str(v)) for v in df[col].head(200)])
                     letter = ws.cell(row=1, column=idx).column_letter
                     ws.column_dimensions[letter].width = min(longest + 2, 40)
     except OSError as exc:
         raise ExportError(f"could not write {path}: {exc}") from exc 
     log.info("wrote %d sheets to %s", len(sheets), path)
     return path

     