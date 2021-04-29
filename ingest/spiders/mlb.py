import json
from scrapy import Spider, Request
from datetime import datetime, timedelta
import dateutil.parser

from wewager.models import Game


class MlbSpider(Spider):
    name = "mlb"

    def expand(self, name):
        return name.replace("NY ", "New York ")

    def start_requests(self):
        bdt = datetime.today()
        edt = bdt - timedelta(days=1)
        begin, end = bdt.strftime("%Y-%m-%d"), edt.strftime("%Y-%m-%d")

        yield Request(
            f"https://bdfed.stitch.mlbinfra.com/bdfed/transform-mlb-scoreboard?stitch_env=prod&sortTemplate=4&sportId=1&startDate={end}&endDate={begin}&gameType=E&&gameType=S&&gameType=R&&gameType=F&&gameType=D&&gameType=L&&gameType=W&&gameType=A&language=en&leagueId=104&&leagueId=103&contextTeamId="
        )
        yield Request(
            f"https://statsapi.web.nhl.com/api/v1/schedule?startDate={end}&endDate={begin}&hydrate=team(leaders(categories=[points,goals,assists],gameTypes=[R])),linescore,broadcasts(all),tickets,game(content(media(epg),highlights(scoreboard)),seriesSummary),radioBroadcasts,metadata,decisions,scoringplays,seriesSummary(series)&site=en_nhl&teamId=&gameType=&timecode="
        )

    def parse(self, response):
        data = json.loads(response.body)
        for date in data["dates"]:
            for game in date["games"]:
                home_name = self.expand(game["teams"]["home"]["team"]["name"])
                away_name = self.expand(game["teams"]["away"]["team"]["name"])
                yield {
                    "__TYPE__": self.name,
                    "mlb_id": game["gamePk"],
                    "date": date["date"],
                    "description": f"{away_name} vs {home_name}",
                    "participants": [
                        {"name": home_name, "score": game["teams"]["home"].get("score", 0)},
                        {"name": away_name, "score": game["teams"]["away"].get("score", 0)},
                    ],
                    "status": game["status"]["detailedState"],
                    "ended": game["status"]["detailedState"] in ["Final", "Game Over"],
                }
