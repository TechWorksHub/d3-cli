import logging
from pathlib import Path
import typing

from .yaml_tools import is_valid_yaml_claim, load_claim, lint_yaml
from .json_tools import check_json_unchanged, get_json_file_name, write_json
from .validate_schemas import get_schema_from_path, get_schema_from_d3_claim, validate_schema
from .check_uri_resolve import check_uri_resolve


def validate_d3_claim_files(yaml_file_names: typing.List[str]):
    """Checks whether D3 claim files are valid.

    Performs each check sequentially, (e.g. like a normal CI task)
    so if one fails, the rest are not checked.
    """
    logging.info("Checking if D3 files have correct filename")
    for file in yaml_file_names:
        # check if file is YAML with right extension
        is_valid_yaml_claim(file)

    logging.info("Linting D3 files")
    for file in yaml_file_names:
        # check if files have good quality yaml
        lint_yaml(file)

    logging.info("Checking whether D3 files match JSONSchema")
    for file in yaml_file_names:
        # import yaml claim to Python dict (JSON)
        claim = load_claim(file)
        # validate schema
        schema = get_schema_from_d3_claim(file)
        validate_schema(claim["credential-subject"], schema)

    logging.info("Checking whether D3 files have valid URIs/refs")
    for file in yaml_file_names:
        # import yaml claim to Python dict (JSON)
        claim = load_claim(file)
        schema = get_schema_from_path(file)
        # check URIs and other refs resolve
        check_uri_resolve(claim, schema)
    return True


def process_claim_file(yaml_file_name: str):
    # check if file is YAML with right extension
    is_valid_yaml_claim(yaml_file_name)

    json_file_name = get_json_file_name(yaml_file_name)

    # import yaml claim to Python dict (JSON)
    claim = load_claim(yaml_file_name)

    # if JSON already exists and is unchanged then skip
    check_json_unchanged(json_file_name, claim)

    # validate schema
    schema = get_schema_from_path(yaml_file_name)
    validate_schema(claim["credential-subject"], schema)

    # check URIs and other refs resolve
    check_uri_resolve(claim, schema)

    # write JSON if valid
    write_json(json_file_name, claim)
    return True
