import pywikibot
import argparse
import tomllib
import click

import requests

from sources import DriblDataSource

class UnsupportedDatasourceException(Exception):
  pass


@click.group()
def wikifoot():
  pass

@wikifoot.command('table')
@click.option('--site', default='en:Wikipedia', required=False, help="The Wiki site to edit on, in the format `lang:name`")
@click.option('--config', required=True, help="The league to edit, provided as a path to a file")
@click.option("--dry-run", required=False, help="Run the template generation, without editing the wiki page")
def table(site: str, config: str, dry_run: bool):
  with open(config, 'rb') as f:
    toml = tomllib.load(f)

    if toml["datasource"]["type"] == "dribl":
      source = DriblDataSource()
      table = source.get_table(toml)
      # TODO: create template from table
    else:
      raise UnsupportedDatasourceException()

if __name__ == "__main__":
  wikifoot()