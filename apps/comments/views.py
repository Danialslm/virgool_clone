from rest_framework.generics import (
    ListAPIView, CreateAPIView, DestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated

from apps.comments.models import Comment
from apps.comments.serializers import CommentSerializer
from apps.posts.models import Post
from apps.utils.paginators import BaseResultsPagination


class IsCommentAuthor(IsAuthenticated):
    """
    Allow access only to comment author.
    """

    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user)


class PostCommentListAPIView(ListAPIView):
    """
    List of post comments.
    """
    serializer_class = CommentSerializer
    pagination_class = BaseResultsPagination

    def get_queryset(self):
        return Comment.objects.filter(
            post__hash=self.kwargs.get('hash'),
            parent__isnull=True,
        ).select_related('user')


class CommentReplyListAPIView(ListAPIView):
    """
    List of comment replies.
    """
    serializer_class = CommentSerializer
    pagination_class = BaseResultsPagination

    def get_queryset(self):
        return Comment.objects.filter(
            parent_id=self.kwargs.get('parent_id'),
        ).select_related('user')


class PostCommentCreateAPIView(CreateAPIView):
    """
    Add comment to post or reply to comment.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(
            Post,
            hash=self.kwargs.get('post_hash'),
            is_draft=False,
        )
        instance = serializer.save(user=self.request.user, post=post)

        # if the created comment has parent comment,
        # increase the parent comment replies count
        if instance.parent:
            instance.parent.replies_count += 1
            instance.parent.save(update_fields=['replies_count'])

        # increase the post comments count
        post.comments_count += 1
        post.save(update_fields=['comments_count'])


class PostCommentDestroyAPIView(DestroyAPIView):
    """
    Delete a comment or reply by id.
    """
    permission_classes = (IsCommentAuthor,)
    queryset = Comment.objects.select_related('post', 'parent', 'user')

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        # if the deleted comment had parent comment,
        # decrease the parent comment replies count
        if instance.parent:
            instance.parent.replies_count -= 1
            instance.parent.save(update_fields=['replies_count'])

        # decrease the post comment count
        instance.post.comments_count -= 1
        instance.post.save(update_fields=['comments_count'])
