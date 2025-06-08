from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('api/v1/products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('api/v1/products/<int:id>/', views.ProductDetailView.as_view(), name='product-detail'),
]