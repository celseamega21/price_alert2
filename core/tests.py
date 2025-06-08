from rest_framework.test import APITestCase, APIClient
from .models import Product
from django.urls import reverse
from scraper.models import ScraperEngine
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@gmail.com', password='testpass123')
        self.engine = ScraperEngine.objects.create(
            engine_name='Test Engine', task_count=0, active=True, ip_engine='127.0.0.1', port=8080
        )
        self.product = Product.objects.create(
            user=self.user,
            email='test@example.com',
            name='Test Product',
            url='http://example.com/product',
            last_price='10000'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    @patch('core.views.initial_scrape.delay')
    def test_create_product_success(self, mock_scrape):
        data = {
            'url': 'http://example.com/product',
            'email': 'user@gmail.com'
        }
        response = self.client.post(reverse('core:product-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Product was successfully tracked!")
        self.assertTrue(Product.objects.filter(user=self.user).exists())
        mock_scrape.assert_called_once()

    def test_patch_product_success(self):
        update_data = {'email': 'newemail@gmail.com'}
        response = self.client.patch(reverse('core:product-detail', kwargs={'id': self.product.id}), data=update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newemail@gmail.com')

    def test_delete_product_success(self):
        response = self.client.delete(reverse('core:product-detail', kwargs={'id': self.product.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_get_product_success(self):
        response = self.client.get(reverse('core:product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Test Product')

    def test_unauthenticate_get_product(self):
        client = APIClient()
        response = client.get(reverse('core:product-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)