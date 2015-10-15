"""
Urls
"""
from django.conf.urls import url, include
from rest_framework import routers

import main.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'genre', views.GenreViewSet)
router.register(r'profile', views.BasicProfileViewSet, base_name='profile')
router.register(r'user', views.UserViewSet)
router.register(r'role', views.GroupViewSet)
router.register(r'artist', views.ArtistViewSet)
# router.register(r'venue', views.VenueViewSet)
router.register(r'show', views.ShowViewSet)
router.register(r'message', views.MessageViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'message/dismiss/(?P<pk>[0-9]+)/$', views.DismissMessageView.as_view())
]