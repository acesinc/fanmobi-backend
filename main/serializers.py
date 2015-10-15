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

        extra_kwargs = {
            'name': {'validators': []}
        }


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

        extra_kwargs = {
            'username': {'validators': []}
        }


class BasicProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = models.BasicProfile


class BasicProfileShortSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    class Meta:
        model = models.BasicProfile
        fields = ('user', 'id', 'current_latitude', 'current_longitude')
        read_only_fields = ('id',)


class ArtistProfileSerializer(serializers.ModelSerializer):
    basic_profile = BasicProfileShortSerializer()
    connected_users = BasicProfileShortSerializer(many=True, required=False)
    genres = GenreSerializer(required=False, many=True)

    class Meta:
        model = models.ArtistProfile


    def validate(self, data):
        logger.debug('inside of ArtistProfileSerializer.validate. data: %s' % data)

        # get profile info
        data['current_latitude'] = data['basic_profile'].get('current_latitude', '0')
        data['current_longitude'] = data['basic_profile'].get('current_longitude', '0')

        # it's an error not to provide a username here
        username = data['basic_profile']['user'].get('username', None)
        basic_profile = models.BasicProfile.objects.filter(
            user__username=username).first()
        if not basic_profile:
            kwargs = {'email': data['basic_profile']['user'].get('email', None),
                'groups': ['ARTIST']}
            p = models.BasicProfile.create_user(username, **kwargs)
            data['basic_profile'] = p
        else:
            data['basic_profile'] = basic_profile

        # if method is a PATCH, we don't want to arbitrarily set fields to None
        # if they were left out of the request data, since a PATCH request
        # need only update one or more fields. If the user didn't specify the
        # field, it shouldn't be updated
        if self.context['request'].method == 'PATCH':
            # TODO: support PATCH
            pass
        else:
            data['name'] = data.get('name', None)
            data['hometown'] = data.get('hometown', None)
            data['bio'] = data.get('bio', None)
            data['website'] = data.get('website', None)
            data['facebook_id'] = data.get('facebook_id', None)
            data['twitter_id'] = data.get('twitter_id', None)
            data['youtube_id'] = data.get('youtube_id', None)
            data['soundcloud_id'] = data.get('soundcloud_id', None)
            data['itunes_url'] = data.get('itunes_url', None)
            data['ticket_url'] = data.get('ticket_url', None)
            data['merch_url'] = data.get('merch_url', None)
            data['paypal_email'] = data.get('paypal_email', None)

            # next_show set automatically (get next show in models.Show for
            # this artist)

            if 'genres' in data:
                genres = []
                for i in data['genres']:
                    g = models.Genre.objects.get(name=i['name'])
                    genres.append(g)
                data['genres'] = genres
            else:
                data['genres'] = []

            if 'connected_users' in data:
                users = []
                for i in data['connected_users']:
                    u = models.BasicProfile.objects.get(user__username=i['user']['username'])
                    users.append(u)
                data['connected_users'] = users
            else:
                data['connected_users'] = []

        return data

    def create(self, validated_data):
        logger.debug('inside of ArtistProfileSerializer.create')
        profile = validated_data['basic_profile']
        a = models.ArtistProfile(
            basic_profile=profile,
            name=validated_data['name'],
            hometown=validated_data['hometown'],
            bio=validated_data['bio'],
            website=validated_data['website'],
            facebook_id=validated_data['facebook_id'],
            twitter_id=validated_data['twitter_id'],
            youtube_id=validated_data['youtube_id'],
            soundcloud_id=validated_data['soundcloud_id'],
            itunes_url=validated_data['itunes_url'],
            ticket_url=validated_data['ticket_url'],
            merch_url=validated_data['merch_url'],
            paypal_email=validated_data['paypal_email'])

        a.save()
        for i in validated_data['genres']:
            a.genres.add(i)

        # support updates to the underlying BasicProfile object
        profile.current_latitude = validated_data['current_latitude']
        profile.current_longitude = validated_data['current_longitude']
        profile.save()

        return a

    def update(self, instance, validated_data):
        if self.context['request'].method == 'PATCH':
            # TODO: handle PATCHING (partial updates)
            pass
        else:
            # if it's not a partial update, we know every field will be present
            # in validated_data (even if it's None)
            instance.hometown = validated_data['hometown']
            instance.name = validated_data['name']
            instance.bio = validated_data['bio']
            instance.website = validated_data['website']
            instance.facebook_id = validated_data['facebook_id']
            instance.twitter_id = validated_data['twitter_id']
            instance.youtube_id = validated_data['youtube_id']
            instance.soundcloud_id = validated_data['soundcloud_id']
            instance.itunes_url = validated_data['itunes_url']
            instance.merch_url = validated_data['merch_url']
            instance.paypal_email = validated_data['paypal_email']

            instance.genres.clear()
            for i in validated_data['genres']:
                instance.genres.add(i)
            instance.save()

            instance.connected_users.clear()
            for i in validated_data['connected_users']:
                instance.connected_users.add(i)
            instance.save()

            # support updates to the underlying BasicProfile object
            profile = instance.basic_profile
            # support updates to the underlying BasicProfile object
            profile.current_latitude = validated_data['current_latitude']
            profile.current_longitude = validated_data['current_longitude']
            profile.save()

            return instance


class ArtistProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArtistProfile
        fields = ('name', 'id')


# class VenueSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Venue


# class VenueShortSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Venue
#         fields = ('name', 'id')


class ShowSerializer(serializers.ModelSerializer):
    # artist = ArtistProfileShortSerializer()
    # venue = VenueShortSerializer()
    class Meta:
        model = models.Show


class MessageSerializer(serializers.ModelSerializer):
    artist = ArtistProfileShortSerializer()
    class Meta:
        model = models.Message