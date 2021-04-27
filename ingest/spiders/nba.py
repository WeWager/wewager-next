import json
from scrapy import Spider
from datetime import datetime

from wewager.models import Game


class NbaSpider(Spider):
    name = "nba"
    start_urls = [
        "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
    ]

    def expand(self, name: str):
        if "LA " in name:
            return name.replace("LA ", "Los Angeles ")
        return name

    def parse(self, response):
        data = json.loads(response.body)
        for game in data["scoreboard"]["games"]:
            home_name = self.expand(
                f"{game['homeTeam']['teamCity']} {game['homeTeam']['teamName']}"
            )
            away_name = self.expand(
                f"{game['awayTeam']['teamCity']} {game['awayTeam']['teamName']}"
            )
            description = f"{away_name} vs {home_name}"
            yield {
                "__TYPE__": self.name,
                "nba_id": game["gameId"],
                "description": description,
                "participants": [
                    {"name": home_name, "score": game["homeTeam"]["score"]},
                    {"name": away_name, "score": game["awayTeam"]["score"]},
                ],
                "status": game["gameStatusText"].strip(),
                "ended": game["gameStatusText"].strip() in ["Final", "Final/OT"],
            }


"""
class NbaBoxScoreSpider(Spider):
    name = "nba_boxscore"

    def start_requests(self):
        base_url = "https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{id}.json"
        games = Game.objects.filter(date__lte=datetime.now(), ended=False).values_list(
            "data__nba_id", flat=True
        )
        for game_id in games:
            url = base_url.format(id=game_id)
            yield url

    def parse(self, response):
        yield json.loads(response.body)

"""
