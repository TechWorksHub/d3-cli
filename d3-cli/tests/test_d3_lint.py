import pytest

import d3_scripts.d3_lint


def test_lint():
    # should pass with no Exception
    d3_scripts.d3_lint.cli([
        "./tests/__fixtures__/d3-build/device-1.type.d3.yaml",
    ])
    with pytest.raises(Exception):
        d3_scripts.d3_lint.cli([
            __file__,  # this file is a python file, not a valid yaml
        ])
