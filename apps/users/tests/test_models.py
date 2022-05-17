from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.posts.models import Post
from apps.users.models import User, get_email_username

UserModel = get_user_model()


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_credentials = {'email': 'sample@sample.sample'}

    def setUp(self):
        self.author = UserModel.objects.create_user(email='author@sample.sample')
        self.post = Post.objects.create(title='sample', author=self.author)

    def test_custom_user_model(self):
        """ Check the custom user model is set correctly. """
        self.assertIs(UserModel, User)

    def test_get_email_username(self):
        username = get_email_username(self.user_credentials['email'])
        self.assertEqual(username, 'sample')

    def test_normal_user_creation(self):
        user = UserModel.objects.create_user(**self.user_credentials)

        self.assertEqual(user.email, self.user_credentials['email'])
        # test that `full_name` and `username` is filled
        self.assertEqual(user.full_name, 'sample')
        self.assertEqual(user.username, 'sample')

        self.assertEqual(user.biography, '')
        self.assertEqual(user.avatar, 'default-avatar.jpg')

    def test_superuser_creation(self):
        admin = UserModel.objects.create_superuser(**self.user_credentials)

        self.assertEqual(admin.email, self.user_credentials['email'])
        # test that `full_name` and `username` is filled
        self.assertEqual(admin.full_name, 'sample')
        self.assertEqual(admin.username, 'sample')

        self.assertEqual(admin.biography, '')
        self.assertEqual(admin.avatar, 'default-avatar.jpg')

    def test_user_like(self):
        self.author.like(self.post)
        self.assertTrue(self.author.is_liked(self.post))

    def test_user_unlike(self):
        self.author.unlike(self.post)
        self.assertFalse(self.author.is_liked(self.post))
