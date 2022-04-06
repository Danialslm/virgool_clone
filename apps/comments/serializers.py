from rest_framework import serializers

from apps.comments.models import Comment
from apps.users.models import User


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'full_name', 'avatar', 'username')


class CommentSerializer(serializers.ModelSerializer):
    user = CommentAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id', 'parent', 'text', 'user',
            'replies_count', 'commented_at',
        )
        read_only_fields = ('replies_count', 'commented_at')
        extra_kwargs = {'post': {}}
