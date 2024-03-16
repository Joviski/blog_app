from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .models import Post


class PostModelTests(TestCase):
    """Post Model Test Case."""
    def setUp(self):
        """setUp function."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user,
            published=True
        )

    def test_model_creation(self):
        """Test model creation."""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post.')
        self.assertEqual(self.post.author, self.user)
        self.assertTrue(self.post.published)

    def test_string_representation(self):
        """Test str() method."""
        self.assertEqual(str(self.post), f"{self.post.id} - {self.post.title}")


class PostViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123'
        )
        self.token = Token.objects.create(user=self.user)
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.other_post = Post.objects.create(
            title='Other Post',
            content='Other content',
            author=self.other_user
        )

    def test_authentication_required_to_access_posts(self):
        response = self.client.get('/api/blog/posts/')
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_user_can_access_own_posts(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/blog/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Ensure user sees only their post

    def test_create_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {'title': 'New Post', 'content': 'New content'}
        response = self.client.post('/api/blog/posts/', data)
        self.assertEqual(response.status_code, 201)  # Created
        self.assertEqual(Post.objects.count(), 3)

    def test_read_post_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(f'/api/blog/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_update_own_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {'title': 'Updated Post'}
        response = self.client.patch(f'/api/blog/posts/{self.post.pk}/', data)
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')

    def test_delete_own_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(f'/api/blog/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, 204)  # No Content
        self.assertEqual(Post.objects.count(), 1)  # Only the other user's post remains

    def test_user_cannot_access_others_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(f'/api/blog/posts/{self.other_post.pk}/')
        self.assertEqual(response.status_code, 404)  # Will not find the object
