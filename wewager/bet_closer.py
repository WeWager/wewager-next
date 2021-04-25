from typing import Mapping, Callable

from wewager.models import Game, GameOutcome, Wager, WagerState


resolvers = {}

class BetCloser:

    @staticmethod
    def resolver(bet_type: str):
        def inner(func):
            resolvers[bet_type] = func
        return inner

    @staticmethod
    def resolve_bet(outcome: GameOutcome, game: Game):
        handler = resolvers.get(outcome.bet_type, None)
        if handler:
            handler(outcome, game)
            outcome.save()

    @staticmethod
    def resolve_game(game: Game):
        for outcome in game.outcomes.all():
            if outcome.hit is None:
                BetCloser.resolve_bet(outcome, game)
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

@BetCloser.resolver("Total Runs")
@BetCloser.resolver("Total Points")
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