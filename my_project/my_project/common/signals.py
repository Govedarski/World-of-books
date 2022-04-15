from django.contrib.auth import get_user_model
from django.db.models import signals
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from my_project.common.models import Notification
from my_project.library.models import Book
from my_project.offer.models import Offer

UserModel = get_user_model()


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


@receiver(m2m_changed, sender=Book.likes.through)
def notification_on_like_dislike(instance, action, pk_set, **kwargs):
    if not instance.owner or not pk_set:
        return
    signal, signal_action = action.split('_')
    if signal == 'post':
        like_action = 'like' if signal_action == 'add' else 'dislike'
        sender_pk = list(pk_set)[0]
        sender = UserModel.objects.get(pk=sender_pk)

        Notification.create_notification_for_like_or_dislike(
            action=like_action,
            kwargs={'sender': sender,
                    'recipient': instance.owner,
                    'book': instance,
                    })
