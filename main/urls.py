"""
Urls
"""
from django.conf.urls import url, include
# from rest_framework import routers

# use drf-nested-routers extension
from rest_framework_nested import routers

import main.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()

router.register(r'genre', views.GenreViewSet)
router.register(r'profile', views.BasicProfileViewSet, base_name='profile')
router.register(r'user', views.UserViewSet)
router.register(r'role', views.GroupViewSet)
router.register(r'artist', views.ArtistViewSet)
# router.register(r'venue', views.VenueViewSet)
# router.register(r'show', views.ShowViewSet)
# router.register(r'message', views.MessageViewSet)

# nested routes
nested_router = routers.NestedSimpleRouter(router, r'artist',
    lookup='artist')
nested_router.register(r'show', views.ShowViewSet,
    base_name='show')

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(nested_router.urls)),
    url(r'message/dismiss/(?P<pk>[0-9]+)/$', views.DismissMessageView.as_view())
]