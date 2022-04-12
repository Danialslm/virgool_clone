import re
from os import path

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.postgres.fields import CICharField, CIEmailField
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image

from apps.users.manager import UserManager


def user_avatar_upload_path(instance, filename):
    ext = path.splitext(filename)[1]
    return f'users/{instance.pk}/avatar{ext}'


def get_email_username(email):
    """
     Get the username part from given email.
     Returns:
          str:username of email address
    """
    pattern = r'^([^@]+)@[^@]+$'
    res = re.search(pattern, email)
    if res is not None:
        return res.group(1)
    else:
        raise ValueError(f"Can't find username of {email}")


class User(AbstractUser):
    first_name = None
    last_name = None
    password = None

    username_validator = UnicodeUsernameValidator()

    username = CICharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        ),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    email = CIEmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email address already exists.'),
        }
    )
    full_name = models.CharField(_('full name'), max_length=150, blank=True)
    biography = models.CharField(_('biography'), max_length=255, blank=True)
    avatar = models.ImageField(
        _('avatar'),
        upload_to=user_avatar_upload_path,
        default='default-avatar.jpg',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        # if user is creating, fill the `full_name` and `username` fields
        if not self.id:
            email_username = get_email_username(self.email)
            self.full_name = email_username
            self.username = email_username

        super().save(*args, **kwargs)

        # resize the user avatar
        avatar = Image.open(self.avatar.path)
        if (avatar.width, avatar.height) > settings.USER_AVATAR_SIZE:
            avatar.thumbnail(settings.USER_AVATAR_SIZE)
            avatar.save(self.avatar.path)  # saving avatar at the same path

    def like(self, post):
        """ Add user to given post likes. """
        post.likes.add(self)

    def unlike(self, post):
        """ Remove user like from post likes. """
        post.likes.remove(self)

    def is_liked(self, post):
        """ Return a bool that shows the user liked the post or not. """
        return post.likes.filter(id=self.id).exists()
