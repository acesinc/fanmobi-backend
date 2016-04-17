"""
Views
"""
import logging
import math

import requests

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework import generics
from rest_framework import permissions as rf_permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework import mixins as mixins
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

import main.constants as constants
import main.permissions as permissions
import main.serializers as serializers
import main.models as models
import main.services as services
import main.errors as errors
import main.utils as utils

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

class ListModelViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass

class ListDestroyModelViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass

class ListUpdateDestroyModelViewSet(mixins.ListModelMixin,
    mixins.DestroyModelMixin, mixins.UpdateModelMixin,
    viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass

class GenreViewSet(viewsets.ModelViewSet):
    """
    Names of music genres
    """
    queryset = services.get_all_genres()
    serializer_class = serializers.GenreSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)


class GroupViewSet(viewsets.ModelViewSet):
    """
    A Group is a Role, like a Fan or an Artist

    A user can belong to one or more groups. Currently, we are using three
    groups: FAN, ARTIST, and ADMIN. These should be very static - don't
    worry about changing anything here

    Accessible only via ADMINs
    """
    queryset = services.get_all_groups()
    serializer_class = serializers.GroupSerializer
    permission_classes = (permissions.IsAdmin,)


class UserViewSet(viewsets.ModelViewSet):
    """
    User is a built-in Django thing - don't use this directly

    Accessible only via ADMINs
    """
    queryset = services.get_all_users()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAdmin,)


class BasicProfileViewSet(viewsets.ModelViewSet):
    """
    Every Fanmobi user has an associated Profile

    At a minimum, a Profile has an associated user with a username and belongs
    to at least one Group (FAN by default)

    `current_latitude` and `current_longitude` are in Decimal Degrees

    Example request data that includes an avatar (this won't work from Swagger):
    `{"current_latitude": "5.4", "current_longitude": "-4.3", "avatar": {"id": 1}}`
    """
    # permission_classes = (permissions.IsFan,)
    serializer_class = serializers.BasicProfileSerializer
    permission_classes = (permissions.ProfilePermissions,)

    def get_queryset(self):
        role = self.request.query_params.get('role', None)
        if role:
            queryset = services.get_profiles_by_role(role)
        else:
            queryset = services.get_all_profiles()
        return queryset

    def create(self, request):
        if not services.is_admin(request.user.username):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        try:
            logger.debug('inside BasicProfileViewSet.create: data: %s' % request.data)
            serializer = serializers.BasicProfileSerializer(data=request.data,
                context={'request': request}, partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response('Error', status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        Get all Profiles (ADMIN only)
        """
        if not services.is_admin(request.user.username):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        return super(BasicProfileViewSet, self).list(self, request)


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_artists()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ArtistProfileSerializer

    def create(self, request):
        """
        Create a new artist

        Given an existing username, make that user an Artist

        Example data: {{"basic_profile": { "user": {"username": "someguy"}}, "name": "someGuysBand"}}
        """
        try:
            logger.debug('inside ArtistViewSet.create, data: %s' % request.data)
            serializer = serializers.ArtistProfileSerializer(data=request.data,
                context={'request': request}, partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response('Error', status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an artist

        ** Does not currently work via Swagger**
        Example request data: `{"basic_profile": {"current_latitude": "53.4", "current_longitude": "-4.3"}, "name": "Great Artist Name", "genres": [{"name": "Blues"}, {"name": "Rock"}]}`
        """
        try:
            logger.debug('inside ArtistViewSet.update, data: %s' % request.data)
            instance = self.get_queryset().get(pk=pk)
            serializer = serializers.ArtistProfileSerializer(instance,
                data=request.data, context={'request': request}, partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except models.ArtistProfile.DoesNotExist:
            return Response('Artist does not exist', status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response('Error', status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        Get all artists
        """
        return super(ArtistViewSet, self).list(self, request)


# class VenueViewSet(viewsets.ModelViewSet):
#     queryset = services.get_all_venues()
#     permission_classes = (permissions.IsFan,)
#     serializer_class = serializers.VenueSerializer


class ShowViewSet(viewsets.ModelViewSet):
    """
    Shows for artists

    Times are in format: `2015-09-19T00:00:00Z` (YYYY-MM-DDTHH:MM:SSZ)
    """
    permission_classes = (permissions.IsArtistOrReadOnly,)
    serializer_class = serializers.ShowSerializer

    def get_queryset(self):
        return services.get_all_shows()

    def list(self, request, artist_pk=None):
        """
        List all shows for an artist
        """
        if not services.get_artist_by_id(artist_pk):
            return Response('Artist not found', status=status.HTTP_404_NOT_FOUND)
        queryset = self.get_queryset().filter(artist__id=artist_pk)
        # because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ShowSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ShowSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, artist_pk=None):
        """
        Get a show for an artist
        """
        queryset = self.get_queryset().get(pk=pk, artist__id=artist_pk)
        serializer = serializers.ShowSerializer(queryset,
            context={'request': request})
        return Response(serializer.data)

    def create(self, request, artist_pk=None):
        """
        Create a new show for an artist
        """
        if not services.can_access(request.user.username, artist_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        try:
            serializer = serializers.ShowSerializer(data=request.data,
                context={'request': request, 'artist_pk': artist_pk})
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
          raise e

    def update(self, request, pk=None, artist_pk=None):
        """
        Update an existing show for an artist
        """
        if not services.can_access(request.user.username, artist_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        try:
            instance = self.get_queryset().get(pk=pk, artist__id=artist_pk)
            serializer = serializers.ShowSerializer(instance, data=request.data,
                context={'request': request, 'artist_pk': artist_pk})
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
          raise e

    def destroy(self, request, pk=None, artist_pk=None):
        """
        Delete a show for an artist
        """
        if not services.can_access(request.user.username, artist_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset()
        show = get_object_or_404(queryset, pk=pk)
        try:
            services.delete_show(request.user.username, show)
        except errors.PermissionDenied:
            return Response('Cannot update another artist\'s show',
                status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsArtistOrReadOnly,)
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        return services.get_all_messages()

    def list(self, request, artist_pk=None):
        """
        List all messages from an artist
        """
        if not services.can_access(request.user.username, artist_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset().filter(artist__id=artist_pk)
        # because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.MessageSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.MessageSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, artist_pk=None):
        """
        Get a message from an artist
        """
        try:
            queryset = self.get_queryset().get(pk=pk, artist__id=artist_pk)
            serializer = serializers.MessageSerializer(queryset,
                context={'request': request})
            return Response(serializer.data)
        except models.Message.DoesNotExist:
            return Response('Message not found',
                    status=status.HTTP_404_NOT_FOUND)

    def create(self, request, artist_pk=None):
        """
        Create a new message for an artist
        """
        if not services.can_access(request.user.username, artist_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        try:
            serializer = serializers.MessageSerializer(data=request.data,
                context={'request': request, 'artist_pk': artist_pk})
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
          raise e

    def destroy(self, request, pk=None, artist_pk=None):
        """
        Delete a message from an artist
        """
        if not services.can_access(request.user.username, artist_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset()
        message = get_object_or_404(queryset, pk=pk)
        try:
            services.delete_message(request.user.username, message)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FanMessageViewSet(ListDestroyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        username = self.request.user.username
        if services.is_admin(username):
            return services.get_all_messages()
        else:
            return services.get_all_unread_messages(username)

    def list(self, request, profile_pk=None):
        """
        Get all unread messages for a user
        """
        if not services.can_access(request.user.username, profile_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)

        requested_user = models.BasicProfile.objects.get(id=profile_pk)
        queryset = services.get_all_unread_messages(requested_user.user.username)
        # because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.MessageSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.MessageSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None, profile_pk=None):
        """
        Mark a message as read for a user
        """
        queryset = self.get_queryset()
        basic_profile = models.BasicProfile.objects.get(id=profile_pk)
        message = get_object_or_404(queryset, pk=pk)
        try:
            services.mark_message_as_read(basic_profile.user.username, message)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ArtistConnectionViewSet(ListModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.BasicProfileShortSerializer

    def list(self, request, artist_pk=None):
        """
        Get all users connected to an artist
        """
        if not services.can_access(request.user.username, artist_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        artist = models.ArtistProfile.objects.get(id=artist_pk)
        queryset = models.ArtistProfile.objects.get(id=artist_pk).connected_users
        # because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.BasicProfileShortSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.BasicProfileShortSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

class FanConnectionViewSet(ListUpdateDestroyModelViewSet):
    """
    Artist connections
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ArtistProfileShortSerializer

    def list(self, request, profile_pk=None):
        """
        Get all artists followed by a user
        """
        if not services.can_access(request.user.username, profile_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        queryset = models.ArtistProfile.objects.filter(connected_users__in=[profile_pk])
        # because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ArtistProfileShortSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ArtistProfileShortSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None, profile_pk=None):
        """
        Unfollow an artist
        """
        if not services.can_access(request.user.username, profile_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        try:
            artist = models.ArtistProfile.objects.get(id=pk)
            updated_connected_users = []
            found = False
            for i in artist.connected_users.all():
                if str(i.id) != str(profile_pk):
                    updated_connected_users.append(i)
                else:
                    found = True
            artist.connected_users.clear()
            artist.connected_users = updated_connected_users
            if found:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response('Unable to complete the request',
                status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, profile_pk=None):
        """
        Follow an artist
        ---
        omit_parameters:
            - body
        """
        if not services.can_access(request.user.username, profile_pk):
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        try:
            artist = models.ArtistProfile.objects.get(id=pk)
            basic_profile = models.BasicProfile.objects.get(id=profile_pk)
            artist.connected_users.add(basic_profile)
            return Response('Followed artist', status=status.HTTP_200_OK)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response('Unable to complete the request',
                status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((rf_permissions.AllowAny,))
def LoginView(request):
    """
    User login via Facebook or an 'anonymous' id

    If both are provided, the `fb_access_token` takes precedence.
    `anonymous_id` must
    be an alphanumeric string of 30 characters or less

    If a user with the corresponding `anonymous_id` or `fb_access_token` is
    not found, it will be created
    ---
    omit_serializer: true
    parameters_strategy:
        form: replace
    parameters:
        - name: fb_access_token
          type: string
        - name: anonymous_id
          type: string
    type:
      username:
        required: true
        type: string
      name:
        required: true
        type: string
      fb_access_token:
        required: false
        type: string
      msg:
        required: false
        type: string
    """
    if 'username' in request.session:
        # already logged in
        username = request.session['username']
        user_profile = services.get_profile(username)
        r_data = {'username': username,
            'msg': 'already logged in as user: %s' % username,
            'id': user_profile.id,
            'artist_id': services.get_artist_id_by_username(username)}
        return Response(r_data,
            status=status.HTTP_200_OK)
    user_profile = None
    username = None
    friendly_name = None
    fb_access_token = request.data.get('fb_access_token', None)
    anonymous_id = request.data.get('anonymous_id', None)
    if fb_access_token:
        logger.debug('attempting to hit facebook with access_token: %s' % fb_access_token)
        fb_url = '%s/?access_token=%s' % (constants.FACEBOOK_ME_ENDPOINT, fb_access_token)
        logger.debug('attempting to hit Facebook url: %s' % fb_url)
        r = requests.get(fb_url)
        if r.status_code == 400:
            logger.error('Bad request to facebook: %s' % r.text)
            return Response('Bad request to Facebook: %s' % r.text, status=status.HTTP_400_BAD_REQUEST)
        if r.status_code != 200:
            logger.error('Error hitting facebook API, got status: %s' % r.status_code)
            return Response('Problem connecting to facebook: %s' % r.text, status=status.HTTP_400_BAD_REQUEST)
        resp = r.json()
        username = resp['id']
        friendly_name = resp['name']
        logger.debug('Got facebook user with id %s and name %s' % (username, friendly_name))
    elif anonymous_id:
        logger.debug('logging user in with anonymous_id: %s' % anonymous_id)
        username = anonymous_id
        friendly_name = username
    else:
        return Response('Error: no facebook or anonymous id provided',
            status=HTTP_400_BAD_REQUEST)

    user_profile = services.get_profile(username)
    if not user_profile:
        # if user doesn't exist, create them
        kwargs = {}
        kwargs['groups'] = ['FAN']

        kwargs['name'] = friendly_name
        p = models.BasicProfile.create_user(username, **kwargs)
        user_profile = p
        logger.info('created user %s' % (user_profile.user.username))
    request.session['username'] = user_profile.user.username
    artist_id = services.get_artist_id_by_username(username)
    r_data = {'username': username, 'name': friendly_name, 'artist_id': artist_id,
        'facebook_authenticated': bool(fb_access_token), 'profile_id': user_profile.id}
    if fb_access_token:
        request.session['fb_access_token'] = fb_access_token

    return Response(r_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((rf_permissions.AllowAny,))
def LogoutView(request):
    """
    Logout user

    Provides the `username` of the user that was logged out. Value will be
    null if no user was logged in
    ---
    omit_serializer: true
    type:
      username:
        required: true
        type: string
    """
    if 'username' not in request.session:
        username = None
    else:
        username = request.session['username']
    request.session.flush()
    r_data = {'username': username}
    return Response(r_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def ArtistInRadiusView(request):
    """
    Get artists within a radius (km) of given coordinates (in decimal degrees )
    ---
    omit_serializer: true
    parameters_strategy:
        form: replace
    parameters:
        - name: radius
          paramType: query
        - name: latitude
          paramType: query
        - name: longitude
          paramType: query
    """
    try:
        radius = request.query_params.get('radius')
        user_lat = request.query_params.get('latitude')
        user_lon = request.query_params.get('longitude')
    except Exception as e:
        return Response('Bad request: %s' % str(e), status=status.HTTP_400_BAD_REQUEST)
    logger.debug('looking for artists in a %s km radius of lat: %s, long: %s' % (radius, user_lat, user_lon))
    # In general, x and y must satisfy (x - center_x)^2 + (y - center_y)^2 < radius^2
    artists = services.get_all_artists()
    artists_in_radius = []
    for a in artists:
        if not a.basic_profile.current_latitude or not a.basic_profile.current_longitude:
            continue
        artist_lat = a.basic_profile.current_latitude
        artist_lon = a.basic_profile.current_longitude
        logger.debug('checking if artist %s is within range' % a.basic_profile.user.username)
        logger.debug('artist lat: %s, artist lon: %s' % (artist_lat, artist_lon))
        logger.debug('user lat: %s, user lon: %s' % (user_lat, user_lon))
        if utils.is_inside_radius(user_lat, user_lon, artist_lat, artist_lon, radius):
            artists_in_radius.append(a)
    serializer = serializers.ArtistProfileSerializer(artists_in_radius, many=True,
        context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


class ImageViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return services.get_all_images()

    serializer_class = serializers.ImageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, JSONParser)

    def create(self, request):
        """
        Upload an image (** Does not work from Swagger**)

        Use content_type = `application/form-data`

        Data:

        * `image_type` = `avatar`|`icon`
        * `file_extension` = `jpg`|`png`
        * `image` = `<FILE>`
        """
        try:
            serializer = serializers.ImageCreateSerializer(data=request.data,
                context={'request': request})
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            raise e

    def list(self, request):
        queryset = self.get_queryset()
        serializer = serializers.ImageSerializer(queryset,
            many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Return an image, enforcing access control
        """
        pk = int(pk)
        queryset = self.get_queryset()
        image = get_object_or_404(queryset, pk=pk)
        image_path = services.get_image_path(pk, image.image_type)
        logger.debug('looking for image %s' % image_path)
        # enforce access control
        user = services.get_profile(self.request.user.username)
        content_type = 'image/' + image.file_extension
        try:
            with open(image_path, 'rb') as f:
                return HttpResponse(f.read(), content_type=content_type)
        except IOError:
            logger.error('No image found for pk %d' % pk)
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        image = get_object_or_404(queryset, pk=pk)
        # TODO: remove image from file system
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

