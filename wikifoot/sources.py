from typing import TypedDict
import requests

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
