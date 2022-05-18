from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework.reverse import reverse

from apps.posts import views


class PostUrlsTest(SimpleTestCase):
    def test_post_create_url(self):
        url = reverse('posts:create')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostCreateAPIView.__name__,
        )

    def test_draft_post_list_url(self):
        url = reverse('posts:user_draft_posts')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.UserDraftPostListAPIView.__name__,
        )

    def test_published_post_list_url(self):
        url = reverse('posts:user_published_posts', kwargs={'username': 'sample'})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.UserPostListAPIView.__name__,
        )

    def test_post_retrieve_url(self):
        url = reverse('posts:detail', kwargs={'slug': 'sample'})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostRetrieveAPIView.__name__,
        )

    def test_post_update_url(self):
        url = reverse('posts:update', kwargs={'hash': 'sample'})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostUpdateAPIView.__name__,
        )

    def test_publish_post_url(self):
        url = reverse('posts:publish', kwargs={'hash': 'sample'})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PublishPostAPIView.__name__,
        )

    def test_draft_post_url(self):
        url = reverse('posts:draft', kwargs={'hash': 'sample'})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.DraftPostAPIView.__name__,
        )

    def test_post_like_url(self):
        url = reverse('posts:like', kwargs={'hash': 'sample'})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostLikeAPIView.__name__,
        )

    def test_latest_post_list_url(self):
        url = reverse('posts:latest')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.LatestPostListView.__name__,
        )

    def test_post_delete_url(self):
        url = reverse('posts:delete', kwargs={'hash': 'sample'})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostDeleteAPIView.__name__,
        )

    def test_post_search_url(self):
        url = reverse('posts:search')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostSearchListAPIView.__name__,
        )
