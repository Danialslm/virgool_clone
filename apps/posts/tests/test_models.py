from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.posts.models import Post

UserModel = get_user_model()


class PostModelsTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='test@test.localhost',
        )

    def test_post_creation(self):
        post = Post.objects.create(title='sample', author=self.user)

        self.assertTrue(post.is_draft)
        self.assertIsNotNone(post.raw_slug)
        self.assertIsNotNone(post.hash)
        self.assertIsNotNone(post.created_at)
        # post doesn't published so published date must be None
        self.assertIsNone(post.published_at)
        self.assertIs(post.author, self.user)

    def test_publish_post(self):
        post = Post.objects.create(title='sample', author=self.user)

        # try publish a post which hasn't any content
        with self.assertRaises(ValidationError):
            post.publish()

        post.content = 'sample content'
        post.publish()

        self.assertIsNotNone(post.published_at)
        self.assertEqual(post.slug, post.raw_slug + '-' + post.hash)
        self.assertFalse(post.is_draft)

    def test_draft_post(self):
        # create a post and publish it first
        post = Post.objects.create(title='sample', content='sample', author=self.user)
        post.publish()

        post.draft()
        self.assertTrue(post.is_draft)
