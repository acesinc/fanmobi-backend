"""
Access the ORM primarily through this
"""
import logging

import django.contrib.auth

import main.models as models

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

def get_profile(username):
    """
    get a user's Profile
    """
    try:
        profile = models.BasicProfile.objects.get(user__username=username)
        return profile
    except models.BasicProfile.DoesNotExist:
        return None

def is_admin(username):
    try:
        profile = get_profile(username)
        groups = profile.user.groups.values_list('name', flat=True)
        if 'ADMIN' in groups:
            return True
        return False
    except Exception:
        return False

def get_all_genres():
    return models.Genre.objects.all()

def get_all_users():
    return django.contrib.auth.models.User.objects.all()

def get_artist_by_id(id):
    try:
        return models.ArtistProfile.objects.get(id=id)
    except models.ArtistProfile.DoesNotExist:
        return None

def get_all_groups():
    return django.contrib.auth.models.Group.objects.all()

def get_all_profiles():
    return models.BasicProfile.objects.all()

def get_profiles_by_role(role):
    return models.BasicProfile.objects.filter(
        user__groups__name__exact=role)

def get_all_artists():
    return models.ArtistProfile.objects.all()

# def get_all_venues():
#     return models.Venue.objects.all()

def get_all_shows():
    return models.Show.objects.all()

def get_all_messages():
    return models.Message.objects.all()

def get_all_unread_messages(username):
    profile = get_profile(username)
    # get all artists connected to this user
    artists = models.ArtistProfile.objects.filter(connected_users__in=[profile.id])
    # get all messages from these artists
    artist_ids = [a.id for a in artists]
    messages = models.Message.objects.filter(artist__id__in=artist_ids)
    # and remvove the messages that have been dismissed
    dismissed_messages = messages.filter(dismissed_by__in=[profile.id])
    unread_messages = [i for i in messages if i not in dismissed_messages]
    return unread_messages

def mark_message_as_read(username, message):
    profile = get_profile(username)
    message.dismissed_by.add(profile)
    return


def delete_show(username, show):
    profile = get_profile(username)
    if username != show.artist.basic_profile.user.username and profile.highest_role() not in ['ADMIN']:
        raise errors.PermissionDenied('Cannot delete a show for another artist')
    show.delete()

def delete_message(username, message):
    profile = get_profile(username)
    if username != message.artist.basic_profile.user.username and profile.highest_role() not in ['ADMIN']:
        raise errors.PermissionDenied('Cannot delete a message for another artist')
    message.delete()
