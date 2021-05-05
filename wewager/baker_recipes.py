from pytz import UTC
from datetime import datetime
from model_bakery.recipe import Recipe, related
from django.contrib.auth.models import User

import wewager.models


prices = ["-120", "+120", "-220", "+220"]
o_make = lambda x: Recipe(wewager.models.GameOutcome, bet_price=x, hit=None)
outcomes = map(o_make, prices)

game_recipe = Recipe(wewager.models.Game, ended=False, date=datetime.now(tz=UTC))

game_with_outcomes = game_recipe.extend(outcomes=related(*outcomes))

user_recipe = Recipe(User)
