from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.db.models.functions import Lower

from my_project.common.helpers import custom_validators


class Category(models.Model):
    NAME_MAX_LENGTH = 32

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    TITTLE_MAX_LENGTH = 64
    AUTHOR_MAX_LENGTH = 64
    UPLOAD_PICTURE_MAX_SIZE_IN_MB = 2

    title = models.CharField(
        max_length=TITTLE_MAX_LENGTH,
    )

    author = models.CharField(
        max_length=AUTHOR_MAX_LENGTH,
    )

    category = models.ForeignKey(
        to=Category,
        null=True,
        blank=True,
        default='',
        on_delete=models.SET_DEFAULT,
    )

    image = models.ImageField(
        upload_to='books',
        null=True,
        blank=True,
        validators=[
            custom_validators.MaxSizeInMBValidator(UPLOAD_PICTURE_MAX_SIZE_IN_MB)
        ],
    )

    owner = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='own_books',
    )

    ex_owners = models.ManyToManyField(
        to=get_user_model(),
        related_name='ex_books',
        blank=True,

    )

    previous_owner = models.ForeignKey(
        to=get_user_model(),
        related_name='books_to_send',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    next_owner = models.ForeignKey(
        to=get_user_model(),
        related_name='book_on_a_way',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    likes = models.ManyToManyField(
        to=get_user_model(),
        related_name='liked_books',
        blank=True,
    )

    is_available = models.BooleanField(
        default=True,
    )

    @property
    def likes_count(self):
        return len(self.likes.all())

    def __str__(self):
        return f'"{self.title}" by {self.author} OWNER:{self.owner}'

    class Meta:
        ordering = [Lower('title')]
