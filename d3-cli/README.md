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


## Usage

```console
usage: d3-cli [-h] [--version] [--guid] [--output [OUTPUT]] [--mode [{build,lint,export,website}]] [--skip-mal]
              [--build-dir [BUILD_DIR]] [--check_uri_resolves] [--web-address [WEB_ADDRESS]] [--verbose | --quiet]
              [input ...]

ManySecured D3 CLI for creating, linting and exporting D3 claims

positional arguments:
  input                 folders containing D3 YAML files.

optional arguments:
  -h, --help            show this help message and exit
  --version             show the version and exit.
  --guid, --uuid        generate and show guid and exit.
  --output [OUTPUT], -o [OUTPUT]
                        directory in which to output built claims.
  --mode [{build,lint,export,website}], -m [{build,lint,export,website}]
                        mode to run d3-cli in.
                        build creates a directory of D3 claims in json format, with the parent and child types resolved, and CVEvulnerabilities added.
                        lint lints the claims to check they confirm to the yaml syntax and schemas.
                        export creates a directory with the CSVs of the tables of types, behaviours andfirmwares.
                        website creates a directory containing the source for a static website of claims which can be browsed,with unique uris for each type.
  --skip-mal            skip malicious url lookup.
                                This takes a bit of time, and requires an internet connection
                                so you may wish to skip this step for local testing.
  --build-dir [BUILD_DIR]
                        build directory with json claims to export to build website with.
                                Specifying this will skip build step in export mode and website mode.
  --check_uri_resolves  check that URIs/refs resolve.
                                This can be very slow, so you may want to leave this off normally.
  --web-address [WEB_ADDRESS]
                        web address to use for website build
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

## D3 type explorer web page

This static page is generated from (post-processed) D3 statements and [hosted here](https://techworkshub.github.io/ManySecured-D3DB/). This site relies upon two Github actions in the [D3DB repository](https://github.com/TechWorksHub/ManySecured-D3DB)
- Run D3 Build of website for github pages - processes all files, exporting html files
- Publish website (main-branch only) deploys the pelecan site to Github pages

In order for the pelican graphviz plugin which generates the digraph's in the webpage to work you need to have graphviz installed on your pc. For linux machines this can be done with `sudo apt install graphviz`, for windows graphviz installers may be downloaded [from here](https://graphviz.org/download/).


### Running Locally

To generate the site files inside a defined directory:
```
cd d3-cli
poetry install
poetry run d3-cli --mode website "path-to-d3-yaml-files" --output "output-file" 

```

serving the static site:
```
cd "output-file"/output
python -m http.server 8000
```