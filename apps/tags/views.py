from django.utils.translation import gettext_lazy as _
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from apps.posts.models import Post
from apps.posts.serializers import PostListSerializer
from apps.posts.views import IsPostAuthor
from apps.tags.models import Tag
from apps.tags.serializers import TagSerializer
from apps.core.paginators import BaseResultsPagination


class PostTagsAPIView(GenericAPIView):
    """
    Add (POST) and remove (DELETE) a tag to a post.
    """
    permission_classes = (IsPostAuthor,)
    lookup_field = 'hash'
    queryset = Post.objects.select_related('author').only('tags', 'author__id')
    serializer_class = TagSerializer

    def get_tag(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data['tag']

    def post(self, request, *args, **kwargs):
        tag = self.get_tag()
        post = self.get_object()
        # limitation check
        if post.tags.count() >= 5:
            return Response({'detail': _('A post can have only five tags.')}, status=400)
        tag, created = Tag.objects.get_or_create(
            tag=tag,
            defaults={'tag': tag}
        )
        post.tags.add(tag)
        return Response({'success': True})

    def delete(self, request, *args, **kwargs):
        tag = self.get_tag()
        post = self.get_object()
        try:
            tag = Tag.objects.get(tag=tag)
        except Tag.DoesNotExist:
            return Response({'detail': f'There is no {tag} tag.'}, status=400)

        post.tags.remove(tag)
        return Response({'success': True})


class TagPostListAPIView(ListAPIView):
    """
    List of posts which have this tag.
    """
    serializer_class = PostListSerializer
    pagination_class = BaseResultsPagination

    def get_queryset(self):
        return Post.objects \
            .select_related('author') \
            .filter(tags__tag=self.kwargs.get('tag'))


class TagSearchListAPIView(ListAPIView):
    """
    Search in tags and return result list
    """
    serializer_class = TagSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Tag.objects.filter(tag__icontains=query)
