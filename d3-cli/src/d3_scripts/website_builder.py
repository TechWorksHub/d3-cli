#! /usr/bin/python3
from .d3_to_markdown import behaviour_to_markdown, type_to_markdown
from .write_pelican_config import write_pelican_config

import pelican
import logging
import os


def build_website(d3_files, output_path, web_address):
    content_path = output_path / "content"
    behaviour_dir = output_path / "behaviours"
    logging.info(f"building website in {output_path}")

    for directory_path in [output_path, content_path, behaviour_dir]:
        if not os.path.isdir(directory_path):
            os.makedirs(directory_path)
    write_pelican_config(output_path, web_address)

    behaviour_d3_files = [
        file for file in d3_files if "behaviour.d3.json" in file.name]

    logging.info(f"Converting {len(behaviour_d3_files)} behaviour files....")

    for file in behaviour_d3_files:
        behaviour_to_markdown(file, behaviour_dir)
    other_d3_files = list(set(d3_files) ^ set(behaviour_d3_files))
    type_d3_files = [
        file for file in other_d3_files if "type.d3.json" in file.name]

    logging.info(f"Converting {len(type_d3_files)} type files....")
    for file in type_d3_files:
        type_to_markdown(file, output_path / "content",
                         behaviour_dir, web_address=web_address)

    pelicanConfPath = str(output_path / "pelicanconf.py")
    pelicanOutputPath = str(output_path / "output")
    logging.info(
        f"Using pelican to build html from {content_path}" +
        " using config file {pelicanConfPath} in {pelicanOutputPath}")
    pelican.main([str(content_path), "-s",
                 pelicanConfPath, "-o", pelicanOutputPath])
