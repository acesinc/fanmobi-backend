"""
Access the ORM primarily through this
"""
import logging

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