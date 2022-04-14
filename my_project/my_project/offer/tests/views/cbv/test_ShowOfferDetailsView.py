from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book
from my_project.offer.models import Offer

UserModel = get_user_model()


class ShowOfferDetailsViewTests(django_test.TestCase):
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
        cls.USER = user
        cls.SECOND_USER = second_user
        cls._create_book(user)
        cls._create_book(second_user)
        cls._create_offer(
            sender=user,
            recipient=second_user,
            sender_books=Book.objects.get(owner=user),
            recipient_books=Book.objects.get(owner=second_user),
        )
        offer = Offer.objects.first()
        cls.TARGET_URL = reverse('show_offer_details',
                                 kwargs={"pk": offer.pk})
        cls.OFFER = offer

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    @staticmethod
    def _create_book(owner):
        Book(
            title='title',
            author='author',
            owner=owner,
        ).save()

    @staticmethod
    def _create_offer(sender, recipient, sender_books, recipient_books):
        '''create notification too'''
        Offer(
            sender=sender,
            recipient=recipient,
        ).save()
        offer = Offer.objects.first()
        offer.sender_books.add(sender_books)
        offer.recipient_books.add(recipient_books)
        offer.full_clean()
        offer.save()

    def test_show_offer__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)

        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_show_offer__when_user_is_not_sender_nor_recipient__expect_status_code_403(
            self):
        extra_credentials = {
            'username': 'extra_User',
            'email': 'extra_user@email.com',
            'password': 'testp@ss',
        }
        UserModel.objects.create_user(**extra_credentials)

        self._login(**extra_credentials)

        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)

    def test_show_offer_context__when_user_is_sender__expect_right_context(self):
        self._login(**self.CREDENTIALS)

        response = self.client.get(self.TARGET_URL)

        result_is_my_offer = response.context.get('is_my_offer')
        expected_my_books = self.OFFER.sender_books.all()
        result_my_books = response.context.get('my_books')
        expected_others_books = self.OFFER.recipient_books.all()
        result_others_books = response.context.get('others_books')

        self.assertTrue(result_is_my_offer)
        self.assertQuerysetEqual(expected_my_books, result_my_books)
        self.assertQuerysetEqual(expected_others_books, result_others_books)

    def test_show_offer_context__when_user_is_recipient__expect_right_context(self):
        self._login(**self.SECOND_CREDENTIALS)

        response = self.client.get(self.TARGET_URL)

        result_is_my_offer = response.context.get('is_my_offer')
        expected_my_books = self.OFFER.recipient_books.all()
        result_my_books = response.context.get('my_books')
        expected_others_books = self.OFFER.sender_books.all()
        result_others_books = response.context.get('others_books')

        self.assertFalse(result_is_my_offer)
        self.assertQuerysetEqual(expected_my_books, result_my_books)
        self.assertQuerysetEqual(expected_others_books, result_others_books)
