from django.contrib import admin
from wewager.models import *

admin.site.register(Avatar)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Team)
admin.site.register(TeamData)
admin.site.register(Wager)
admin.site.register(GameOutcome)


class GameAdmin(admin.ModelAdmin):
    date_hierarchy = "date_eastern"
    list_display = ("description", "league", "date_eastern", "status", "winner")
    readonly_fields = ("date_eastern",)
    fields = (
        "description",
        "external_uid",
        "date",
        "date_eastern",
        "league",
        "data",
        "ended",
        "outcomes",
    )
    list_filter = ("league", "date")


admin.site.register(Game, GameAdmin)
