import datetime as dt
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

from .._read_excel_openpyxl import make_table, parse_blocks
from ..read_excel import read_excel
from ... import Table
from ...store import BlockType


def test_make_table():
    lines = [
        ["**foo", None, None, None],
        ["all", None, None, None],
        ["place", "distance", "ETA", "is_hot"],
        ["text", "km", "datetime", "onoff"],
        ["home", 0.0, dt.datetime(2020, 8, 4, 8, 0, 0), 1],
        ["work", 1.0, dt.datetime(2020, 8, 4, 9, 0, 0), 0],
        ["beach", 2.0, dt.datetime(2020, 8, 4, 17, 0, 0), 1],
        ["wonderland", "-", "-", "FALSE"],
    ]

    t = make_table(lines)

    assert t.name == "foo"
    assert set(t.metadata.destinations) == {"all"}
    assert t.column_names == ["place", "distance", "ETA", "is_hot"]
    assert t.units == ["text", "km", "datetime", "onoff"]

    df = pd.DataFrame(
        [
            ["home", 0.0, dt.datetime(2020, 8, 4, 8, 0, 0), True],
            ["work", 1.0, dt.datetime(2020, 8, 4, 9, 0, 0), False],
            ["beach", 2.0, dt.datetime(2020, 8, 4, 17, 0, 0), True],
            ["wonderland", np.nan, np.nan, False],
        ],
        columns=["place", "distance", "ETA", "is_hot"],
    )
    pd.testing.assert_frame_equal(t.df, df)


def test_parse_blocks():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["**foo"])
    ws.append(["all"])
    ws.append(["place", "distance"])
    ws.append(["text", "km"])
    ws.append(["ha", 1.0])
    ws.append([])
    ws.append(["**bar"])
    ws.append(["all"])
    ws.append(["a", "b", "c"])
    ws.append(["-", "-", "onoff"])
    ws.append([42, 66, 1])
    ws.append([1, 2, 0])
    ws.append([3, 4, 1])

    blocks = list(parse_blocks(ws))
    tables = [block for (block_type, block) in blocks if block_type == BlockType.TABLE]

    assert tables[0].name == "foo"
    assert tables[0].column_names == ["place", "distance"]
    assert len(tables[0].df) == 1
    assert tables[1].name == "bar"
    assert tables[1].column_names == ["a", "b", "c"]
    assert len(tables[1].df) == 3


def test_read_excel():

    # Prepare the expected tables.
    # Note: not testing datetime columns due to upstream bug in openpyxl:
    # timestamps are off by one microsecond.
    # https://foss.heptapod.net/openpyxl/openpyxl/-/issues/1493

    t0 = Table(name="places_to_go")
    t0["place"] = ["home", "work", "beach", "wonderland"]
    t0.add_column("distance", list(range(3)) + [float("nan")], "km")
    t0.add_column("is_hot", [True, False, True, False], "onoff")

    t1 = Table(name="spelling_numbers")
    t1.add_column("number", [1, 6, 42], "-")
    t1.add_column("spelling", ["one", "six", "forty-two"], "text")

    expected_tables = [t0, t1]

    # Read tables from file
    blocks = read_excel(Path(__file__).parent / "input" / "foo.xlsx")
    tables_read = [block for (block_type, block) in blocks if block_type == BlockType.TABLE]
    assert len(expected_tables) == len(tables_read)

    # Assert read tables are equal to the expected ones
    for te, tr in zip(expected_tables, tables_read):
        assert te.equals(tr)

