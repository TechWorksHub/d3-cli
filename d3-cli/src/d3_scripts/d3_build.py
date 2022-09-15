#! /usr/bin/python3

from pathlib import Path
import multiprocessing as mp
import logging
from tqdm import tqdm
import functools
from .d3_utils import process_claim_file
from .guid_tools import get_guid, check_guids, get_parent_claims, check_guids_array
from .yaml_tools import is_valid_yaml_claim, get_yaml_suffixes, load_claim
from .claim_graph import build_claim_graph
from .build_type_map import build_type_map
from .d3_build_vulnerabilities import build_vulnerabilities
from .json_tools import write_json
import typing


class PathFinder:
    def __init__(self, output_dir):
        self.d3_src_dst_map = {}
        self.output_dir = output_dir

    def add_to_d3_map(self, claim_filepath, folder):
        claim_relative_filepath = claim_filepath.relative_to(folder)
        json_filepath = Path(self.output_dir, str(claim_relative_filepath).replace(".yaml", ".json"))
        self.d3_src_dst_map[str(claim_filepath)] = json_filepath
        return claim_filepath

    def get_json_filepath(self, yaml_filepath: str):
        """Returns the filepath to the JSON file for a given YAML file.

        Args:
            yaml_filepath: The filepath to the YAML file

        Returns:
            The filepath to the JSON file
        """
        json_file_name = self.d3_src_dst_map[yaml_filepath]
        return json_file_name


def claim_handler(file_name):
    stringified_file_name = str(file_name)
    if is_valid_yaml_claim(stringified_file_name):
        return stringified_file_name
    return False


def d3_build(
    d3_folders: typing.Iterable[Path],
    output_dir: Path,
    check_uri_resolves: bool = True,
    pass_on_failure: bool = False,
):
    """Build compressed D3 files from D3 YAML files

    Args:
        d3_folders: The folders containing D3 YAML files to build from.
        output_dir: The directory in which to put the built json directories.
        check_uri_resolves: Whether to check that URIs/refs resolve.
                            This can be very slow, so you may want to
                            leave this off normally.
        pass_on_failure: Whether to allow build to continue on failure
                         to validate file claims
    """
    pathFinder = PathFinder(output_dir=output_dir)

    d3_files = (
        pathFinder.add_to_d3_map(d3_file, d3_folder)
        for d3_folder in d3_folders
        for d3_file in d3_folder.glob("**/*.yaml")
    )

    print("Compiling D3 claims...")
    bar_format = "{desc: <20}|{bar}| {percentage:3.0f}% [{elapsed}]"
    pbar = tqdm(total=100, ncols=80, bar_format=bar_format)
    pbar.set_description("Setting up worker pool ")
    pool_size = max(mp.cpu_count() - 1, 1)
    pool = mp.Pool(processes=pool_size)
    pbar.update(10)

    # Get list of YAML files and check for invalid claims
    pbar.set_description("Finding claims")
    files_to_process = pool.map(claim_handler, d3_files)
    files_to_process = [file for file in files_to_process if file]
    pbar.update(15)

    pbar.set_description("Loading claims")
    behaviour_files = get_files_by_type(files_to_process, "behaviour")
    behaviour_jsons = tuple(pool.map(load_claim, behaviour_files))
    type_files = get_files_by_type(files_to_process, "type")
    type_jsons = tuple(pool.map(load_claim, type_files))
    claim_jsons = behaviour_jsons + type_jsons
    pbar.update(5)

    pbar.set_description("Searching CVE dataset for vulnerabilities")
    cve_vulnerabilities = build_vulnerabilities(type_jsons, pbar, percentage_total=15)
    outputFolder = Path(output_dir, "cve_vulnerabilities")
    Path(outputFolder).mkdir(parents=True, exist_ok=True)
    for vuln in cve_vulnerabilities:
        json_file_name = Path(
            outputFolder, f"{vuln['credentialSubject']['id']}.json"
        )
        # write JSON for CVE vulnerability
        write_json(json_file_name, vuln)
    pbar.update(5)

    # check for duplicate GUID/UUIDs
    pbar.set_description("Checking UUIDs")
    guids = [guid for guid in pool.map(get_guid, claim_jsons) if guid]
    check_guids(guids, files_to_process)
    parent_guids = list(pool.map(get_parent_claims, claim_jsons))
    check_guids_array(parent_guids, files_to_process)
    pbar.update(20)

    # Pass behaviour files into process_claim_file function
    pbar.set_description("Finding inherited rules & checking for vulnerabilities")
    behaviour_map = {
        claim["credentialSubject"]["id"]: claim for claim in behaviour_jsons
    }
    behaviour_graph = build_claim_graph(behaviour_map)
    type_map = build_type_map(type_jsons)
    process_claim = functools.partial(
        process_claim_file,
        behaviour_map=behaviour_map,
        behaviour_graph=behaviour_graph,
        type_map=type_map,
        check_uri_resolves=check_uri_resolves,
        pass_on_failure=pass_on_failure,
        get_json_filepath=pathFinder.get_json_filepath,
    )
    pbar.update(10)

    pbar.set_description("Processing claims")
    for i, warnings in enumerate(pool.map(process_claim, files_to_process)):
        for warning in warnings:
            logging.warning(f"{warning} in {files_to_process[i]}")

    pool.close()
    pbar.update(20)
    pbar.set_description("Done!")
    pbar.close()


def get_files_by_type(files, type_code):
    return [file for file in files if get_yaml_suffixes(file)[0] == "." + type_code]

