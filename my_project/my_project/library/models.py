from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
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

    available = models.BooleanField(
        default=True,
    )

    owner = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'"{self.title}" by {self.author}'



    class Meta:
        ordering = ['title']
