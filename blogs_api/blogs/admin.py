from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "created_at", "published_at"]
    list_filter = ["status", "created_at", "author"]
    search_fields = ["title", "content", "tags"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
