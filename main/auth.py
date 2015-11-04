"""
Auth
"""
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

class FanmobiAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if 'username' not in request.session:
            return None

        try:
            user = User.objects.get(username=request.session['username'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)