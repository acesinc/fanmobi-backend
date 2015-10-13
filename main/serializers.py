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


class ArtistProfileSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    name = serializers.CharField(max_length=128)
    email = serializers.EmailField(required=False)
    hometown = serializers.CharField(max_length=128, required=False)
    connected_users = serializers.ListField(child=serializers.CharField(
        max_length=30), read_only=True)
    genres = serializers.ListField(child=serializers.CharField(
        max_length=50))


    def validate(self, data):
        logger.debug('inside of ArtistProfileSerializer.validate. data: %s' % data)
        username = data.get('username', None)
        basic_profile = models.BasicProfile.objects.filter(user__username=username).first()
        name = data.get('name', None)
        data['hometown'] = data.get('hometown', None)
        if not basic_profile:
            kwargs = {'email': data.get('email', None),
                'groups': ['ARTIST']}
            p = models.BasicProfile.create_user(username, **kwargs)
            data['basic_profile'] = p
        else:
            data['basic_profile'] = basic_profile

        if 'genres' in data:
            data['genres'] = models.Genre.objects.filter(name__in=data['genres'])

        return data

    def create(self, validated_data):
        logger.debug('inside of ArtistProfileSerializer.create')
        a = models.ArtistProfile(basic_profile=validated_data['basic_profile'],
            name=validated_data['name'], hometown=validated_data['hometown'])
        a.save()
        for i in validated_data['genres']:
            a.genres.add(i)

        return a

    def to_representation(self, obj):
        connected_users = []
        for i in obj.connected_users.all():
            connected_users.append(i.user.username)
        return {
            'username': obj.basic_profile.user.username,
            'hometown': obj.hometown,
            'connected_users': connected_users,
            'name': obj.name
        }


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