"""
Urls
"""
from django.conf.urls import url, include
# from rest_framework import routers

# use drf-nested-routers extension
from rest_framework_nested import routers

import main.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'genre', views.GenreViewSet)
router.register(r'profile', views.BasicProfileViewSet, base_name='profile')
router.register(r'user', views.UserViewSet)
router.register(r'group', views.GroupViewSet)
router.register(r'artist', views.ArtistViewSet)
router.register(r'image', views.ImageViewSet, base_name='image')
# router.register(r'venue', views.VenueViewSet)
# router.register(r'show', views.ShowViewSet)
# router.register(r'message', views.MessageViewSet)

# nested routes
artist_nested_router = routers.NestedSimpleRouter(router, r'artist',
    lookup='artist')
artist_nested_router.register(r'show', views.ShowViewSet,
    base_name='show')
artist_nested_router.register(r'message', views.MessageViewSet,
    base_name='message')

artist_nested_router.register(r'connected', views.ArtistConnectionViewSet,
    base_name='connected')

profile_nested_router = routers.NestedSimpleRouter(router, r'profile',
    lookup='profile')
profile_nested_router.register(r'message', views.FanMessageViewSet,
    base_name='message')
profile_nested_router.register(r'connected', views.FanConnectionViewSet,
    base_name='connected')

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^artists-in-radius/$', views.ArtistInRadiusView),
    url(r'^', include(artist_nested_router.urls)),
    url(r'^', include(profile_nested_router.urls)),
    url(r'^login/$', views.LoginView),
    url(r'^logout/$', views.LogoutView)
]