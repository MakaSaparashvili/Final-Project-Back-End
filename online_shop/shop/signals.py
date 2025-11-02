from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import CustomUser, Cart

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile_and_cart(sender, instance, created, **kwargs):
    if created:
        profile = CustomUser.objects.create(user=instance)
        Cart.objects.create(user=profile)

