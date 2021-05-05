from django.urls import path, include
from rest_framework.routers import DefaultRouter

import social.views

router = DefaultRouter()
router.register(r"post", social.views.PostViewSet, basename="post")
router.register(r"feed", social.views.FeedViewSet, basename="feed")
router.register(r"user", social.views.UserViewSet, basename="user")
router.register(r"follow", social.views.FollowViewSet, basename="follow")

urlpatterns = router.urls
