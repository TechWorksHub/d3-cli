import functools
import logging
from pyclbr import Function
import typing
import warnings
from pathlib import Path
import multiprocessing
from networkx import DiGraph
import tqdm
import jsonschema

from .yaml_tools import is_valid_yaml_claim, load_claim, lint_yaml
from .json_tools import is_json_unchanged, write_json
from .validate_schemas import (
    get_schema_validator_from_path,
    validate_claim_meta_schema,
    validate_d3_claim_schema,
)
from .check_uri_resolve import check_uri
from .check_behaviours_resolve import check_behaviours_resolve, BehaviourMap
from .resolve_behaviour_rules import resolve_behaviour_rules
from .d3_constants import d3_type_codes
from typing import Sequence, Mapping, Any
from copy import deepcopy

TypeJson = Mapping[str, Any]
TypeJsons = Sequence[TypeJson]
LOG = logging.getLogger(__name__)


def _validate_d3_claim_uri(yaml_file_path: str, **check_uri_kwargs):
    """Checks whether the given YAML file has valid URIs.

    Raises:
        Exception: If the YAML file has a URI that is not valid/resolveable.
    """
    # import yaml claim to Python dict (JSON)
    claim = load_claim(yaml_file_path)
    schema = get_schema_validator_from_path(yaml_file_path).schema
    # check URIs and other refs resolve
    check_uri(
        claim["credentialSubject"], schema, **check_uri_kwargs,
    )


def validate_d3_claim_files(
    yaml_file_names: typing.Sequence[str], check_uri_resolves: bool = False
):
    """Checks whether D3 claim files are valid.

    Performs each check sequentially, (e.g. like a normal CI task)
    so if one fails, the rest are not checked.
    """
    stages = {
        "Checking if D3 files have correct filename": is_valid_yaml_claim,
        "Linting D3 files": lint_yaml,
        "Checking whether D3 files match JSONSchema": validate_d3_claim_schema,
        "Checking whether URIs/refs resolve": functools.partial(
            _validate_d3_claim_uri, check_uri_resolves=check_uri_resolves,
        ),
    }

    with multiprocessing.Pool() as pool:
        for description, function in stages.items():
            # use imap so that progress bar only updates when each chunk is done
            result_generator = pool.imap(function, yaml_file_names, chunksize=16)
            for _result in tqdm.tqdm(
                result_generator,
                unit="files",
                desc=description,
                disable=logging.getLogger().getEffectiveLevel() > logging.INFO,
                delay=0.5,  # delay to show progress bar
                total=len(yaml_file_names),
            ):
                pass

    return True


def process_claim_file(
    yaml_file_name: str,
    behaviour_map: BehaviourMap,
    behaviour_graph: DiGraph,
    type_map: BehaviourMap,
    check_uri_resolves: bool,
    pass_on_failure: bool,
    get_json_filepath: Function,
) -> typing.List[Warning]:
    """Processes a single D3 claim file.
    Checks include:
    - is unchanged claim
    - is valid claim relative to JSONSchema for type
    - are all URIs/refs resolveable/valid
    - behaviour statements are valid

    Args:
        yaml_file_name: The filepath to the YAML file
        check_uri_resolves: Whether to check URIs/refs resolveable/valid

    Returns:
        List of warnings. If empty, no warnings.
        Warnings are hidden by default in multiprocessing.
    """
    json_file_name = get_json_filepath(yaml_file_name)
    Path(json_file_name).parent.mkdir(parents=True, exist_ok=True)

    # import yaml claim to Python dict (JSON)
    claim = load_claim(yaml_file_name)

    # if JSON already exists and is unchanged then skip, unless claim has parents (parents may have changed)
    if len(claim.get("credentialSubject", {}).get("parents", [])) and is_json_unchanged(
        json_file_name, claim
    ):
        return []

    # validate schema
    validate_claim_meta_schema(claim)

    try:
        schema_validator = get_schema_validator_from_path(yaml_file_name)
        schema = schema_validator.schema
        try:
            schema_validator.validate(claim["credentialSubject"])
        except jsonschema.exceptions.ValidationError as err:
            raise Exception(f"Error validating credentialSubject for {yaml_file_name}: {err}")

        if claim["type"] == d3_type_codes["behaviour"]:
            # Gets aggregated rules, checking that specified parents exist
            aggregated_rules = resolve_behaviour_rules(
                claim, behaviour_map, behaviour_graph
            )
            # Replace claim rules with aggregated rules from parents
            claim["credentialSubject"]["rules"] = aggregated_rules

        if claim["type"] == d3_type_codes["type"]:
            claim_id = claim["credentialSubject"]["id"]
            # update type claim to use object in type_map - includes inherited properties
            claim = deepcopy(
                type_map[claim_id]
            )  # must use deepcopy to prevent modification of type_map

        if claim["type"] == d3_type_codes["firmware"]:
            firmware_type = claim["credentialSubject"].get("type", None)
            if type_map.get(firmware_type, None) is None:
                raise ValueError(
                    f"Type {firmware_type} of firmware claim {claim['credentialSubject']['id']} not found"
                )
            if claim["credentialSubject"].get("behaviour", None) is None:
                # if no behaviour of it's own, inherit from parent type to which firmware belongs
                type_behaviour = type_map[firmware_type]["credentialSubject"].get(
                    "behaviour", None
                )
                if type_behaviour is not None:
                    claim["credentialSubject"]["behaviour"] = type_behaviour

        # check URIs and other refs resolve
        with warnings.catch_warnings(record=True) as uri_warnings:
            check_uri(
                claim["credentialSubject"],
                schema,
                check_uri_resolves=check_uri_resolves,
            )

        # check behaviour statement is valid, if so add to claim
        claim["credentialSubject"] = check_behaviours_resolve(
            claim["credentialSubject"], schema, behaviour_map.values()
        )

        # write JSON if valid
        write_json(json_file_name, claim)

        return [*uri_warnings]
    except FileNotFoundError as err:
        if pass_on_failure:
            LOG.warn(f"Skipping claim {yaml_file_name} due to error: ${err}")
            return []
        else:
            raise err
