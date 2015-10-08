"""
Serializers
"""
import logging

import django.contrib.auth

from rest_framework import serializers

import main.models as models

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = django.contrib.auth.models.Group
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User
        fields = ('username', 'email', 'groups')


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User
        fields = ('username', 'email')


class BasicProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = models.BasicProfile


class BasicProfileShortSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    class Meta:
        model = models.BasicProfile
        fields = ('user', 'id')


class ArtistProfileSerializer(serializers.ModelSerializer):
    basic_profile = BasicProfileSerializer()
    connected_users = BasicProfileSerializer(many=True)
    class Meta:
        model = models.ArtistProfile


class ArtistProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArtistProfile
        fields = ('name', 'id')


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Venue


class VenueShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Venue
        fields = ('name', 'id')


class ShowSerializer(serializers.ModelSerializer):
    artist = ArtistProfileShortSerializer()
    venue = VenueShortSerializer()
    class Meta:
        model = models.Show


class MessageSerializer(serializers.ModelSerializer):
    artist = ArtistProfileShortSerializer()
    class Meta:
        model = models.Message