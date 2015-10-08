"""
Views
"""
import logging

from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

import main.permissions as permissions
import main.serializers as serializers
import main.models as models
import main.services as services

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

class GenreViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_genres()
    serializer_class = serializers.GenreSerializer
    permission_classes = (permissions.IsFan,)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_groups()
    serializer_class = serializers.GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_users()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsFan,)


class BasicProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsFan,)
    serializer_class = serializers.BasicProfileSerializer

    def get_queryset(self):
        queryset = services.get_all_profiles()
        role = self.request.query_params.get('role', None)
        if role:
            queryset = services.get_profiles_by_role(role)
        return queryset


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_artists()
    permission_classes = (permissions.IsFan,)
    serializer_class = serializers.ArtistProfileSerializer


class VenueViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_venues()
    permission_classes = (permissions.IsFan,)
    serializer_class = serializers.VenueSerializer


class ShowViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_shows()
    permission_classes = (permissions.IsFan,)
    serializer_class = serializers.ShowSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_messages()
    permission_classes = (permissions.IsFan,)
    serializer_class = serializers.MessageSerializer


# TODO: PUT or DELETE? what url?
class DismissMessageView(generics.DestroyAPIView):
    queryset = services.get_all_messages()
    permission_classes = (permissions.IsFan,)
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        return services.get_all_messages()

    def destroy(self, request, pk=None):
        try:
            instance = self.get_queryset().get(pk=pk)
            basic_profile = services.get_profile(request.user.username)
            instance.dismissed_by.add(basic_profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise e