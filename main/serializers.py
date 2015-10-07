"""
Serializers
"""
import logging

from rest_framework import serializers

import main.models as models

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre