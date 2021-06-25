import re
import logging

from wewager.models import Game, GameOutcome, Wager, WagerState


logger = logging.Logger(__name__)

resolvers = {}


class BetCloser:
    @staticmethod
    def resolver(bet_type: str):
        def inner(func):
            resolvers[bet_type] = func

        return inner

    @staticmethod
    def resolve_bet(outcome: GameOutcome, game: Game):
        for resolver in resolvers:
            if re.match(resolver, outcome.bet_type):
                handler = resolvers[resolver]
                logger.debug(f"Resolver {resolver} matched.")
                handler(outcome, game)
                outcome.save()
                return
        logger.error(f"ERROR: No resolver matched {outcome.bet_type}")

    @staticmethod
    def resolve_game(game: Game):
        for outcome in game.outcomes.all():
            logger.debug(f"Resolving {outcome.description}...")
            if outcome.hit is None:
                BetCloser.resolve_bet(outcome, game)
            wagers = Wager.objects.filter(outcome=outcome,
                                          status=WagerState.ACCEPTED)
            for wager in wagers:
                wager.complete(outcome.hit)
                wager.save()


@BetCloser.resolver("Moneyline")
def moneyline(outcome: GameOutcome, game: Game):
    data = game.data
    winner = max(data["participants"], key=lambda x: x["score"])
    hit = winner["name"] in outcome.description
    outcome.hit = hit


@BetCloser.resolver("Total (Points|Runs)")
def total_points(outcome: GameOutcome, game: Game):
    data = game.data
    total = sum([x["score"] for x in data["participants"]])

    desc_split = outcome.description.split()
    direction = desc_split[0]
    amount = float(desc_split[1])

    if direction == "Over":
        outcome.hit = total > amount
    elif direction == "Under":
        outcome.hit = total < amount


@BetCloser.resolver("(Point Spread|Run Line)")
def point_spread(outcome: GameOutcome, game: Game):
    teams = game.data["participants"]
    direction = "+" if "+" in outcome.description else "-"
    split = outcome.description.split(direction)
    team_name, line = split[0].strip(), float(split[1])
    if direction == "-":
        line *= -1

    matching_team = next(x for x in teams if x["name"] == team_name)
    other_team = next(x for x in teams if x != matching_team)

    matching_team["score"] += line

    winner = max((matching_team, other_team), key=lambda x: x["score"])
    outcome.hit = winner == matching_team
