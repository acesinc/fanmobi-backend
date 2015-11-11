"""
Utility functions
"""
import logging
import math

logger = logging.getLogger('fanmobi')

def str_to_bool(val):
    if not val:
        return False
    falsy = ['0', 'false']
    val = val.lower()
    if val in falsy:
        return False
    else:
        return True

def is_inside_radius(center_lat, center_lon, lat, lon, radius):
    """
    Determines if a given point is within a radius of another point

    Args:
        center_lat: the latitude (in degrees) of the center point
        center_lon: the longitude (in degrees) of the center point
        lat: the latitude (in degrees) of the point to test
        lon: the longitude (in degrees) of the point to test
        radius: the radius (in km) to check

    Returns:
        True if the point is within the given radius, False otherwise
    """
    # convert degrees -> radians
    center_lat = float(center_lat) * math.pi/180
    center_lon = float(center_lon) * math.pi/180
    lat = float(lat) * math.pi/180
    lon = float(lon) * math.pi/180
    radius = float(radius)
    earth_radius_km = float(6371)
    # calculate via Great Circle Distance: http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates#Distance
    km_apart = math.acos(math.sin(center_lat) * math.sin(lat) + math.cos(center_lat) * math.cos(lat) * math.cos(lon - (center_lon))) * earth_radius_km
    logger.debug('two points are %s km apart' % km_apart)
    return km_apart <= radius