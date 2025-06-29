from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import User


@receiver(post_delete, sender=User)
def clear_user_cache(sender, instance, **kwargs):
    cache_key = f"user_auth_{instance.username}"
    cache.delete(cache_key)
