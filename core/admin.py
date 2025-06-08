from django.contrib import admin
from .models import PriceHistory, Product

admin.site.register(PriceHistory)
admin.site.register(Product)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'username', 'url', 'engine', 'last_price', 'created_at')
    list_filter = ('engine', 'user')
    search_fields = ('name', 'username', 'email')

class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'date')
    list_filter = ('product',)
    ordering = ('-date',)