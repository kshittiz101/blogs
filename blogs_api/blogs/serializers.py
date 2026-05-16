from rest_framework import serializers
from .models import Blog


class BlogListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "author",
            "author_name",
            "status",
            "tags",
            "created_at",
            "published_at",
        ]
        read_only_fields = ["author", "slug", "created_at", "published_at"]


class BlogDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "excerpt",
            "featured_image",
            "author",
            "author_name",
            "status",
            "tags",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = ["author", "slug", "created_at", "updated_at", "published_at"]


class BlogCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "title",
            "content",
            "excerpt",
            "featured_image",
            "status",
            "tags",
        ]

    def validate_status(self, value):
        if value not in dict(Blog.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status choice")
        return value
