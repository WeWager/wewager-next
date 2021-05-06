import pytz
import logging
from datetime import datetime
import dateutil.parser
from typing import Mapping
from collections import defaultdict

from wewager.models import Game, GameOutcome


logger = logging.Logger(__name__)


UTC = pytz.timezone("UTC")


class IngestPipeline:
    def process_item(self, item, spider):
        return item


class GamePipeline:
    gathered_outcomes: Mapping

    def open_spider(self, spider):
        self.gathered_outcomes = defaultdict(list)

    def normalize(self, name):
        aliases = {
            "England - Premier League": "EPL",
            "New Jersey Islanders": "New York Islanders",
        }
        if name in aliases:
            return name.replace(aliases[name])
        return name

    def process_item(self, item, spider):
        if item.get("__TYPE__", None) == "datafeeds":
            dt = datetime.fromisoformat(item["startDate"][:-1])
            utc_dt = UTC.localize(dt)
            game, g_created = Game.objects.get_or_create(
                external_uid=item["gameUID"],
            )
            if g_created:
                game.description = self.normalize(item["description"])
                game.date = utc_dt
                game.league = self.normalize(item["league"])
                game.save()

            outcome_dt = datetime.fromisoformat(item["startDate"][:-1])
            outcome, o_created = GameOutcome.objects.get_or_create(
                external_uid=item["id"],
            )
            outcome.description = item["betName"]
            outcome.bet_type = item["betType"]
            outcome.bet_price = item["betPrice"]
            outcome.update_dt = UTC.localize(outcome_dt)
            outcome.save()

            game.outcomes.add(outcome)
            self.gathered_outcomes[game].append(outcome.id)
        return item

    def close_spider(self, spider):
        for game in self.gathered_outcomes.keys():
            outcomes = self.gathered_outcomes[game]
            logging.debug(f"Closing out {game}, outcomes: {outcomes}")
            logging.debug(game.outcomes.all().exclude(id__in=outcomes).update(is_latest=False))


class ScorePipeline:
    def process_item(self, item, spider):
        if item.pop("__TYPE__", None) in ["nba", "mlb", "epl"]:
            date = dateutil.parser.parse(item.pop("date")).date()
            game = (
                Game.objects.filter(description=item.pop("description"))
                .order_by("date")
                .filter(date_eastern__date=date, ended=False)
                .first()
            )
            if game:
                game.data = item
                game.ended = item.pop("ended")
                game.save()
        return item
