from django.db.models import signals
from django.dispatch import receiver

from my_project.common.models import Notification
from my_project.offer.models import Offer


@receiver(signals.post_save, sender=Offer)
def send_notification_on_offer_made(instance, created, **kwargs):
    if not created:
        return None

    Notification.create_notification_for_offer_made(
        kwargs={
            'sender': instance.sender,
            'recipient': instance.recipient,
            'offer': instance,
        }
    )


@receiver(signals.pre_save, sender=Offer)
def notification_on_offer_reply(instance, **kwargs):
    if instance.is_active or not instance.pk:
        return None
    previous = Offer.objects.get(id=instance.id)
    if previous.is_active == instance.is_active:
        return None

    notification = Notification.objects.get(offer=instance)
    notification.answer()

    Notification.create_notification_for_offer_offer_reply(
        kwargs={
            'sender': instance.recipient,
            'recipient': instance.sender,
            'offer': instance,
        }
    )
