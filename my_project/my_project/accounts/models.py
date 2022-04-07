from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower
from cloudinary.models import CloudinaryField
from my_project.accounts.managers import MyUserManager
from my_project.common.helpers import custom_validators


class WorldOfBooksUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_MAX_LENGTH = 32
    USERNAME_VALIDATION_ERROR_MASSAGE = 'This username is already used by another user'
    EMAIL_VALIDATION_ERROR_MASSAGE = 'This email is already used by another user'

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
    )

    email = models.EmailField(
        unique=True,
    )

    date_joined = models.DateTimeField(
        auto_now_add=True,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    objects = MyUserManager()

    @property
    def nickname(self):
        return self.username if self.is_active else 'archived user'

    def clean(self):
        if WorldOfBooksUser.objects.filter(email=self.username).exists():
            raise ValidationError({'username': self.USERNAME_VALIDATION_ERROR_MASSAGE})
        if WorldOfBooksUser.objects.filter(username=self.email).exists():
            raise ValidationError({'email': self.EMAIL_VALIDATION_ERROR_MASSAGE})
        super().clean()

    class Meta:
        ordering = [Lower('username')]


class Profile(models.Model):
    FIRST_NAME_MAX_LENGTH = 32
    FIRST_NAME_MIN_LENGTH = 2
    LAST_NAME_MAX_LENGTH = 32
    LAST_NAME_MIN_LENGTH = 2
    UPLOAD_PICTURE_MAX_SIZE_IN_MB = 2
    NATIONALITY_MAX_LENGTH = 32

    class GenderChoices(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        DO_NOT_SHOW = "Do not show", "Do not show"

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True,
    )

    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        null=True,
        blank=True,
        validators=[
            validators.MinLengthValidator(FIRST_NAME_MIN_LENGTH),
            custom_validators.OnlyLetterValidator(),
        ],
    )

    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        null=True,
        blank=True,
        validators=[
            validators.MinLengthValidator(LAST_NAME_MIN_LENGTH),
            custom_validators.OnlyLetterValidator(),
        ],
    )

    gender = models.CharField(
        max_length=max(len(x.value) for x in GenderChoices),
        choices=GenderChoices.choices,
        default=GenderChoices.DO_NOT_SHOW,
    )

    picture_upload = CloudinaryField(
        "Image",
        null=True,
        blank=True,
        transformation={"quality": "auto:eco"},
        overwrite=True,
    )

    picture_url = models.URLField(null=True,
                                  blank=True
                                  )

    nationality = models.CharField(
        max_length=NATIONALITY_MAX_LENGTH,
        null=True,
        blank=True,
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    @property
    def full_name(self):
        first_name = f'{self.first_name} ' if self.first_name else ''
        last_name = self.last_name if self.last_name else ''
        return first_name + last_name

    @property
    def age(self):
        if not self.date_of_birth:
            return ""
        today = date.today()
        age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age


class ContactForm(models.Model):
    CITY_MAX_LENGTH = 32
    ADDRESS_MAX_LENGTH = 64
    PHONE_NUMBER_MIN_LENGTH = 9
    PHONE_NUMBER_MAX_LENGTH = 9

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True)

    city = models.CharField(
        max_length=CITY_MAX_LENGTH,
        null=True,
        blank=True,
    )

    address = models.CharField(
        max_length=ADDRESS_MAX_LENGTH,
        null=True,
        blank=True,
    )

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_MAX_LENGTH,
        null=True,
        blank=True,
        validators=[
            validators.MinLengthValidator(PHONE_NUMBER_MIN_LENGTH),
            custom_validators.OnlyNumberValidator()
        ]
    )

    @property
    def is_completed(self):
        return all([self.city, self.address])