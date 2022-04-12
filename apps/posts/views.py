from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, DestroyAPIView,
    RetrieveUpdateAPIView, CreateAPIView, GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.posts import serializers
from apps.posts.models import Post
from apps.core.paginators import BaseResultsPagination


class IsPostAuthor(IsAuthenticated):
    """
    Allows access only to post author.
    """

    def has_object_permission(self, request, view, obj):
        return bool(obj.author == request.user)


class LatestPostListView(ListAPIView):
    """
    List of latest posts.
    """
    queryset = Post.objects.latest().select_related('author')
    serializer_class = serializers.PostListSerializer
    pagination_class = BaseResultsPagination


class UserDraftPostListAPIView(ListAPIView):
    """
    List of logged-in user draft posts.
    """
    serializer_class = serializers.PostListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = BaseResultsPagination

    def get_queryset(self):
        return Post.objects.filter(
            is_draft=True,
            author=self.request.user,
        ).select_related('author')


class UserPostListAPIView(ListAPIView):
    """
    List of user published posts.
    """
    serializer_class = serializers.PostListSerializer
    pagination_class = BaseResultsPagination

    def get_queryset(self):
        return Post.objects.filter(
            is_draft=False,
            author__username=self.kwargs.get('username'),
        ).select_related('author')


class PostCreateAPIView(CreateAPIView):
    """
    Create a post.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Post.objects.all()
    serializer_class = serializers.PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve a post by.
    """
    serializer_class = serializers.PostRetrieveSerializer
    lookup_field = 'slug'
    queryset = Post.objects.filter(is_draft=False).select_related('author')


class PostUpdateAPIView(RetrieveUpdateAPIView):
    """
    Retrieve and update a post.
    """
    permission_classes = (IsPostAuthor,)
    serializer_class = serializers.PostUpdateSerializer
    lookup_field = 'hash'
    queryset = Post.objects.select_related('author').prefetch_related('tags')


class PostDeleteAPIView(DestroyAPIView):
    """
    Delete a post.
    """
    permission_classes = (IsPostAuthor,)
    lookup_field = 'hash'
    queryset = Post.objects.select_related('author').only('author__id')


class PublishPostAPIView(GenericAPIView):
    """
    Publish a post.
    """
    permission_classes = (IsPostAuthor,)
    queryset = Post.objects \
        .select_related('author') \
        .only('is_draft', 'published_at', 'raw_slug',
              'slug', 'hash', 'title', 'content', 'author__id')
    lookup_field = 'hash'

    def post(self, request, *args, **kwargs):
        self.get_object().publish()
        return Response({'success': True})


class DraftPostAPIView(GenericAPIView):
    """
    Draft a post.
    """
    permission_classes = (IsPostAuthor,)
    queryset = Post.objects.select_related('author').only('is_draft', 'author__id')
    lookup_field = 'hash'

    def post(self, request, *args, **kwargs):
        self.get_object().draft()
        return Response({'success': True})


class PostLikeAPIView(GenericAPIView):
    """
    Like (POST) and unlike (DELETE) a post.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Post.objects.filter(is_draft=False).only('likes_count')
    lookup_field = 'hash'
    serializer_class = serializers.PostRetrieveSerializer

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        self.request.user.like(post)

        # increase the post likes count
        post.likes_count += 1
        post.save(updating_likes_count=True)

        return Response({'success': True})

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        self.request.user.unlike(post)

        # decrease the post likes count
        post.likes_count -= 1
        post.save(updating_likes_count=True)

        return Response({'success': True}, status=204)


class PostSearchListAPIView(ListAPIView):
    """
    Search in posts and return result list.
    """
    serializer_class = serializers.PostListSerializer
    pagination_class = BaseResultsPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Post.objects \
            .search(query) \
            .filter(is_draft=False) \
            .select_related('author')
