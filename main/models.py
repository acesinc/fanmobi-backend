"""
model definitions for fanmobi

"""
import logging
import os
import uuid

import django.contrib.auth
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings

from PIL import Image

import main.constants as constants

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

# TODO:
# - upload avatar (and thumb) - image storage and serving

class Genre(models.Model):
    """
    Music genres
    """
    name = models.CharField(max_length=128, unique=True)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class ArtistProfile(models.Model):
    basic_profile = models.ForeignKey('BasicProfile', related_name='artists')
    name = models.CharField(max_length=256)
    hometown = models.CharField(max_length=256, blank=True, null=True)
    bio = models.CharField(max_length=8192, blank=True, null=True)
    avatar_url_thumb = models.URLField(max_length=2048, blank=True, null=True)
    avatar_url = models.URLField(max_length=2048, blank=True, null=True)
    website = models.URLField(max_length=2048, blank=True, null=True)
    facebook_id = models.CharField(max_length=256, blank=True, null=True)
    facebook_page_id = models.CharField(max_length=256, blank=True, null=True)
    twitter_id = models.CharField(max_length=256, blank=True, null=True)
    youtube_id = models.CharField(max_length=256, blank=True, null=True)
    soundcloud_id = models.CharField(max_length=256, blank=True, null=True)
    itunes_url = models.URLField(max_length=2048, blank=True, null=True)
    ticket_url = models.URLField(max_length=2048, blank=True, null=True)
    merch_url = models.URLField(max_length=2048, blank=True, null=True)
    kickstarter_url = models.URLField(max_length=2048, blank=True, null=True)
    google_play_url = models.URLField(max_length=2048, blank=True, null=True)
    instagram_id = models.CharField(max_length=256, blank=True, null=True)
    vimeo_url = models.URLField(max_length=2048, blank=True, null=True)
    paypal_email = models.EmailField(null=True)
    next_show = models.ForeignKey('Show', related_name='artists', null=True)
    genres = models.ManyToManyField(
        Genre,
        related_name='artists',
        db_table='artist_genre')
        # artist->user connections
    connected_users = models.ManyToManyField(
        'BasicProfile',
        related_name='connected_artists',
        db_table='artist_user'
    )
    # thank you message
    # thank you attachment


class BasicProfile(models.Model):
    """
    Basic info for a user (fan)

    An Artist also has a basic profile

    Note that some information (username, email, last_login, date_joined) is
    held in the associated Django User model. In addition, the user's role
    (USER, ARTIST, or ADMIN) is represented by the Group
    associated with the Django User model

    Notes on use of contrib.auth.models.User model:
        * first_name and last_name are not used
        * is_superuser is always set to False
        * is_staff is set to True for Admins
        * password: TBD
    """
    # instead of overriding the builtin Django User model used
    # for authentication, we extend it
    # https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#extending-the-existing-user-model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True,
        blank=True)

    current_latitude = models.CharField(max_length=16, blank=True, null=True)
    current_longitude = models.CharField(max_length=16, blank=True, null=True)
    avatar = models.ForeignKey('Image', related_name='basic_profile',
        null=True, blank=True)

    def __repr__(self):
        return 'Profile: %s' % self.user.username

    def __str__(self):
        return self.user.username

    @staticmethod
    def create_groups():
        """
        Groups are used as Roles, and as such are relatively static, hence
        their declaration here (NOTE that this must be invoked manually
        after the server has started)
        """
        # create the different Groups (Roles) of users
        group = django.contrib.auth.models.Group.objects.create(
            name='FAN')
        group = django.contrib.auth.models.Group.objects.create(
            name='ARTIST')
        group = django.contrib.auth.models.Group.objects.create(
            name='ADMIN')

    def highest_role(self):
        """
        ADMIN > ARTIST > FAN
        """
        groups = self.user.groups.all()
        group_names = [i.name for i in groups]

        if 'ADMIN' in group_names:
            return 'ADMIN'
        elif 'ARTIST' in group_names:
            return 'ARTIST'
        elif 'FAN' in group_names:
            return 'FAN'
        else:
            # TODO: raise exception?
            logger.error('User %s has invalid Group' % self.user.username)
            return ''

    @staticmethod
    def create_user(username, **kwargs):
        """
        Create a new User and Fan object

        kwargs:
            password
            groups (['group1_name', 'group2_name'])

        """
        # TODO: what to make default password?
        password = kwargs.get('password', 'password')

        email = kwargs.get('email', '')

        # create User object
        # if this user is an ORG_STEWARD or APPS_MALL_STEWARD, give them
        # access to the admin site
        groups = kwargs.get('groups', ['FAN'])
        if 'ADMIN' in groups:
            user = django.contrib.auth.models.User.objects.create_superuser(
                username=username, email=email, password=password)
            user.save()
            # logger.warn('creating superuser: %s, password: %s' % (username, password))
        else:
            user = django.contrib.auth.models.User.objects.create_user(
                username=username, email=email, password=password)
            user.save()
            # logger.info('creating user: %s' % username)

        # add user to group(s) (i.e. Roles - FAN, ARTIST, ADMIN). If no
        # specific Group is provided, we will default to FAN
        for i in groups:
            g = django.contrib.auth.models.Group.objects.get(name=i)
            user.groups.add(g)

        # get additional profile information (so far none)

        # create the fan object and associate it with the User
        f = BasicProfile(user=user)
        f.save()

        # if 'ARTIST' in groups:
        #     # if the name is blank, just use their username (facebook id) for now
        #     a = ArtistProfile(basic_profile=f, name=kwargs.get('name', username))
        #     a.save()

        return f

class Message(models.Model):
    """
    A message (created by an artist for their users)
    """
    text = models.CharField(max_length=8192)
    created_at = models.DateTimeField(auto_now=True)
    attachment = models.URLField(max_length=2048, blank=True, null=True)
    artist = models.ForeignKey(ArtistProfile, related_name='messages')
    dismissed_by = models.ManyToManyField(
        'BasicProfile',
        related_name='dismissed_messages',
        db_table='message_basic_profile'
    )

    def __repr__(self):
        return '%s:%s' % (self.artist.name, self.created_at)

    def __str__(self):
        return '%s:%s' % (self.artist.name, self.created_at)

# TODO: Ultimately, Venue should probably be a separate model with a unique name
# For now (since we don't know who would manage those entries), just
# denormalize

# class Venue(models.Model):
#     """
#     A venue

#     # TODO:
#         * address
#         * phone
#         * email
#         * twitter, facebook, website
#     """
#     name = models.CharField(max_length=1024, unique=True)
#     description = models.CharField(max_length=8192, blank=True, null=True)
#     latitude = models.DecimalField(max_digits=8, decimal_places=3)
#     longitude = models.DecimalField(max_digits=8, decimal_places=3)

#     def __repr__(self):
#         return self.name

#     def __str__(self):
#         return self.name

class Show(models.Model):
    """
    A Show

    TODO: Should probably have a foreign key to a models.Venue, but for now
    keep it simple
    """
    start = models.DateTimeField()
    end = models.DateTimeField()
    artist = models.ForeignKey(ArtistProfile, related_name='shows')
    # venue = models.ForeignKey(Venue, related_name='shows')
    latitude = models.CharField(max_length=16, null=True, blank=True)
    longitude = models.CharField(max_length=16, null=True, blank=True)
    venue_name = models.CharField(max_length=1024, blank=True, null=True)

    def __repr__(self):
        return '%s:%s:%s' % (self.artist.name, self.venue.name, self.start)

    def __str__(self):
        return '%s:%s:%s' % (self.artist.name, self.venue.name, self.start)

class Image(models.Model):
    """
    Image

    (Uploaded) images are stored in a flat directory on the server using a
    filename like <id>_<image_type>.png

    When creating a new image, use the Image.create_image method, do not
    use the Image.save() directly
    """
    # don't need this now, but could be useful later
    uuid = models.CharField(max_length=36, unique=True)
    file_extension = models.CharField(max_length=16, default='png')
    image_type = models.CharField(max_length=64)

    def __repr__(self):
        return str(self.id)

    def __str__(self):
        return str(self.id)

    @staticmethod
    def create_image(pil_img, **kwargs):
        """
        Given an image (PIL format) and some metadata, write to file sys and
        create DB entry

        pil_img: PIL.Image (see https://pillow.readthedocs.org/en/latest/reference/Image.html)
        """
        # get DB info for image
        random_uuid = str(uuid.uuid4())
        file_extension = kwargs.get('file_extension', 'png')
        valid_extensions = constants.VALID_IMAGE_EXTENSIONS
        if file_extension not in valid_extensions:
            logger.error('Invalid file extension for image: %s' % file_extension)
            raise Exception('Invalid file extension for image')

        image_type = kwargs.get('image_type', None)
        if image_type not in constants.VALID_IMAGE_TYPES:
            logger.error('No image_type (or invaid image_type) provided')
            raise Exception('No image_type (or invaid image_type) provided')

        # create database entry
        img = Image(uuid=random_uuid, file_extension=file_extension,
            image_type=image_type)
        img.save()

        # write the image to the file system
        file_name = settings.MEDIA_ROOT + str(img.id) + '_' + image_type + '.' + file_extension
        # logger.debug('saving image %s' % file_name)
        pil_img.save(file_name)

        # check size requirements
        size_bytes = os.path.getsize(file_name)
        logger.debug('Uploaded image size of %s bytes' % size_bytes)
        # if size_bytes > image_type.max_size_bytes:
        #     logger.error('Image size is %d bytes, which is larger than the max \
        #         allowed %d bytes' % (size_bytes, image_type.max_size_bytes))
        #     # TODO raise exception and remove file
        #     return

        # TODO: check width and height

        return img



