from datetime import timedelta

from django.db.models import Manager, Q, QuerySet
from django.utils import timezone


class PostQueryset(QuerySet):
    def latest(self):
        """ List of posts published in the last month. """
        last_month = timezone.now() - timedelta(days=30)
        return self.filter(published_at__gte=last_month, is_draft=False)

    def search(self, query):
        """
        Search the given string (query) in title, description and content fields.
        """
        return self.filter(
            Q(title__icontains=query) | Q(title__trigram_word_similar=query) |
            Q(description__icontains=query) | Q(description__trigram_word_similar=query) |
            Q(content__icontains=query) | Q(content__trigram_word_similar=query)
        )


class PostManager(Manager.from_queryset(PostQueryset)):
    pass
