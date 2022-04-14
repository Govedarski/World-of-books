from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.common.models import Notification
from my_project.library.models import Book
from my_project.offer.models import Offer
from my_project.offer.views import ShowOffersView

UserModel = get_user_model()


class AcceptOfferViewTests(django_test.TestCase):
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
        cls._create_offers(user, second_user)
        offer = Offer.objects.first()
        cls.OFFER = offer
        cls.TARGET_URL = reverse('accept_offer',
                                 kwargs={'pk': offer.pk})

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    @staticmethod
    def _create_offers(sender, recipient):
        '''Create Notification'''
        Offer(
            sender=sender,
            recipient=recipient,
        ).save()

    @staticmethod
    def _create_books(number, owner):
        for _ in range(number):
            Book(
                author='test author',
                title='test author',
                owner=owner,
            ).save()

    def test_accept_offer__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_accept_offer__when_user_is_not_recipient__expect_status_code_403(self):
        self._login(**self.CREDENTIALS)
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)

    def test_accept_offer__when_user_is_recipient_and_book_valid__inactive_offer_book_change_owners_and_notf_create(
            self):
        self._create_books(5, self.USER)
        self._create_books(5, self.SECOND_USER)
        sender_books_in_offer = Book.objects.filter(owner=self.USER)[:3]
        recipient_books_in_offer = Book.objects.filter(owner=self.SECOND_USER)[:3]
        self.OFFER.sender_books.set(book.pk for book in sender_books_in_offer)
        self.OFFER.recipient_books.set(book.pk for book in recipient_books_in_offer)
        self.OFFER.save()

        self._login(**self.SECOND_CREDENTIALS)
        response = self.client.get(self.TARGET_URL)

        result_offer = Offer.objects.get(pk=self.OFFER.pk)
        result_sender_books = result_offer.sender_books.all()
        result_recipient_books = result_offer.recipient_books.all()
        result_notf = Notification.objects.order_by('pk').last()
        redirect_url = reverse('show_offer_details',
                               kwargs={'pk': self.OFFER.pk})

        self.assertFalse(result_offer.is_active)
        self.assertTrue(result_offer.is_accept)

        self.assertQuerysetEqual(sender_books_in_offer, result_sender_books)
        self.assertQuerysetEqual(recipient_books_in_offer, result_recipient_books)
        self.assertFalse(any(b.owner for b in result_sender_books))
        self.assertFalse(any(b.owner for b in result_recipient_books))
        self.assertTrue(all(b.next_owner == self.SECOND_USER for b in result_sender_books))
        self.assertTrue(all(b.next_owner == self.USER for b in result_recipient_books))
        self.assertTrue(all(b.previous_owner == self.USER for b in result_sender_books))
        self.assertTrue(all(b.previous_owner == self.SECOND_USER for b in result_recipient_books))
        self.assertEqual(len(sender_books_in_offer), sum(b.ex_owners.count() for b in result_sender_books))
        self.assertEqual(len(result_recipient_books), sum(b.ex_owners.count() for b in result_recipient_books))

        self.assertEqual(2, Notification.objects.count())
        self.assertTrue(result_notf.is_answered)
        self.assertEqual(self.USER, result_notf.recipient)
        self.assertEqual(self.SECOND_USER, result_notf.sender)
        self.assertEqual(self.OFFER, result_notf.offer)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_accept_offer__when_user_is_recipient_and_book_invalid__expect_redirect_book_not_change(self):
        self._create_books(5, self.USER)
        self._create_books(5, self.SECOND_USER)
        sender_books_in_offer = Book.objects.filter(owner=self.USER)[:3]
        recipient_books_in_offer = Book.objects.filter(owner=self.SECOND_USER)[:3]
        self.OFFER.sender_books.set(book.pk for book in sender_books_in_offer)
        self.OFFER.recipient_books.set(book.pk for book in recipient_books_in_offer)
        invalid_book = Book.objects.filter(owner=self.SECOND_USER)[0]
        invalid_offer = self.OFFER
        invalid_offer.sender_books.add(invalid_book)
        invalid_offer.save()

        self._login(**self.SECOND_CREDENTIALS)
        response = self.client.get(self.TARGET_URL)

        result_offer = Offer.objects.get(pk=self.OFFER.pk)
        result_sender_books = result_offer.sender_books.all()
        result_recipient_books = result_offer.recipient_books.all()


        self.assertFalse(result_offer.is_active)
        self.assertFalse(result_offer.is_accept)

        self.assertTrue(all(b.owner for b in result_recipient_books))
        self.assertTrue(all(b.owner for b in result_recipient_books))
        self.assertFalse(any(b.next_owner for b in result_sender_books))
        self.assertFalse(any(b.next_owner for b in result_recipient_books))
        self.assertFalse(any(b.previous_owner for b in result_sender_books))
        self.assertFalse(any(b.previous_owner for b in result_recipient_books))
        self.assertEqual(0, sum(b.ex_owners.count() for b in result_sender_books))
        self.assertEqual(0, sum(b.ex_owners.count() for b in result_recipient_books))

        self.assertTemplateUsed(response, 'offer/inactive_offer.html')