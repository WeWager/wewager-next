from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views

from . import views

router = DefaultRouter()
router.register(r"user", views.UserViewSet, basename="user")
router.register(r"game", views.GameViewSet, basename="game")
router.register(r"wager", views.WagerViewSet, basename="wager")

v1_urlpatterns = [
    path("wallet/", views.WalletViewSet.as_view(), name="wallet"),
    path("api-token-auth/", auth_views.obtain_auth_token),
]

v1_urlpatterns += router.urls

urlpatterns = [path("api/v1/", include(v1_urlpatterns))]
