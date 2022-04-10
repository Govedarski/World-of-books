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

