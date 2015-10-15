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

def get_all_genres():
    return models.Genre.objects.all()

def get_all_users():
    return django.contrib.auth.models.User.objects.all()

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