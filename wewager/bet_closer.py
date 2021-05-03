import re
import logging
from typing import Mapping, Callable

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
        print(f"Finding resolver for {outcome.bet_type}")
        for resolver in resolvers:
            print(f"Trying resolver: {resolver}")
            if re.match(resolver, outcome.bet_type):
                logger.debug(f"Resolver {resolver} matched.")
                handler(outcome, game)
                outcome.save()
                return
            print(f"ERROR: No resolver matched {outcome.bet_type}")

    @staticmethod
    def resolve_game(game: Game):
        for outcome in game.outcomes.all():
            print(f"Resolving {outcome.description}...")
            if outcome.hit is None:
                BetCloser.resolve_bet(outcome, game)
            else:
                print(f"Outcome already calcualted: {outcome.hit}")
            wagers = Wager.objects.filter(outcome=outcome, status=WagerState.ACCEPTED)
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
