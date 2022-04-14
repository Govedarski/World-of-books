from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.common.models import Notification
from my_project.library.models import Book
from my_project.offer.forms import NegotiateOfferForm
from my_project.offer.models import Offer

UserModel = get_user_model()


class NegotiateOfferViewTests(django_test.TestCase):
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
        cls.TARGET_URL = reverse('negotiate_offer',
                                 kwargs={"pk": offer.pk})
        cls.INITIAL_OFFER = offer

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

    def test_negotiate_offer__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)

        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_negotiate_offer__when_user_has_not_been_part_of_previous_offer__expect_status_code_403(
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

    def test_negotiate_offer_get__when_user_try_to_negotiate_his_own_offer__expect_status_code_403(
            self):
        self._login(**self.CREDENTIALS)
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)

    def test_negotiate_offer_get__when_user_is_valid__expect_right_instance_and_reversed_initial_data(self):
        self._login(**self.SECOND_CREDENTIALS)

        response = self.client.get(self.TARGET_URL)
        form = response.context.get('form')

        self.assertEqual(self.INITIAL_OFFER, form.instance)
        self.assertListEqual(list(self.INITIAL_OFFER.sender_books.all()), form.initial.get('recipient_books'))
        self.assertListEqual(list(self.INITIAL_OFFER.recipient_books.all()), form.initial.get('sender_books'))

    def test_negotiate_offer_post__when_user_is_valid_and_dif_book__expect_deactivated_old_offer_create_new_and_notfs(
            self):
        self._login(**self.SECOND_CREDENTIALS)
        self._create_book(self.SECOND_USER)
        new_book = Book.objects.order_by('pk').last()
        init_recipient_books = [b for b in self.INITIAL_OFFER.sender_books.all()]

        post_data = {'sender_books': [new_book.pk],
                     'recipient_books': [b.pk for b in init_recipient_books],
                     }

        response = self.client.post(self.TARGET_URL,
                                    data=post_data)

        old_offer = Offer.objects.get(pk=self.INITIAL_OFFER.pk)
        counter_offer = Offer.objects.order_by('pk').last()

        self.assertEqual(2, Offer.objects.count())
        self.assertFalse(old_offer.is_active)
        self.assertFalse(old_offer.is_accept)
        self.assertEqual(self.INITIAL_OFFER.sender, old_offer.sender, counter_offer.recipient)
        self.assertEqual(self.INITIAL_OFFER.recipient, old_offer.recipient, counter_offer.sender)
        self.assertEqual(old_offer, counter_offer.previous_offer)
        self.assertTrue(counter_offer.is_active)
        self.assertFalse(counter_offer.is_accept)
        result_co_sender_books = [b for b in counter_offer.sender_books.all()]
        result_co_recipient_books = [b for b in counter_offer.recipient_books.all()]
        self.assertListEqual([new_book], result_co_sender_books)
        self.assertListEqual(init_recipient_books, result_co_recipient_books)

        self.assertEqual(3, Notification.objects.count())
        create_offer_notf, reject_offer_notf, negotiate_offer_notf = Notification.objects.order_by('pk').all()
        self.assertTrue(create_offer_notf.is_answered)
        self.assertTrue(reject_offer_notf.is_answered)
        self.assertFalse(negotiate_offer_notf.is_answered)
        self.assertEqual(self.USER, create_offer_notf.sender)
        self.assertEqual(self.SECOND_USER, create_offer_notf.recipient)
        self.assertEqual(self.SECOND_USER, reject_offer_notf.sender)
        self.assertEqual(self.USER, reject_offer_notf.recipient)
        self.assertEqual(self.SECOND_USER, negotiate_offer_notf.sender)
        self.assertEqual(self.USER, negotiate_offer_notf.recipient)
        self.assertEqual(self.USER, negotiate_offer_notf.recipient)
        self.assertEqual(old_offer, create_offer_notf.offer)
        self.assertEqual(old_offer, reject_offer_notf.offer)
        self.assertEqual(counter_offer, negotiate_offer_notf.offer)

    def test_negotiate_offer_post__when_user_is_valid_and_no_change_books__expect_old_offer_don_not_change_no_new_offer_correct_error(
            self):
        self._login(**self.SECOND_CREDENTIALS)
        init_sender_books = [b for b in self.INITIAL_OFFER.recipient_books.all()]
        init_recipient_books = [b for b in self.INITIAL_OFFER.sender_books.all()]

        post_data = {'sender_books': [b.pk for b in init_sender_books],
                     'recipient_books': [b.pk for b in init_recipient_books],
                     }

        response = self.client.post(self.TARGET_URL,
                                    data=post_data)

        old_offer = Offer.objects.get(pk=self.INITIAL_OFFER.pk)

        self.assertEqual(1, Offer.objects.count())
        self.assertTrue(old_offer.is_active)
        form = response.context.get('form')
        error = form.errors.get('__all__')[0]
        self.assertEqual(NegotiateOfferForm.NOT_CHANGE_ERROR,error)
