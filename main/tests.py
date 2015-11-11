"""
Utils tests
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from main import models as models
from main import utils as utils

class UtilsTest(TestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        pass

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        pass

    def test_str_to_bool(self):
        res = utils.str_to_bool('True')
        self.assertTrue(res)
        res = utils.str_to_bool('FALSE')
        self.assertFalse(res)
        res = utils.str_to_bool('false')
        self.assertFalse(res)
        res = utils.str_to_bool('0')
        self.assertFalse(res)

    def test_is_inside_radius(self):
        baltimore_lat = '39.2833'
        baltimore_lon = '-76.6167'

        baltimore_city_hall_lat = '39.2910'
        baltimore_city_hall_lon = '-76.6107'

        dc_lat = '38.9047'
        dc_lon = '-77.0164'

        # two points are 0.9999km apart
        res = utils.is_inside_radius(baltimore_lat, baltimore_lon,
            baltimore_city_hall_lat, baltimore_city_hall_lon, '1')
        self.assertTrue(res)

        res = utils.is_inside_radius(baltimore_lat, baltimore_lon,
            baltimore_city_hall_lat, baltimore_city_hall_lon, '.99')
        self.assertFalse(res)


        # baltimore->dc = 54.4km
        res = utils.is_inside_radius(baltimore_lat, baltimore_lon,
            dc_lat, dc_lon, '55')
        self.assertTrue(res)
        res = utils.is_inside_radius(baltimore_lat, baltimore_lon,
            dc_lat, dc_lon, '54')
        self.assertFalse(res)






