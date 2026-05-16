from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Blog


class BlogAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_blog(self):
        data = {
            "title": "My First Blog",
            "content": "Hello world!",
            "status": "draft",
        }
        response = self.client.post("/api/blogs/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Blog.objects.count(), 1)

    def test_list_blogs(self):
        Blog.objects.create(
            title="Test Blog",
            content="Test content",
            author=self.user,
            status="published",
        )
        response = self.client.get("/api/blogs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_unauthenticated_cannot_create(self):
        self.client.logout()
        data = {"title": "Hacked", "content": "bad", "status": "published"}
        response = self.client.post("/api/blogs/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
