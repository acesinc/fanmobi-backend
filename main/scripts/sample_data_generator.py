"""
Creates test data

************************************WARNING************************************
Many of the unit tests depend on data set in this script. Always
run the unit tests (python manage.py test) after making any changes to this
data!!
************************************WARNING************************************
"""
import datetime
import os
import pytz
import sys

from PIL import Image

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

import pytz

import django.contrib.auth

from main import models as models
from main import services

TEST_IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images') + '/'

def run():
    """
    Creates basic sample data
    """
    # TODO: Check to see if DB is empty - if not, don't run!
    # Create Groups
    models.BasicProfile.create_groups()

    ############################################################################
    #                               Genres
    ############################################################################
    alternative = models.Genre(name='Alternative')
    alternative.save()

    blues = models.Genre(name='Blues')
    blues.save()

    rock = models.Genre(name='Rock')
    rock.save()

    country = models.Genre(name='Country')
    country.save()

    hip_hop = models.Genre(name='Hip-Hop')
    hip_hop.save()

    ############################################################################
    #                               Venues
    # TODO: add this back later (if we end up supporting Venues as their own
    #        objects)
    ############################################################################
    # nine_thirty_club = models.Venue(name='9:30 Club',
    #     description='State-of-the-art concert space presents top-name rock, punk, hip-hop and country acts nightly',
    #     latitude=38.918229, longitude=-77.023795)
    # nine_thirty_club.save()

    # rams_head_live_bmore = models.Venue(name='Rams Head Live',
    #     description='Rams Head Live! is an indoor music venue, club, and bar located in Baltimore, Maryland',
    #     latitude=39.290128, longitude=-76.607246)
    # rams_head_live_bmore.save()

    ############################################################################
    #                               Artists
    ############################################################################
    kwargs = {'email': 'counting_crows@gmail.com', 'groups': ['ARTIST']}
    counting_crows_basic = models.BasicProfile.create_user(
        'counting_crows', **kwargs)
    counting_crows_artist = models.ArtistProfile(basic_profile=counting_crows_basic,
        name='Counting Crows')
    counting_crows_artist.save()
    counting_crows_artist.genres.add(alternative)

    ############################################################################
    #                               Shows
    ############################################################################
    start = pytz.timezone('America/New_York').localize(
        datetime.datetime(2015, 9, 18, hour=20, minute=0))
    end = start + datetime.timedelta(hours=3)
    counting_crows_show_1 = models.Show(start=start, end=end,
        artist=counting_crows_artist, latitude='38.918229', longitude='-77.023795',
        venue_name='9:30 Club')
    counting_crows_show_1.save()

    ############################################################################
    #                               Users
    ############################################################################
    kwargs = {'email': 'john@gmail.com', 'groups': ['FAN']}
    john = models.BasicProfile.create_user(
        'john', **kwargs)

    kwargs = {'email': 'alice@gmail.com', 'groups': ['FAN']}
    alice = models.BasicProfile.create_user(
        'alice', **kwargs)

    kwargs = {'email': 'bob@gmail.com', 'groups': ['FAN']}
    bob = models.BasicProfile.create_user(
        'bob', **kwargs)

    counting_crows_artist.connected_users.add(bob)


    ############################################################################
    #                               Admin
    ############################################################################
    kwargs = {'email': 'none@none.com', 'groups': ['ADMIN']}
    john = models.BasicProfile.create_user(
        'admin', **kwargs)


    ############################################################################
    #                               Messages
    ############################################################################
    msg = models.Message(
        text='The Counting Crows are playing a show next week!',
        artist=counting_crows_artist)
    msg.save()


if __name__ == "__main__":
    run()
