from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.posts.models import Post

UserModel = get_user_model()


class PostManagersTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )
        self.post = Post.objects.create(title='sample', content='sample', author=self.user)
        self.post.publish()

    def test_latest_query(self):
        latest_posts = Post.objects.latest()
        self.assertIn(self.post, latest_posts)

    def test_latest_query_failure(self):
        self.post.published_at = timezone.now() - timedelta(days=31)
        self.post.save()

        latest_posts = Post.objects.latest()
        self.assertNotIn(self.post, latest_posts)

    def test_search_query(self):
        result = Post.objects.search(query='sample')
        self.assertIn(self.post, result)

    def test_search_query_failure(self):
        result = Post.objects.search(query='does not exist')
        self.assertNotIn(self.post, result)
