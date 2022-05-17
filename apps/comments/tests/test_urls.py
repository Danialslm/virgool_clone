from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework.reverse import reverse

from apps.comments import views


class CommentUrlsTest(SimpleTestCase):
    def test_comment_add_url(self):
        url = reverse('comments:add', kwargs={'post_hash': 'sample'})
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.PostCommentCreateAPIView.__name__,
        )

    def test_comment_delete_url(self):
        url = reverse('comments:delete', kwargs={'pk': 1})
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.PostCommentDestroyAPIView.__name__,
        )

    def test_post_comment_list_url(self):
        url = reverse('comments:post_comments', kwargs={'hash': 'sample'})
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.PostCommentListAPIView.__name__,
        )

    def test_comment_reply_list_url(self):
        url = reverse('comments:replies', kwargs={'parent_id': 1})
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.CommentReplyListAPIView.__name__,
        )
