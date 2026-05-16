import django_filters
from django.db import models
from .models import Blog


class BlogFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    author = django_filters.NumberFilter(field_name="author__id")
    status = django_filters.ChoiceFilter(choices=Blog.STATUS_CHOICES)
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Blog
        fields = ["status", "author", "tags"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value)
            | models.Q(content__icontains=value)
            | models.Q(tags__icontains=value)
        )
