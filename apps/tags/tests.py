from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.reverse import reverse

from apps.posts.models import Post
from apps.tags import views
from apps.tags.models import Tag
from apps.utils import otp

UserModel = get_user_model()


class TagModelsTestCase(TestCase):
    def test_tag_creation(self):
        tag = Tag.objects.create(name='test tag')

        self.assertEqual(tag.name, 'test tag')


class TagViewsTestCase(TestCase):
    def setUp(self):
        # create an user and authenticate it
        self.user = UserModel.objects.create_user(
            email='test@test.localhost',
        )
        self.client.post(
            reverse('users:login'),
            data={
                'email': self.user.email,
            }
        )
        # create otp code to authenticate
        code = otp.create_new_otp(self.user.id)
        self.client.post(
            reverse('users:login_verification'),
            data={
                'verification_code': code,
            }
        )
        # create a post
        self.post = Post.objects.create(
            title='test post', author=self.user, is_draft=False,
        )

    def test_post_tags_view(self):
        url = reverse('tags:post_tags', kwargs={'hash': self.post.hash})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostTagsAPIView.__name__,
        )

        # add tag
        response = self.client.post(url, data={
            'name': 'test tag',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.post.tags.filter(name='test tag').first())

        # remove tag
        response = self.client.delete(
            url,
            content_type='application/json',
            data={'name': 'test tag'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(self.post.tags.filter(name='test tag').first())

        # try to remove a tag that does not exist from the post
        response = self.client.delete(
            url,
            content_type='application/json',
            data={'name': 'does not exist'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tag_posts_view(self):
        tag = Tag.objects.create(name='test tag')
        self.post.tags.add(tag)

        url = reverse('tags:tag_posts', kwargs={'tag': tag.name})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.TagPostListAPIView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset({'title': 'test post'}, dict(response.data['results'][0]))
