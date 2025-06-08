from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from .models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from datetime import timedelta


class UserRegisterAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.existing_user_data = {
            'username': 'existuser',
            'email': 'existing@gmail.com',
            'password': 'existingpassword123'
        }
        self.existing_user = User.objects.create_user(**self.existing_user_data)
        self.url = reverse('account:user_register')

    def test_user_registration_success(self):
        self.registration_data = {
            'username': 'newuser',
            'email': 'newuser@gmail.com',
            'password': 'testpassword123',
            'password2': 'testpassword123'
        }
        response = self.client.post(self.url, self.registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertIn('message', response.data)

    def test_user_registration_duplicate_username(self):
        duplicate_data = {
            'username': 'existuser',
            'email': 'different@gmail.com',
            'password': 'existingpassword123'
        }
        response = self.client.post(self.url, duplicate_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_user_registration_duplicate_email(self):
        duplicate_data = {
            'username': 'differentuser',
            'email': 'existing@gmail.com',
            'password': 'existingpassword123',
            'password2': 'existingpassword123'
        }
        response = self.client.post(self.url, duplicate_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_password_mismatch(self):
        mismatch_data = {
            'username': 'testuser2',
            'email': 'test2@gmail.com',
            'password': 'testpassword123',
            'password2': 'diffpass123'
        }
        response = self.client.post(self.url, mismatch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_user_regist_invalid_email(self):
        invalid_data = {
            'username': 'testuser3',
            'email': 'test3',
            'password': 'testpassword123',
            'password123': 'testpassword123'
        }
        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

class TokenObtainPairTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.refresh_url = reverse('account:token_obtain_pair')

        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='testpassword123',
        )

    def test_token_obtain_pair_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.refresh_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        token = AccessToken(response.data['access'])
        self.assertEqual(token['email'], 'test@gmail.com')

class AccessTokenTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('account:token_obtain_pair')
        self.refresh_url = reverse('account:token_refresh')

        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='testpassword123',
        )

    def test_get_access_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh = response.data['refresh']
        self.assertIsNotNone(refresh)

        refresh_response = self.client.post(self.refresh_url, {'refresh': refresh}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        new_access = refresh_response.data['access']
        self.assertIsNotNone(new_access)

    def test_exp_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        refresh.set_exp(lifetime=timedelta(seconds=-1))

        response = self.client.post(self.refresh_url, {}, format='json', cookies={'refresh_token': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.change_password_url = reverse('account:change_password')
        self.user = User.objects.create_user(
            username='testuser',
            email='tes@gmail.com',
            password='testpassword123',
        )

        response = self.client.post(reverse('account:token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpassword123'
        }, format='json')
        self.access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_change_password_success(self):
        data = {
            'old_password': 'testpassword123',
            'new_password': 'newpass123',
            'new_password2': 'newpass123',
        }
        response = self.client.patch(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_login = self.client.post(reverse('account:token_obtain_pair'), {
            'username': 'testuser',
            'password': 'newpass123'
        })
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertIn('access', response_login.data)

    def test_change_pass_wrong_oldpass(self):
        response = self.client.patch(self.change_password_url, {
            'old_password': 'wrongpassword',
            'new_password': 'newpass123',
            'new_password2': 'newpass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

class LogOutTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse('account:user_logout')
        self.login_url = reverse('account:token_obtain_pair')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='testpass123' 
        )
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpass123'}, format='json')
        self.access = response.data['access']
        self.refresh = response.data['refresh']

        self.client.credentials(HTTP_AUTHOIZATION='Bearer ' + self.access)

    def test_logout_success(self):
        response = self.client.post(self.logout_url, {'refresh': self.refresh}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)