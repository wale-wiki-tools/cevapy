from abc import abstractmethod
from datetime import datetime
from typing import TypedDict

import pywikibot
import pywikibot.textlib
import mwparserfromhell
import requests
import re
from exceptions import PageNotFoundException

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

class TablePosition(TypedDict):
  name: str
  wins: int
  draws: int
  losses: int
  goals_for: int
  goals_against: int

class DataSource:
  def __init__(self):
    self.table: list[TablePosition] = []
  
  @abstractmethod
  def get_table(self, config) -> list[TablePosition]:
    """
    Returns a dictionary representing the (ordered) current table.
    """
    pass

  @abstractmethod
  def find_replace(self, config, dry_run: bool) -> str:
    """
    Finds and replaces information in an existing Wikipedia template.
    """
    pass

class DriblDataSource(DataSource):
  def get_table(self, config) -> list[TablePosition]:
    ladders_query_params = {
      "date_range": "default",
      "ladder_type": "regular", # no support for finals series, knockouts etc
      "competition": config["datasource"]["dribl"]["comp-id"],
      "league": config["datasource"]["dribl"]["league-id"],
    }

    ladders_req = requests.get("https://mc-api.dribl.com/api/ladders", params=ladders_query_params, headers=headers)
    ladders = ladders_req.json()

    for team in ladders["data"]:
      position = TablePosition(
        name=team["attributes"]["club_name"],
        wins=team["attributes"]["won"],
        draws=team["attributes"]["drawn"],
        losses=team["attributes"]["lost"],
        goals_for=team["attributes"]["goals_for"],
        goals_against=team["attributes"]["goals_against"]
      )
      self.table.append(position)

    return self.table

  def find_replace(self, config, dry_run: bool, year: str = None) -> str:
    page = config["season"]["page-format"]
    if year:
      page = page.replace("%year", year)
    else:
      page = page.replace("%year", str(datetime.now().year))

    site = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(site, page)
    
    if page.exists():
        sections = pywikibot.textlib.extract_sections(page.text, site)
        table_section = sections.sections[config["season"]["section-index"]]
        wikicode = mwparserfromhell.parse(table_section)
        table_templates = wikicode.filter_templates()
        template_code = table_templates[0]

        code = str(template_code)

        # Generate 'update' time
        code = re.sub(r"(\|update)=([a-zA-Z0-9\s\(\)]+)", rf"\g<1>={datetime.now().strftime("%d %B %Y")}\n", code)

        for team in self.table:
          # Crude name normalisation logic
          name = re.sub(r'(FC|SC|AFC|CF)', '', team["name"]).strip()
          name_overrides = config["datasource"]["dribl"]["name-overrides"]
          if name in name_overrides:
            name = name_overrides[name]

          normalized_name = name.lower().replace(" ", "-")
          config_team = config["teams"][normalized_name][0]

          abbrev = config_team["abbrev"]

          code = re.sub(rf"(\|win_{abbrev})=(\d)+", rf"\g<1>={team["wins"]}", code)
          code = re.sub(rf"(\|draw_{abbrev})=(\d)+", rf"\g<1>={team["draws"]}", code)
          code = re.sub(rf"(\|loss_{abbrev})=(\d)+", rf"\g<1>={team["losses"]}", code)
          code = re.sub(rf"(\|gf_{abbrev})=(\d)+", rf"\g<1>={team["goals_for"]}", code)
          code = re.sub(rf"(\|ga_{abbrev})=(\d)+", rf"\g<1>={team["goals_against"]}", code)
        
        print(code)
    else:
        raise PageNotFoundException("This bot only supports _existing_ Wikipedia pages.")