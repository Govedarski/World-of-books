from django.contrib.auth import get_user_model
from django.db import models

from my_project.library.models import Book


class Notification(models.Model):
    class TypeChoices(models.TextChoices):
        CHANGE_OWNER = 'Change owner'
        LIKED = 'Liked'
        REVIEWED = 'Reviewed'
        WANTED = 'Wanted'
        OFFERED = 'Offered'
        DEAL = 'Deal'

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
    )

    type = models.CharField(
        max_length=max(len(x.value) for x in TypeChoices),
        choices=TypeChoices.choices,
    )

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
        if self.type == self.TypeChoices.CHANGE_OWNER:
            return f'{self.sender} sent {self.book} to you?'
        elif self.type == self.TypeChoices.LIKED:
            pass
        elif self.type == self.TypeChoices.REVIEWED:
            pass
        elif self.type == self.TypeChoices.WANTED:
            pass
        elif self.type == self.TypeChoices.OFFERED:
            pass
        elif self.type == self.TypeChoices.DEAL:
            pass
