from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.common.models import Notification
from my_project.library.models import Book, Category

UserModel = get_user_model()


class LikeBookViewTest(django_test.TestCase):
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
        book = cls._create_book(user)
        cls.USER = user
        cls.SECOND_USER = second_user
        cls.BOOK = book
        cls.TARGET_URL = reverse('like_book',
                                 kwargs={'pk': book.pk})

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
        return Book.objects.create(
            title=f"Test title",
            author=f"Test author",
            owner=owner
        )

    def test_like_book_view__when_like_book_with_next__expect_add_like_create_notf_and_redirect_to_next(self):
        back_url = reverse('book_details',
                           kwargs={'pk': self.BOOK.pk})
        target_url = f"{self.TARGET_URL}?back={back_url}"
        self._login(**self.SECOND_CREDENTIALS)

        response = self.client.get(target_url)
        result_book = Book.objects.get(pk=self.BOOK.pk)
        result_notf = Notification.objects.last()

        self.assertEqual(1, result_book.likes_count)
        self.assertEqual(self.SECOND_USER, result_notf.sender)
        self.assertEqual(self.USER, result_notf.recipient)
        self.assertEqual(self.BOOK, result_notf.book)
        self.assertTrue(result_notf.is_answered)
        self.assertFalse(result_notf.is_read)
        self.assertRedirects(response, back_url, status_code=302, target_status_code=200)

    def test_like_book_view__when_like_liked_book__expect__reduce_like_and_notf(self):
        book = self.BOOK
        book.likes.add(self.SECOND_USER)
        book.save()
        self._login(**self.SECOND_CREDENTIALS)

        self.client.get(self.TARGET_URL)
        result_book = Book.objects.get(pk=self.BOOK.pk)
        result_notf = Notification.objects.last()

        self.assertEqual(0, result_book.likes_count)
        self.assertEqual(self.SECOND_USER, result_notf.sender)
        self.assertEqual(self.USER, result_notf.recipient)
        self.assertEqual(self.BOOK, result_notf.book)
        self.assertTrue(result_notf.is_answered)
        self.assertFalse(result_notf.is_read)

    def test_like_book_view__when_like_not_existing_book__expect__status_code_404(self):
        self._login(**self.SECOND_CREDENTIALS)
        target_url = reverse('like_book',
                             kwargs={'pk': 9999})

        response = self.client.get(target_url)
        self.assertEqual(404, response.status_code)

    def test_like_book_view__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_like_book_view__when_user_try_to_like_his_own_book__expect_status_code_403(self):
        self._login()
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)
