"""
Custom permissions

Can do things like if view.action == 'create'

"""
import logging

from rest_framework import permissions
import main.models as models
import main.services as services

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

logger = logging.getLogger('fanmobi')

class ProfilePermissions(permissions.BasePermission):
    """
    Permissions to apply on all Profile views

    Rules:
        - ADMINs have full access
        - FANs and ARTISTS can only view and edit their own info
    """
    def has_permission(self, request, view):
        if request.method == 'POST' and not services.is_admin(request.user.username):
            return False
        return True
    def has_object_permission(self, request, view, obj):
        if services.is_admin(request.user.username):
            return True
        if request.user.username == obj.user.username:
            return True
        return False

class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        user_profile = services.get_profile(request.user.username)
        if user_profile:
            return True
        else:
            return False

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

        logger.debug('user %s is not an artist' % request.user.username)
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
        if services.is_admin(request.user.username):
            return True
        return False
