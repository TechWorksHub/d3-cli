import pytest
from pathlib import Path
import json
import d3_scripts.d3_build


def assert_string_in_error(string, error_message):
    assert string in error_message


def test_duplicated_guids():
    # should throw an error due to duplicate UUID
    test_dir = Path(__file__).parent / "__fixtures__" / "duplicate-uuid"
    output_dir = test_dir / "json"
    with pytest.raises(Exception) as excinfo:
        d3_scripts.d3_build.d3_build(
            d3_folders=[test_dir],
            output_dir=output_dir,
            skip_mal=True,
        )
    assert "Duplicate GUIDs" in excinfo.value.args[0]


def test_invalid_uri(caplog):
    """Test whether invalid uris log a warning and whether valid URIs don't log a warning
    """
    test_dir = Path(__file__).parent / "__fixtures__" / "invalid-uri"
    output_dir = test_dir / "json"
    for json_file in (output_dir).glob("*.json"):
        try:
            json_file.unlink()
        except FileNotFoundError:
            pass  # can't use missing_ok = True since it's only added in Python 3.8

    d3_scripts.d3_build.d3_build(
        d3_folders=[test_dir],
        output_dir=output_dir,
        check_uri_resolves=True,
        skip_mal=True,
    )
    for record in caplog.records:
        assert "URI https://nquiringminds.com.invalid cannot be resolved" in record.message

    caplog.clear()
    test_dir = Path(__file__).parent / "__fixtures__" / "valid-uri"
    output_dir = test_dir / "json"
    # should work as long as nquiringminds.com is resolvable
    d3_scripts.d3_build.d3_build(
        d3_folders=[test_dir],
        output_dir=output_dir,
        check_uri_resolves=True,
        skip_mal=True,
    )
    # should be empty, as all URIs are valid
    assert len(caplog.records) == 0


def test_non_existent_parent_behaviour():
    """Test whether behaviours with non-existent parents raises an error"""
    test_dir = Path(__file__).parent / "__fixtures__" / \
        "non-existent-parent-behaviour"
    output_dir = test_dir / "json"
    with pytest.raises(Exception) as excinfo:
        d3_scripts.d3_build.d3_build(
            d3_folders=[test_dir],
            output_dir=output_dir,
            skip_mal=True,
        )
    for string in ["Parent behaviour id", "doesn't exist"]:
        assert string in excinfo.value.args[0]


def test_circular_behaviour_dependencies():
    """Test whether behaviours with circular parent dependencies raise an error"""
    test_dir = Path(__file__).parent / "__fixtures__" / \
        "circular-type-dependence"
    output_dir = test_dir / "json"
    with pytest.raises(Exception) as excinfo:
        d3_scripts.d3_build.d3_build(
            d3_folders=[test_dir],
            output_dir=output_dir,
            skip_mal=True,
        )
    assert "Graph has Cyclic dependency" in excinfo.value.args[0]


def test_non_existent_parent_type():
    """Test whether types with non-existent parents raises an error"""
    test_dir = Path(__file__).parent / "__fixtures__" / \
        "non-existent-parent-type"
    output_dir = test_dir / "json"
    with pytest.raises(Exception) as excinfo:
        d3_scripts.d3_build.d3_build(
            d3_folders=[test_dir],
            output_dir=output_dir,
            skip_mal=True,
        )
    for string in ["Parent type with id", "doesn't exist"]:
        assert string in excinfo.value.args[0]


def test_duplicate_property_type_inheritance():
    """Test whether inheriting duplicate properties from types raises an error"""
    test_dir = Path(__file__).parent / "__fixtures__" / \
        "duplicate-property-type-inheritance"
    output_dir = test_dir / "json"
    with pytest.raises(Exception) as excinfo:
        d3_scripts.d3_build.d3_build(
            d3_folders=[test_dir],
            output_dir=output_dir,
            skip_mal=True,
        )
    assert "Duplicate inherited properties in type definition" in excinfo.value.args[0]


def test_inherit_missing_property():
    """Test whether attempting to inherit missing properties from parent types raises an error"""
    test_dir = Path(__file__).parent / "__fixtures__" / \
        "missing-property-type-inheritance"
    output_dir = test_dir / "json"
    with pytest.raises(Exception) as excinfo:
        d3_scripts.d3_build.d3_build(
            d3_folders=[test_dir],
            output_dir=output_dir,
            skip_mal=True,
        )
    assert "Attempted to inherit missing property" in excinfo.value.args[0]


def test_firmware_with_missing_type():
    """Tests whether a firmware with a type which is missing raises an error"""
    test_dir = Path(__file__).parent / "__fixtures__" / "firmware-missing-type"
    output_dir = test_dir / "json"
    with pytest.raises(Exception) as excinfo:
        d3_scripts.d3_build.d3_build(
            d3_folders=[test_dir],
            output_dir=output_dir,
            skip_mal=True,
        )
    for string in ["Type", "of firmware claim", "not found"]:
        assert string in excinfo.value.args[0]


def test_duplicate_property_type_inheritance_single_parent():
    """Test whether inheriting duplicate properties from a single parent type is ignored"""
    test_dir = Path(__file__).parent / "__fixtures__" / \
        "duplicate-property-type-inheritance-single-parent"
    output_dir = test_dir / "json"
    # should succeed
    d3_scripts.d3_build.d3_build(
        d3_folders=[test_dir],
        output_dir=output_dir,
        skip_mal=True,
    )


def test_cpe_resoolves():
    """Test whether inheriting duplicate properties from a single parent type is ignored"""
    test_dir = Path(__file__).parent / "__fixtures__" / "cpe"
    output_dir = test_dir / "json"
    # should succeed
    d3_scripts.d3_build.d3_build(
        d3_folders=[test_dir],
        output_dir=output_dir,
        skip_mal=True,
    )


def test_inherited_rulename_conflict():
    """Test whether behaviour inheriting a rule with duplicate name to a behaviour rule resolves without duplication"""
    test_dir = Path(__file__).parent / "__fixtures__" / \
        "inherited-rulename-conflict"
    output_dir = test_dir / "json"
    # should succeed
    d3_scripts.d3_build.d3_build(
        d3_folders=[test_dir],
        output_dir=output_dir,
        skip_mal=True,
    )
    # should not have duplicate rule names
    for json_file in (output_dir).glob("*behaviour.d3.json"):
        with json_file.open() as f:
            data = json.load(f)
        assert len(data["credentialSubject"]["rules"]) == len(set(rule["name"] for rule in data["credentialSubject"]["rules"]))


def test_build():
    # should succeed
    test_dir = Path(__file__).parent / "__fixtures__" / "d3-build"
    output_dir = test_dir / "json"
    d3_scripts.d3_build.d3_build(
        d3_folders=[test_dir],
        output_dir=output_dir,
    )
