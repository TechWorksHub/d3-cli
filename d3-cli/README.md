# ManySecured d3-cli

Utility cli for ManySecured-D3 claims

## Installation

This api may be installed using pip like so:

```
pip install d3-cli
```

When developing these scripts, [Python Poetry](https://python-poetry.org/)
is used to install and manage dependencies as well as publish to [PyPI](https://pypi.org/).

Poetry will create a python isolated virtual environment in the `./.venv` folder and install dependencies if you run:

```bash
poetry install
```

You cannot run the cli or scripts directly from the `./src/d3-scripts` since we are using [Python relative imports](https://realpython.com/absolute-vs-relative-python-imports/#relative-imports).

Instead, you must run the d3-cli script defined in the `[tool.poetry.scripts]` field of [`pyproject.toml`](./pyproject.toml): You can run the command line interface locally, directly from source code without building/installing by running `poetry run d3-cli`.

In order for the pelican graphviz plugin which generates the digraph's in the webpage to work you need to have graphviz installed on your pc. For linux machines this can be done with `sudo apt install graphviz`, for windows graphviz installers may be downloaded [from here](https://graphviz.org/download/).

## Usage

```console
usage: d3-cli [-h] [--version] [--guid] [--output [OUTPUT]]
              [--mode [{build,lint,export}]] [--build-dir [BUILD_DIR]]
              [--check_uri_resolves] [--verbose | --quiet]
              [input ...]

ManySecured D3 CLI for creating, linting and exporting D3 claims

positional arguments:
  input                 Folders containing D3 YAML files. (default: [])

optional arguments:
  -h, --help            show this help message and exit
  --version             Show the version and exit. (default: False)
  --guid, --uuid        Generate and show guid and exit. (default:
                        False)
  --output [OUTPUT]     Directory in which to output built claims.
                        (default: <cwd>/d3-build)
  --mode [{build,lint,export}], -m [{build,lint,export}]
                        Mode to run d3-cli in. (default: build)
  --build-dir [BUILD_DIR]
                        Build directory with json claims to export.
                        Specifying this will skip build step in export
                        mode. (default: None)
  --check_uri_resolves  Check that URIs/refs resolve. This can be very
                        slow, so you may want to leave this off
                        normally. (default: False)
  --verbose, -v
  --quiet, -q

Example: d3-cli ./manufacturers
```

## Tests

Tests can be run via:

```bash
poetry run pytest
```

## Publish

The d3-cli utility is published [here](https://pypi.org/project/d3-cli/).

In order to publish you must run:

```
poetry build
poetry publish
```

And then enter the credentials for the NquiringMinds pypi account.
