#! /usr/bin/python3
from .guid import guid
from .d3_build import d3_build
from .d3_build_db import d3_build_db
from .d3_utils import validate_d3_claim_files

from tempfile import TemporaryDirectory
import argparse
from pathlib import Path
import logging

__version__ = "0.1.0"


def cli(argv=None):
    parser = argparse.ArgumentParser(
        description="ManySecured D3 CLI for creating, linting and exporting D3 claims",
        epilog="Example: d3-cli ./manufacturers",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input",
        nargs="*",
        help="Folders containing D3 YAML files.",
        default=[],
        type=Path,
    )
    parser.add_argument(
        "--mode",
        "-m",
        nargs="?",
        help="Mode to run d3-cli in.",
        default="build",
        choices=["build", "lint", "export"],
    )
    parser.add_argument(
        "--version", action="store_true", help="Show the version and exit.",
    )
    parser.add_argument(
        "--guid",
        "--uuid",
        action="store_true",
        help="Generate and show guid and exit.",
    )
    parser.add_argument(
        "--output",
        nargs="?",
        help="Directory in which to output built claims.",
        default=Path.cwd(),
        type=Path,
    )
    parser.add_argument(
        "--build-dir",
        nargs="?",
        help="""Build directory with json claims to export.
        Specifying this will skip build step in export mode.""",
        default=Path.cwd(),
        type=Path,
    )
    parser.add_argument(
        "--check_uri_resolves",
        action="store_true",
        help="""Check that URIs/refs resolve.
        This can be very slow, so you may want to leave this off normally.""",
    )

    debug_level_group = parser.add_mutually_exclusive_group()
    debug_level_group.add_argument(
        "--verbose", "-v", dest="log_level", action="append_const", const=-10,
    )
    debug_level_group.add_argument(
        "--quiet", "-q", dest="log_level", action="append_const", const=10,
    )

    args = parser.parse_args(argv)

    if args.version:
        # TODO: check this version number is correct when installed
        logging.info(f"d3-cli, version {__version__}")
        return

    if args.guid:
        guid()
        return

    log_level_sum = min(sum(args.log_level or tuple(), logging.INFO), logging.ERROR)
    logging.basicConfig(level=log_level_sum)

    if len(args.input) == 0:
        logging.warning("No directories provided, Exiting...")
        return

    print(args.input)

    if args.mode == "lint":
        logging.info("linting")
        d3_files = list(
            (
                d3_file
                for d3_folder in args.input
                for d3_file in d3_folder.glob("**/*.yaml")
            )
        )

        try:
            validate_d3_claim_files(
                d3_files, check_uri_resolves=args.check_uri_resolves
            )
        except Exception as error:
            logging.error(error)
        logging.info("All files passed linting successfully.")

    elif args.mode == "build":
        logging.info("building")
        try:
            d3_build(
                d3_folders=args.input,
                output_dir=args.output,
                check_uri_resolves=args.check_uri_resolves,
            )
        except Exception as error:
            logging.error(error)

    elif args.mode == "export":
        logging.info("exporting")
        if args.build_dir:
            build_dir = Path(args.build_dir)
            if not build_dir.exists():
                raise Exception("Non existent build-dir provided. Exiting.")
        else:
            temp_dir = TemporaryDirectory()
            build_dir = Path(temp_dir.name)
            try:
                d3_build(
                    d3_folders=args.input,
                    output_dir=build_dir,
                    check_uri_resolves=args.check_uri_resolves,
                )
            except Exception as error:
                logging.error(error)
        try:
            d3_build_db(build_dir, args.output)
        except Exception as error:
            logging.error(error)
        try:
            temp_dir.cleanup()
        except NameError:
            pass

    else:
        raise Exception("unknown mode")


if __name__ == "__main__":
    cli()
