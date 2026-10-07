import pandas as pd
import pytest

from pl_pipeline import export
from pl_pipeline.config import ExportError


def test_export_creates_sheets(tmp_path):
    out = tmp_path / "sub" / "out.xlsx"
    export.export_to_excel(
        {"Standings": pd.DataFrame({"Squad": ["A"], "Pts": [1]}), "Top Scorers": pd.DataFrame({"Player": ["P"]})},
        out,
    )
    assert out.exists()
    book = pd.read_excel(out, sheet_name=None)
    assert set(book) == {"Standings", "Top Scorers"}
    assert book["Standings"].loc[0, "Pts"] == 1


def test_export_no_sheets(tmp_path):
    with pytest.raises(ExportError):
        export.export_to_excel({}, tmp_path / "x.xlsx")


def test_export_empty_dataframe(tmp_path):
    with pytest.raises(ExportError):
        export.export_to_excel({"S": pd.DataFrame()}, tmp_path / "x.xlsx")


@pytest.mark.parametrize("name", ["bad/name", "x" * 32, "a:b"])
def test_export_invalid_sheet_name(tmp_path, name):
    with pytest.raises(ExportError):
        export.export_to_excel({name: pd.DataFrame({"a": [1]})}, tmp_path / "x.xlsx")


def test_export_unwritable_path(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    with pytest.raises(ExportError):
        export.export_to_excel({"S": pd.DataFrame({"a": [1]})}, blocker / "out.xlsx")