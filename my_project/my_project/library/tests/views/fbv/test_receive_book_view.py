from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book

UserModel = get_user_model()


class ReceiveBookViewTest(django_test.TestCase):
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
            next_owner=user,
            previous_owner=second_user,
        )
        cls.USER = user
        cls.SECOND_USER = second_user
        cls.BOOK = book

        cls.TARGET_URL = reverse('receive_book',
                                 kwargs={'pk': book.pk})

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    def test_receive_book_book_view__when_valid_book_no_liked_by_user_expect_book_change_owner_and_redirect_to_next(self):
        self._login()

        response = self.client.get(self.TARGET_URL)
        result_book = Book.objects.get(pk=self.BOOK.pk)
        redirect_url = reverse('show_books_dashboard',
                               kwargs={'pk': self.USER.pk})

        self.assertEqual(self.USER, result_book.owner)
        self.assertIsNone(result_book.next_owner)
        self.assertIsNone(result_book.previous_owner)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_receive_book_book_view__when_valid_book_liked_by_user_expect_book_change_owner_like_to_be_deleted_and_redirect_to_next(
            self):
        liked_book = Book.objects.create(
            title=f"Test title",
            author=f"Test author",
            next_owner=self.USER,
            previous_owner=self.SECOND_USER,
        )
        liked_book.likes.add(self.USER)
        liked_book.save()

        self._login()

        target_url = reverse('receive_book',
                             kwargs={'pk': liked_book.pk})
        response = self.client.get(target_url)
        result_book = Book.objects.get(pk=liked_book.pk)
        redirect_url = reverse('show_books_dashboard',
                               kwargs={'pk': self.USER.pk})

        self.assertEqual(0, result_book.likes_count)
        self.assertEqual(self.USER, result_book.owner)
        self.assertIsNone(result_book.next_owner)
        self.assertIsNone(result_book.previous_owner)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_receive_book_view__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_receive_book_view__when_user_is_not_next_owner_expect_status_code_403(self):
        self._login(**self.SECOND_CREDENTIALS)
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)
