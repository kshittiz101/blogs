from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from .models import Blog
from .serializers import (
    BlogListSerializer,
    BlogDetailSerializer,
    BlogCreateUpdateSerializer,
)
from .permissions import IsAuthorOrReadOnly
from .filters import BlogFilter


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = BlogFilter
    search_fields = ["title", "content", "tags"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BlogCreateUpdateSerializer
        elif self.action == "retrieve":
            return BlogDetailSerializer
        return BlogListSerializer

    def get_queryset(self):
        queryset = Blog.objects.select_related("author")
        user = self.request.user
        if user.is_authenticated:
            if self.action == "list" and not self.request.query_params.get(
                "author"
            ):
                queryset = queryset.filter(
                    models.Q(status="published") | models.Q(author=user)
                )
            elif self.action == "list" and self.request.query_params.get(
                "author"
            ):
                pass
            else:
                if self.action in ("retrieve",):
                    blog = queryset.filter(pk=self.kwargs.get("pk")).first()
                    if blog and blog.author != user and blog.status == "draft":
                        queryset = queryset.filter(status="published")
        else:
            if self.action == "list":
                queryset = queryset.filter(status="published")
            elif self.action == "retrieve":
                blog = queryset.filter(pk=self.kwargs.get("pk")).first()
                if blog and blog.status == "draft":
                    queryset = queryset.none()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        blog = self.get_object()
        if blog.author != request.user:
            return Response(
                {"detail": "Not authorized."},
                status=status.HTTP_403_FORBIDDEN,
            )
        blog.status = "published"
        blog.published_at = timezone.now()
        blog.save()
        return Response(
            BlogDetailSerializer(blog, context={"request": request}).data
        )

    @action(detail=True, methods=["post"])
    def draft(self, request, pk=None):
        blog = self.get_object()
        if blog.author != request.user:
            return Response(
                {"detail": "Not authorized."},
                status=status.HTTP_403_FORBIDDEN,
            )
        blog.status = "draft"
        blog.published_at = None
        blog.save()
        return Response(
            BlogDetailSerializer(blog, context={"request": request}).data
        )

    @action(detail=False, methods=["get"])
    def my_blogs(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        blogs = Blog.objects.filter(author=request.user).select_related("author")
        page = self.paginate_queryset(blogs)
        if page is not None:
            serializer = BlogListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        serializer = BlogListSerializer(blogs, many=True, context={"request": request})
        return Response(serializer.data)
