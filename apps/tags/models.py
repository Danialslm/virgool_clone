from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    tag = models.CharField(_('tag'), max_length=15, unique=True)

    def __str__(self):
        return self.tag
