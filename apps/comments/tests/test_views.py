from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from apps.comments import views
from apps.posts.models import Post

UserModel = get_user_model()
factory = APIRequestFactory()


class CommentViewsTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='test@test.localhost',
        )
        self.post = Post.objects.create(
            title='test', author=self.user, is_draft=False,
        )
        self.comment = self.post.comments.create(text='sample comment', user=self.user)

    def test_add_comment(self):
        """ Test adding a comment to a post. """
        view = views.PostCommentCreateAPIView.as_view()
        request = factory.post('/comments/add/', data={'text': 'sample comment'})
        force_authenticate(request, user=self.user)

        response = view(request, post_hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertContains(response, 'sample comment', status_code=status.HTTP_201_CREATED)

    def test_add_reply_comment(self):
        """ Test adding a reply comment to a comment/ """
        view = views.PostCommentCreateAPIView.as_view()
        request = factory.post('/comments/add/', data={'text': 'sample comment', 'parent': self.comment.id})
        force_authenticate(request, user=self.user)

        response = view(request, post_hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parent'], self.comment.id)

    def test_post_comment_list(self):
        view = views.PostCommentListAPIView.as_view()
        request = factory.get('/comments/post/')

        response = view(request, hash=self.post.hash)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_comment_reply_list(self):
        view = views.CommentReplyListAPIView.as_view()
        request = factory.get('/comments/replies/')

        response = view(request, parent_id=self.comment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
