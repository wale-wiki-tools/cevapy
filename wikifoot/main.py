import argparse
import tomllib

import click
import pywikibot
import requests
from exceptions import UnsupportedDatasourceException
from sources import DriblDataSource


@click.group()
def wikifoot():
    pass


@wikifoot.command("table")
@click.option(
    "--site",
    default="en:Wikipedia",
    required=False,
    help="The Wiki site to edit on, in the format `lang:name`",
)
@click.option(
    "--config", required=True, help="The league to edit, provided as a path to a file"
)
@click.option(
    "--year",
    required=False,
    help="The current season to work with (e.g. 2025 NPL Victoria, 2024/25 Premier League)",
)
@click.option(
    "--dry-run",
    required=False,
    help="Run the template generation, without editing the wiki page",
)
def table(site: str, config: str, year: str, dry_run: bool):
    with open(config, "rb") as f:
        toml = tomllib.load(f)

        match toml["datasource"]["type"]:
            case "dribl":
                source = DriblDataSource()
                table = source.get_table(toml)
                template = source.find_replace(toml, dry_run, year)
            # TODO: create template from table
            case _:
                raise UnsupportedDatasourceException()


if __name__ == "__main__":
    wikifoot()
