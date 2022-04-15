from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.common.models import Notification
from my_project.library.models import Book, Category

UserModel = get_user_model()


class RejectDeleteBookViewTest(django_test.TestCase):
    CREDENTIALS = {
        'username': 'user',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }
    SECOND_CREDENTIALS = {
        'username': 'second_user',
        'email': 'second_user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserModel.objects.create_user(**cls.CREDENTIALS)
        second_user = UserModel.objects.create_user(**cls.SECOND_CREDENTIALS)
        book = Book.objects.create(
            title=f"Test title",
            author=f"Test author",
        )
        cls.USER = user
        cls.SECOND_USER = second_user
        cls.BOOK = book
        notf = Notification.create_notification_for_offer_made(
            {'sender': user,
             'recipient': second_user,
             'book': book})
        cls.NOTIFICATION = notf
        cls.TARGET_URL = reverse('reject_delete_book',
                                 kwargs={'pk': notf.pk})

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    def test_reject_d_book_view__when_valid_expect_book_not_change_owner_create_notf_and_redirect_to_next(self):
        self._login(**self.SECOND_CREDENTIALS)
        response = self.client.get(self.TARGET_URL)

        result_book = Book.objects.get(pk=self.BOOK.pk)
        result_notf = Notification.objects.get(pk=self.NOTIFICATION.pk)

        self.assertIsNone(result_book.next_owner)
        self.assertIsNone(result_book.previous_owner)
        self.assertTrue(result_notf.is_answered)
        self.assertRedirects(response, reverse('show_notifications'))

    def test_reject_d_book_view__when_notf_do_not_have_book__expect__status_code_404(self):
        notf_without_book = Notification.create_notification_for_offer_made(
            {'sender': self.USER,
             'recipient': self.SECOND_USER,
             }
        )

        self._login(**self.SECOND_CREDENTIALS)
        target_url = reverse('reject_delete_book',
                             kwargs={'pk': notf_without_book.pk})

        response = self.client.get(target_url)
        self.assertEqual(404, response.status_code)

    def test_reject_d_book_view__when_notf_do_not_exist__expect__status_code_404(self):
        self._login(**self.SECOND_CREDENTIALS)
        target_url = reverse('reject_delete_book',
                             kwargs={'pk': 9999})

        response = self.client.get(target_url)
        self.assertEqual(404, response.status_code)

    def test_reject_d_book_view__when_notf_is_answered_already__expect__status_code_403(self):
        answered_notf = Notification.create_notification_for_offer_made(
            {'sender': self.USER,
             'recipient': self.SECOND_USER,
             'book': self.BOOK,
             'is_answered': True}
        )

        self._login(**self.SECOND_CREDENTIALS)
        target_url = reverse('reject_delete_book',
                             kwargs={'pk': answered_notf.pk})

        response = self.client.get(target_url)
        self.assertEqual(403, response.status_code)

    def test_reject_d_book_view__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_reject_d_book_view__when_user_is_not_recipient__expect_status_code_403(self):
        self._login()
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)
