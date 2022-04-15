from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse_lazy

from my_project.library.models import Book
from my_project.offer.models import Offer


class NotificationQueryset(QuerySet):
    def unread(self):
        return self.filter(is_read=False)


class Notification(models.Model):
    objects = NotificationQueryset.as_manager()

    sender = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name='sender_messages',
    )
    recipient = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name='receiver_messages',
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )

    offer = models.ForeignKey(
        Offer,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )

    massage = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    is_answered = models.BooleanField(
        default=False
    )

    received_date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-received_date']

    def __str__(self):
        return self.massage

    def get_absolute_url(self):
        return reverse_lazy('notification_details', kwargs={"pk": self.pk})

    def answer(self):
        self.is_answered = True
        self.save()

    @classmethod
    def create_notification(cls, massage, **kwargs):
        kwargs.update({'massage': massage})
        notf = cls(**kwargs)
        notf.full_clean()
        notf.save()
        return notf

    @classmethod
    def create_notification_for_offer_made(cls, kwargs):
        offer = kwargs.get('offer')
        sender = kwargs.get('sender')
        massage = f'{sender} makes {offer} to you'
        return cls.create_notification(massage, **kwargs)

    @classmethod
    def create_notification_for_offer_offer_reply(cls, kwargs):
        offer = kwargs.get('offer')
        sender = kwargs.get('sender')
        massage = f"Your {offer} to {sender} was rejected or canceled"
        if offer.is_accept:
            massage = f"{sender} accepted your {offer}"

        kwargs.update({'is_answered': True})
        return cls.create_notification(massage, **kwargs)


    @classmethod
    def create_notification_for_book(cls, sender, recipient, book):
        pass

    @classmethod
    def create_notification_for_like_or_dislike(cls, sender, recipient, book):
        pass


