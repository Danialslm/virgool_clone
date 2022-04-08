from os import path
from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.posts.managers import PostManager


def post_primary_image_upload_path(instance, filename):
    ext = path.splitext(filename)[1]
    return f'users/{instance.author.pk}/posts/{instance.hash}{ext}'


def gen_hash():
    """ Generate a unique string by uuid4 that sliced to 12 character. """
    return uuid4().hex[:12]


class Post(models.Model):
    is_draft = models.BooleanField(_('draft'), default=True)
    title = models.CharField(_('title'), max_length=50)
    description = models.CharField(_('description'), max_length=100, blank=True)
    content = models.TextField(_('content'))
    raw_slug = models.CharField(_('raw slug'), blank=True, max_length=50)
    slug = models.SlugField(_('slug'), blank=True, allow_unicode=True)
    hash = models.CharField(_('hash'), max_length=15, unique=True, default=gen_hash, editable=False)
    primary_image = models.ImageField(_('primary image'), upload_to=post_primary_image_upload_path, null=True)
    author = models.ForeignKey(
        'users.User',
        verbose_name=_('author'),
        on_delete=models.CASCADE,
        related_name='posts'
    )
    tags = models.ManyToManyField('tags.Tag', verbose_name=_('tags'), related_name='posts')
    likes = models.ManyToManyField('users.User', verbose_name=_('likes'), related_name='liked_posts')
    likes_count = models.PositiveSmallIntegerField(_('likes count'), default=0)
    comments_count = models.PositiveSmallIntegerField(_('comments count'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    published_at = models.DateTimeField(_('published at'), null=True)

    objects = PostManager()

    def __str__(self):
        return self.title

    def save(self, updating_likes_count=False, *args, **kwargs):
        if not updating_likes_count and not self.is_draft:
            # if raw slag was not considered, use title as raw slug
            if not self.raw_slug:
                self.raw_slug = self.title

            # create original slug
            self.slug = self.raw_slug + '-' + self.hash
        super().save(*args, **kwargs)

    def publish(self):
        """ Publish the post object. """
        if not self.is_draft:
            return
        if not self.title or not self.content:
            raise ValidationError({'detail': _('The post must have a title and content to be published.')})

        self.published_at = timezone.now()
        self.is_draft = False

        self.save(update_fields=['is_draft', 'published_at', 'slug', 'raw_slug'])

    def draft(self):
        """ draft the post object. """
        if self.is_draft:
            return

        self.is_draft = True
        self.save()
