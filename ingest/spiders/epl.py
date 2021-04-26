import json
from scrapy import Spider, Request


class EplSpider(Spider):
    name = "epl"
    url = "https://footballapi.pulselive.com/football/fixtures?page=0&gameweeks=5696"

    def start_requests(self):
        yield Request(url=self.url, headers={"Origin": "https://www.premierleague.com"})

    def parse(self, response):
        data = json.loads(response.body)
        for game in data["content"]:
            home_name = game["teams"][0]["team"]["name"]
            away_name = game["teams"][1]["team"]["name"]
            yield {
                "__TYPE__": self.name,
                "epl_id": int(game["id"]),
                "description": f"{away_name} vs {home_name}",
                "participants": [
                    {"name": home_name, "score": int(game["teams"][0].get("score", 0))},
                    {"name": away_name, "score": int(game["teams"][1].get("score", 0))},
                ],
                "status": game.get("clock", {}).get("label", ""),
                "ended": game["status"] == "C",
            }
