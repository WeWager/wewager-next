import json
from os import environ
from scrapy import Spider, Request


KEY = environ.get("DATAFEEDS_API_KEY")


class DataFeedsSpider(Spider):
    name = "datafeeds"
    start_urls = [
        f"https://draftkings.datafeeds.net/api/json/odds/v3/900/draftkings/basketball/nba/all?api-key={KEY}",
        f"https://draftkings.datafeeds.net/api/json/odds/v3/900/draftkings/baseball/mlb/all?api-key={KEY}",
        f"https://caesars.datafeeds.net/api/json/odds/v3/60/caesars/hockey/nhl/moneyline?api-key={KEY}",
        f"https://bookmaker.datafeeds.net/api/json/odds/v3/60/bookmaker/soccer/england-premier-league/moneyline?api-key={KEY}",
    ]

    def parse(self, response):
        data = json.loads(response.body)
        for idx in data["games"]:
            game = data["games"][idx]
            game["__TYPE__"] = self.name
            yield game
