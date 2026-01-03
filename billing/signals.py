from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Subscription, SubscriptionStatus

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    if created:
        Subscription.objects.create(
            user=instance,
            plan=Subscription.FREE,
            status=SubscriptionStatus.ACTIVE,
            max_vehicles=5,
            max_active_vigencias=3
        )