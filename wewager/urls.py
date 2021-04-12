from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views

import wewager.views

router = DefaultRouter()
router.register(r"game", wewager.views.GameViewSet, basename="game")
router.register(r"wager", wewager.views.WagerViewSet, basename="wager")
router.register(
    r"leaderboard", wewager.views.LeaderboardViewSet, basename="leaderboard"
)
router.register(r"wallet", wewager.views.WalletViewSet, basename="wallet")

v1_urlpatterns = [
    path("api-token-auth/", auth_views.obtain_auth_token),
]

v1_urlpatterns += router.urls

web_urlpatterns = [
    path("", wewager.views.IndexView.as_view(), name="index"),
    path("games/", wewager.views.GamesView.as_view(), name="games"),
    path("wagers/", wewager.views.WagerView.as_view(), name="wagers"),
]

partial_urlpatterns = [path("balance/", wewager.views.balance_view, name="balance")]

urlpatterns = [
    path("", include(v1_urlpatterns)),
    path("web/", include(web_urlpatterns)),
    path("partial/", include(partial_urlpatterns)),
    path("accounts/", include("django.contrib.auth.urls")),
]
