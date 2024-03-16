from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class UserViewSetTestCase(APITestCase):
    """User ViewSet Test Case."""
    def setUp(self):
        """setUp function."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.superuser = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword123'
        )
        self.token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)

    def test_authentication_required(self):
        """Test endpoints that require authentication without providing a token."""
        response = self.client.get('/api/account/users/')
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_permission_for_create_user(self):
        """Test 'create' doesn't require authentication."""
        data = {'username': 'newuser', 'password': 'newpassword123'}
        response = self.client.post('/api/account/users/', data)
        self.assertEqual(response.status_code, 201)  # Created

    def test_retrieve_user(self):
        """Test retrieve user."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(f'/api/account/users/{self.user.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_user_unauthorized(self):
        """Test update user unauthorized."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)
        response = self.client.patch(f'/api/account/users/{self.user.pk}/', {'username': 'updateduser'})
        self.assertEqual(response.status_code, 405)

    def test_login_success(self):
        """Test login success."""
        data = {'username': 'testuser', 'password': 'testpassword123'}
        response = self.client.post('/api/account/users/login/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_logout_success(self):
        """Test logout success."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/account/users/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], 'User logged out')