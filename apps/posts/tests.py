from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.reverse import reverse

from apps.posts import views
from apps.posts.models import Post
from apps.tags.models import Tag
from apps.utils import otp

UserModel = get_user_model()


class PostModelsTestCase(TestCase):
    def setUp(self):
        self.author = UserModel.objects.create_user(
            email='test@test.localhost',
        )
        tag = Tag.objects.create(name='test tag')
        self.post = Post.objects.create(title='test', author=self.author)
        self.post.tags.add(tag)

    def test_post_creation(self):
        self.assertTrue(self.post.is_draft)
        self.assertEqual(self.post.author, self.author)
        self.assertIsNotNone(self.post.tags.filter(name='test tag').first())

    def test_post_like_unlike(self):
        user = UserModel.objects.create_user(
            email='test_user@test.localhost',
        )
        user.like(self.post)
        self.assertTrue(user.is_liked(self.post))

        user.unlike(self.post)
        self.assertFalse(user.is_liked(self.post))


class PostViewsTestCase(TestCase):
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
            title='test', author=self.user, is_draft=False,
        )

    def test_post_create_view(self):
        url = reverse('posts:create')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostCreateAPIView.__name__,
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_draft_post_list_view(self):
        url = reverse('posts:user_draft_posts')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.UserDraftPostListAPIView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_published_post_list_view(self):
        url = reverse('posts:user_published_posts', kwargs={'username': self.user.username})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.UserPostListAPIView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_retrieve_view(self):
        self.post.publish()

        url = reverse('posts:detail', kwargs={'slug': self.post.slug})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostRetrieveAPIView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_update_view(self):
        url = reverse('posts:update', kwargs={'hash': self.post.hash})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostUpdateAPIView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {'title': 'test', 'content': 'test'}
        response = self.client.put(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_publish_post_view(self):
        url = reverse('posts:publish', kwargs={'hash': self.post.hash})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PublishPostAPIView.__name__,
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_draft_post_view(self):
        url = reverse('posts:draft', kwargs={'hash': self.post.hash})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.DraftPostAPIView.__name__,
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_like_view(self):
        url = reverse('posts:like', kwargs={'hash': self.post.hash})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostLikeAPIView.__name__,
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_liked(self.post))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.user.is_liked(self.post))

    def test_latest_post_list_view(self):
        url = reverse('posts:latest')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.LatestPostListView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_delete_view(self):
        url = reverse('posts:delete', kwargs={'hash': self.post.hash})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostDeleteAPIView.__name__,
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
