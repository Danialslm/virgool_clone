from rest_framework import serializers

from apps.posts.models import Post
from apps.users.serializers import UserDetailsSerializer


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'is_draft', 'hash', 'created_at',)
        read_only_fields = ('is_draft', 'hash', 'created_at',)
        extra_kwargs = {'author': {}}


class PostListSerializer(serializers.ModelSerializer):
    author = UserDetailsSerializer()

    class Meta:
        model = Post
        fields = (
            'id', 'is_draft', 'hash', 'slug',
            'created_at', 'title', 'author',
        )


class PostUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'is_draft', 'title', 'raw_slug', 'slug',
            'content', 'hash', 'description',
            'primary_image', 'created_at', 'tags',
        )
        read_only_fields = ('is_draft', 'slug')

    def get_tags(self, obj):
        return [tag.tag for tag in obj.tags.all()]


class PostRetrieveSerializer(serializers.ModelSerializer):
    author = UserDetailsSerializer()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'description',
            'content', 'raw_slug', 'slug',
            'hash', 'primary_image', 'author',
            'tags', 'likes_count', 'comments_count',
            'created_at', 'published_at', 'is_liked',
        )

    def get_is_liked(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return request.user.is_liked(obj)
