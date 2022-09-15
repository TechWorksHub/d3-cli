#! /usr/bin/python3
from tqdm import tqdm
from pathlib import Path

from .export_tools import CsvExporter
from .d3_build import d3_build


def d3_build_db(json_dir: Path, csv_dir: Path):
    csv_exporter = CsvExporter(csv_dir=csv_dir)
    if not json_dir.exists():
        print("D3 claims not compiled. Compiling now...")
        d3_build()

    print("Exporting D3 claims...")
    # sort so that the *.csv files are relatively consistent
    files_to_process = sorted(json_dir.glob("**/*.d3.json"))

    csv_exporter.create_csv_templates()

    bar_format = "{bar}| {percentage:3.0f}% ({n_fmt}/{total_fmt}) [{elapsed}]"
    for file in tqdm(files_to_process, bar_format=bar_format, ncols=80):
        csv_exporter.d3_json_export_csv(file)
