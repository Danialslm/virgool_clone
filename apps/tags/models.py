from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    name = models.CharField(_('tag name'), max_length=15, unique=True)

    def __str__(self):
        return self.name
