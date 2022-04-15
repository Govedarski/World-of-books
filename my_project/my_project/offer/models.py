from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from my_project.library.models import Book

UserModel = get_user_model()
class Offer(models.Model):
    sender = models.ForeignKey(
        UserModel,
        on_delete=models.DO_NOTHING,
        related_name='sender_offer',
    )
    recipient = models.ForeignKey(
        UserModel,
        on_delete=models.DO_NOTHING,
        related_name='receiver_offer',
    )

    sender_books = models.ManyToManyField(
        Book,
        related_name='offered',
    )

    recipient_books = models.ManyToManyField(
        Book,
        related_name='wanted'
    )

    is_accept = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True,
    )

    previous_offer = models.OneToOneField(
        'self',
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name='next_offer',
    )

    received_date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-received_date']

    def __str__(self):
        if self.previous_offer:
            return f'Counter offer №{self.pk}'
        return f'Offer №{self.pk}'
