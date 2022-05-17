from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from apps.posts.models import Post
from apps.tags import views

UserModel = get_user_model()
factory = APIRequestFactory()


class TagViewsTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )
        self.post = Post.objects.create(
            title='sample', author=self.user, is_draft=False,
        )
        self.post.tags.create(tag='sample tag')

    def test_add_tag(self):
        """ Test adding a tag to a post. """
        view = views.PostTagsAPIView.as_view()
        request = factory.post('/tags/post/', data={'tag': 'sample tag'})
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': True})
        self.assertEqual(self.post.tags.count(), 1)

    def test_remove_tag(self):
        """ Test removing a tag from a post. """
        view = views.PostTagsAPIView.as_view()
        request = factory.delete('/tags/post/', data={'tag': 'sample tag'})
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': True})
        self.assertEqual(self.post.tags.count(), 0)

    def test_remove_tag_failure(self):
        view = views.PostTagsAPIView.as_view()
        request = factory.delete('/tags/post/', data={'tag': 'does not exist tag'})
        force_authenticate(request, user=self.user)

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tag_posts_view(self):
        """ Test tag posts list. """
        view = views.TagPostListAPIView.as_view()
        request = factory.get('/tags/')

        response = view(request, tag='sample tag')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_tag_search(self):
        view = views.TagSearchListAPIView.as_view()
        request = factory.get('/tags/search/?q=sample tag')

        response = view(request)
        self.assertGreaterEqual(len(response.data), 1)
