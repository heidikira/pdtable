import io
from pathlib import Path
from textwrap import dedent

from pdtable import Table, TableDataFrame
from pdtable import TableBundle, read_csv, read_excel
# TBC: group these types in same import
from pdtable.demo.unit_converter import convert_this
from pdtable.utils import read_bundle_from_csv


def input_dir() -> Path:
    return Path(__file__).parent / "input"


def test_read_bundle_from_csv():
    """ verify that custom UnitPolicy translates kg to g
        verify that read_bundle_from_csv can be called with
          unit_policy as an instance
          unit_policy as a type
    """
    # fmt off
    instr = dedent(
        """\
        **farm_types1;;;
        your_farm my_farm farms_galore;;;
        species;  num;  flt;    log;
        text;       -;   kg;  onoff;
        chicken;    2;    3;      1;
        pig;        4;   39;      0;
        goat;       4;    -;      1;
        zybra;      4;    -;      0;
        cow;      NaN;  200;      1;
        goose;      2;    9;      0;
        """
    )
    # fmt on

    # test 1]: unit_policy as an instance
    stream = io.StringIO(instr)
    ucs = {"farm_types1": {"flt": "g"}}
    bundle = read_bundle_from_csv(stream, unit_conversion_schedule=ucs, unit_converter=convert_this)

    assert len(bundle) > 0

    for tab in bundle:
        assert tab["flt"].unit == "g"
        assert tab["flt"].values[4] == 200000

    # test 2]: unit_policy as a type
    stream = io.StringIO(instr)
    bundle = read_bundle_from_csv(stream, unit_conversion_schedule=ucs, unit_converter=convert_this)
    assert len(bundle) > 0
    for tab in bundle:
        assert tab["flt"].unit == "g"
        assert tab["flt"].values[0] == 3000


def test_TableBundlebundle_from_file():
    """ Verify that TableBundle can be generated from top level AIP methods: read_csv, read_excel
    """
    input_file = input_dir() / "bundle.csv"
    bundle = TableBundle(read_csv(input_file), as_dataframe=True)
    assert bundle is not None
    assert len(bundle) == 3
    assert isinstance(bundle[0], TableDataFrame)

    assert bundle.unique("spelling_numbers").spelling[1] == "six"
    assert bundle[1].spelling[0] == "one"
    assert len(bundle.all("places_to_go")) == 2

    bundle = TableBundle(read_csv(input_file), as_dataframe=False)
    assert bundle is not None
    assert len(bundle) == 3
    assert isinstance(bundle[1], Table)
    assert bundle.spelling_numbers["spelling"].values[0] == "one"
    assert len(bundle.all("places_to_go")) == 2

    input_file = input_dir() / "bundle.xlsx"
    bundle = TableBundle(read_excel(input_file), as_dataframe=False)
    assert bundle is not None
    assert len(bundle) == 3
    assert isinstance(bundle[1], Table)
    assert bundle.spelling_numbers["spelling"].values[0] == "one"
    assert len(bundle.all("places_to_go")) == 2

    bundle = TableBundle(read_excel(input_file), as_dataframe=True)
    assert bundle is not None
    assert len(bundle) == 3
    assert isinstance(bundle[0], TableDataFrame)

    assert bundle.unique("spelling_numbers").spelling[1] == "six"
    assert bundle[1].spelling[0] == "one"
    assert len(bundle.all("places_to_go")) == 2
