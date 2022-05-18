from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from apps.posts import views
from apps.posts.models import Post

UserModel = get_user_model()
factory = APIRequestFactory()


class PostRatingTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )
        self.post = Post.objects.create(title='sample', content='sample', author=self.user)
        self.post.publish()

    def test_post_like(self):
        view = views.PostLikeAPIView.as_view()
        request = factory.post('/posts/like/')
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertTrue(self.user.is_liked(self.post))
        self.assertEqual(self.post.likes_count, 1)

    def test_post_unlike(self):
        view = views.PostLikeAPIView.as_view()
        request = factory.delete('/posts/like/')
        force_authenticate(request, user=self.user)

        self.post.likes_count = 1
        self.post.save()

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.user.is_liked(self.post))
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 0)

    def test_like_draft_post(self):
        self.post.draft()

        view = views.PostLikeAPIView.as_view()
        request = factory.post('/posts/like/')
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unlike_draft_post(self):
        self.post.draft()

        view = views.PostLikeAPIView.as_view()
        request = factory.delete('/posts/like/')
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostCRUDTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )
        self.post = Post.objects.create(title='sample', author=self.user)

    def test_post_create_view(self):
        view = views.PostCreateAPIView.as_view()
        request = factory.post('/posts/create/')
        force_authenticate(request, user=self.user)

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_retrieve_view(self):
        # we need the post slug for retrieving the post
        # and for getting the post slug we should publish it
        self.post.content = 'sample'
        self.post.publish()

        view = views.PostRetrieveAPIView.as_view()
        request = factory.get('/posts/')

        response = view(request, slug=self.post.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_update_view(self):
        view = views.PostUpdateAPIView.as_view()
        request = factory.get('/posts/update/')
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {'title': 'new title', 'content': 'new content'}
        request = factory.patch('/posts/update/', data=data)
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'new title')
        self.assertEqual(response.data['content'], 'new content')

    def test_post_delete_view(self):
        view = views.PostDeleteAPIView.as_view()
        request = factory.delete('/posts/delete/')
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(self.post.DoesNotExist):
            self.post.refresh_from_db()

    def test_user_draft_post_list_view(self):
        view = views.UserDraftPostListAPIView.as_view()
        request = factory.get('/posts/draft/')
        force_authenticate(request, user=self.user)

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_published_post_list_view(self):
        view = views.UserPostListAPIView.as_view()
        request = factory.get('/posts/user/')

        response = view(request, username=self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_latest_post_list_view(self):
        view = views.LatestPostListView.as_view()
        request = factory.get('/posts/user/')

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_post_list_view(self):
        self.post.content = 'sample'
        self.post.publish()

        view = views.PostSearchListAPIView.as_view()
        request = factory.get('/posts/latest/?q=sample')

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'sample')


class PostPublicationTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )
        self.post = Post.objects.create(
            title='sample', author=self.user,
        )

    def test_publish_post_view(self):
        view = views.PublishPostAPIView.as_view()
        request = factory.post('/posts/publish/')
        force_authenticate(request, user=self.user)

        # save a sample content for the post
        # because for publication the post must be have content and title
        self.post.content = 'sample content'
        self.post.save()

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': True})
        self.post.refresh_from_db()
        self.assertFalse(self.post.is_draft)
        self.assertEqual(self.post.slug, self.post.raw_slug + '-' + self.post.hash)

    def test_draft_post_view(self):
        view = views.DraftPostAPIView.as_view()
        request = factory.post('/posts/draft/')
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': True})
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_draft)
