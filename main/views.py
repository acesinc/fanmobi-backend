"""
Views
"""
import logging

from rest_framework import viewsets

import main.permissions as permissions
import main.serializers as serializers
import main.models as models
import main.services as services

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

class GenreViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_genres()
    serializer_class = serializers.GenreSerializer
    permission_classes = (permissions.IsFan,)
