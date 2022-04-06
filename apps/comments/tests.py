import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.reverse import reverse

from apps.comments import views
from apps.comments.models import Comment
from apps.posts.models import Post
from apps.utils import otp

UserModel = get_user_model()


class CommentModelsTestCase(TestCase):
    def setUp(self):
        author = UserModel.objects.create_user(
            email='test@test.localhost',
        )
        self.post = Post.objects.create(title='test', author=author)

    def test_comment_creation(self):
        user = UserModel.objects.create_user(
            email='test_user@test.localhost',
        )
        comment = Comment.objects.create(
            post=self.post,
            user=user,
            text='test comment',
        )

        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, user)
        self.assertEqual(comment.text, 'test comment')
        self.assertIsNotNone(comment.commented_at)
        self.assertIsNone(comment.parent)

        # comment reply
        reply = Comment.objects.create(
            post=self.post,
            user=user,
            parent=comment,
            text='test comment reply',
        )
        self.assertEqual(reply.parent, comment)


class CommentViewsTestCase(TestCase):
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

    def test_post_comment_create_view(self):
        url = reverse('comments:add', kwargs={'post_hash': self.post.hash})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostCommentCreateAPIView.__name__,
        )

        response = self.client.post(
            url,
            data={'text': 'test comment'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_as_json = json.loads(response.rendered_content)
        self.assertDictContainsSubset({'text': 'test comment'}, response_as_json)

        # comment reply
        parent_id = response_as_json['id']
        response = self.client.post(
            url,
            data={'text': 'test comment reply', 'parent': parent_id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_as_json = json.loads(response.rendered_content)
        self.assertDictContainsSubset({'text': 'test comment reply', 'parent': parent_id}, response_as_json)

    def test_post_comment_list_view(self):
        url = reverse('comments:post_comments', kwargs={'hash': self.post.hash})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.PostCommentListAPIView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_reply_list_view(self):
        parent_comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='test comment',
        )

        url = reverse('comments:replies', kwargs={'parent_id': parent_comment.id})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.CommentReplyListAPIView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
