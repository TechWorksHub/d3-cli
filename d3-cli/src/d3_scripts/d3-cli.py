#! /usr/bin/python3
from guid import guid

import argparse
from pathlib import Path
import logging
from importlib import metadata
__version__ = metadata.version(__package__)
del metadata  # optional, avoids polluting the results of dir(__package__)


def cli(argv=None):
    parser = argparse.ArgumentParser(
        description="ManySecured D3 CLI for creating, linting and exporting D3 claims",
        epilog="Example: d3-cli build manufacturers/",
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
        "--version",
        action="store_true",
        help="Show the version and exit.",
    )
    parser.add_argument(
        "--guid", "--uuid",
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
        "--check_uri_resolves",
        action="store_true",
        help="""Check that URIs/refs resolve.
        This can be very slow, so you may want to leave this off normally.""",
    )
    parser.add_argument(
        "--pass-on-failure",
        help="Allow build to continue on failure to validate file claims.",
        action="store_true",
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
        print(f"d3-cli, version {__version__}")  # TODO: check this version number is correct when installed
        return

    if args.guid:
        guid()
        return

    log_level_sum = min(sum(args.log_level or tuple(),
                        logging.INFO), logging.ERROR)
    logging.basicConfig(level=log_level_sum)

    print(args)


if __name__ == "__main__":
    cli()
