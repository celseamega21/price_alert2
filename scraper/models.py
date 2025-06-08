from django.db import models

class ScraperEngine(models.Model):
    engine_name = models.CharField(max_length=100, unique=True)
    task_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField()
    ip_engine = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)