from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework.reverse import reverse

from apps.tags import views


class TagUrlsTest(SimpleTestCase):
    def test_post_tags_url(self):
        url = reverse('tags:post_tags', kwargs={'hash': 'sample'})
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.PostTagsAPIView.__name__,
        )

    def test_tag_search_url(self):
        url = reverse('tags:search')
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.TagSearchListAPIView.__name__,
        )

    def test_tag_posts_url(self):
        url = reverse('tags:tag_posts', kwargs={'tag': 'sample tag'})
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.TagPostListAPIView.__name__,
        )
