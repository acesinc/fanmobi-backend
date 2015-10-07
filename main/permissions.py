"""
Custom permissions

Can do things like if view.action == 'create'

"""
from rest_framework import permissions
import main.models as models
import main.services as services

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        user_profile = services.get_profile(request.user.username)
        if (request.method in SAFE_METHODS or \
            user_profile.highest_role() in ['ADMIN']):
            return True
        return False


class IsArtistOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        user_profile = services.get_profile(request.user.username)
        if (request.method in SAFE_METHODS or \
            user_profile.highest_role() in ['ADMIN', 'ARTIST']):
            return True
        return False

class IsFan(permissions.BasePermission):
    """
    Global permission check if current user is a Fan
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        profile = services.get_profile(request.user.username)
        if profile is None:
           return False
        if 'FAN' in profile.user.groups.values_list('name', flat=True):
            return True
        else:
            return False

class IsArtist(permissions.BasePermission):
    """
    Global permission check if current user is an Artist
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        profile = services.get_profile(request.user.username)
        if profile is None:
            return False
        if 'ARTIST' in profile.basic_profile.user.groups.values_list('name', flat=True):
            return True
        else:
            return False

class IsAdmin(permissions.BasePermission):
    """
    Global permission check if current user is an Admin
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        profile = services.get_profile(request.user.username)
        if profile is None:
            return False
        if 'ADMIN' in profile.basic_profile.user.groups.values_list('name', flat=True):
            return True
        else:
            return False