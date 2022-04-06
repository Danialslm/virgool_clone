from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(label=_('tag name'), max_length=15)

    class Meta:
        model = Tag
        fields = ('id', 'name')
