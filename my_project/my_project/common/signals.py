from django.db.models import signals
from django.dispatch import receiver

from my_project.accounts.models import Profile
from my_project.common.models import Notification
from my_project.offer.models import Offer


@receiver(signals.post_save, sender=Offer)
def answer_notification_on_offer_reply(instance, **kwargs):
    if instance.is_active:
        return None

    notification = Notification.objects.get(offer=instance)
    notification.is_answered = True
    notification.save()

