from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book

UserModel = get_user_model()


class SetupCreateOfferViewTests(django_test.TestCase):
    CREDENTIALS = {
        'username': 'User',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }

    SECOND_CREDENTIALS = {
        'username': 'Second_User',
        'email': 'Second_user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserModel.objects.create_user(**cls.CREDENTIALS)
        second_user = UserModel.objects.create_user(**cls.SECOND_CREDENTIALS)
        cls._create_book(second_user)
        wanted_book = Book.objects.first()
        cls.TARGET_URL = reverse('create_offer',
                                 kwargs={'pk': wanted_book.pk})
        cls.USER = user
        cls.WANTED_BOOK = wanted_book
        cls.SECOND_USER = second_user

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    @staticmethod
    def _create_book( owner):
        Book(
            title='title',
            author='author',
            owner=owner,
        ).save()

    def _set_user_cf(self, user=None):
        cf = self.USER.contactform
        if user:
            cf = user.contactform
        cf.city = "test"
        cf.address = "test"
        cf.save()
