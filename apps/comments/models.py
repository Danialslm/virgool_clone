from django.db import models
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    post = models.ForeignKey(
        'posts.Post',
        verbose_name=_('post'),
        related_name='comments',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        'users.User',
        verbose_name=_('user'),
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    commented_at = models.DateTimeField(_('commented at'), auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        verbose_name=_('replies'),
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
    )
    replies_count = models.PositiveSmallIntegerField(_('replies count'), default=0)

    def __str__(self):
        return self.text
