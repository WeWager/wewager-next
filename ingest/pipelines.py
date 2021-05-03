import pytz
from datetime import datetime
import dateutil.parser
from itemadapter import ItemAdapter

from wewager.models import Game, GameOutcome


UTC = pytz.timezone("UTC")


class IngestPipeline:
    def process_item(self, item, spider):
        return item


class GamePipeline:
    def shorten(self, name):
        aliases = {
            "England - Premier League": "EPL",
            "New Jersey Islanders": "New York Islanders",
        }
        if name in aliases:
            return aliases[name]
        return name

    def process_item(self, item, spider):
        if item.get("__TYPE__", None) == "datafeeds":
            dt = datetime.fromisoformat(item["startDate"][:-1])
            utc_dt = UTC.localize(dt)
            game, g_created = Game.objects.get_or_create(
                description=item["description"],
                date=utc_dt,
                external_uid=item["gameUID"],
                league=self.shorten(item["league"]),
            )

            outcome_dt = datetime.fromisoformat(item["startDate"][:-1])
            outcome, o_created = GameOutcome.objects.get_or_create(
                external_uid=item["id"],
                description=item["betName"],
                bet_type=item["betType"],
                bet_price=item["betPrice"],
                update_dt=UTC.localize(outcome_dt),
            )
            if o_created:
                game.outcomes.add(outcome)
        return item


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
