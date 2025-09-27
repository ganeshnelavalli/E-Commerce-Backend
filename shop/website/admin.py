from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Create a default admin if none exists
@receiver(post_migrate)
def ensure_default_admin(sender, **kwargs):
    if sender.name != 'website':
        return
    if not User.objects.filter(is_staff=True).exists():
        User.objects.create_superuser(
            username='admin', email='admin@example.com', password='admin123'
        )
from website.models import Products
admin.site.register(Products)
# Register your models here.
