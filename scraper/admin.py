from django.contrib import admin
from .models import ScraperEngine

admin.site.register(ScraperEngine)

class ScraperEngineAdmin(admin.ModelAdmin):
    list_display = ('engine_name', 'task_count', 'active', 'ip_engine', 'port')
    list_filter = ('active',)