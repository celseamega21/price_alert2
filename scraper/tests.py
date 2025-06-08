from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from scraper.models import ScraperEngine
from rest_framework import status
from core.models import Product
from django.test import TestCase
from scraper.load_balancer import LoadBalancer

User = get_user_model()

class ProductLoadBalancerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', email='test@gmail.com', password='testpass123')
        self.client = APIClient()
        refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_token.access_token}')
        self.engine = ScraperEngine.objects.create(
            engine_name='Test Engine',
            task_count=0,
            active=True,
            ip_engine='127.0.0.1',
            port=8000
        )

    @patch('core.views.LoadBalancer.get_scraper_engine')
    @patch('core.views.initial_scrape.delay')
    def test_load_balancer(self, mock_scrape, mock_get_engine):
        mock_get_engine.return_value = self.engine
        data = {
            'url': 'http://example.com/product1',
            'email': 'test@gmail.com'
        }
        response = self.client.post(reverse('core:product-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        mock_get_engine.assert_called_once()

        product = Product.objects.get(url='http://example.com/product1')
        self.assertEqual(product.engine, self.engine)

        mock_scrape.asser_called_once_with(product.id)

class LoadBalancerTest(TestCase):
    def setUp(self):
        self.engine1 = ScraperEngine.objects.create(
            engine_name='Engine 1',
            task_count=3,
            active=True,
            ip_engine='127.0.0.1',
            port=8000
        )
        self.engine2 = ScraperEngine.objects.create(
            engine_name='Engine 2',
            task_count=7,
            active=True,
            ip_engine='127.0.0.2',
            port=8001
        )
        self.engine3 = ScraperEngine.objects.create(
            engine_name='Engine 3',
            task_count=10,
            active=False,
            ip_engine='127.0.0.3',
            port=8002
        )

    # returns least task count
    def test_get_engine_active(self):
        selected_engine = LoadBalancer.get_scraper_engine()
        self.assertEqual(selected_engine, self.engine1)

    # returns none if no active
    def test_get_engine_nonactive(self):
        ScraperEngine.objects.all().update(active=False)
        selected_engine = LoadBalancer.get_scraper_engine()
        self.assertIsNone(selected_engine)