import json
import requests

from wewager.models import Team


class NBATeams:

    def run():
        resp = requests.get("https://www.balldontlie.io/api/v1/teams")
        data = json.loads(resp.text)
        for team in data["data"]:
            obj, created = Team.objects.get_or_create(
                city=team["city"],
                name=team["name"],
                abbr=team["abbreviation"],
                league="NBA"
            )
            obj.save()

if __name__ == "__main__":
    NBATeams.run()