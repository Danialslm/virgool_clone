from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.comments.models import Comment
from apps.posts.models import Post

UserModel = get_user_model()


class CommentModelsTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )
        self.post = Post.objects.create(title='sample', author=self.user)

    def test_comment_creation(self):
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='sample comment',
        )

        self.assertIs(comment.post, self.post)
        self.assertIs(comment.user, self.user)
        self.assertEqual(comment.text, 'sample comment')
        self.assertIsNotNone(comment.commented_at)
        self.assertIsNone(comment.parent)

    def test_reply_comment_creation(self):
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='sample comment',
        )

        reply = Comment.objects.create(
            post=self.post,
            user=self.user,
            parent=comment,
            text='sample comment reply',
        )
        self.assertIs(reply.parent, comment)
