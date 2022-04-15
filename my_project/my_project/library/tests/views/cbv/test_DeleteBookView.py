from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.common.models import Notification
from my_project.library.models import Book, Category

UserModel = get_user_model()


class DeleteBookViewTest(django_test.TestCase):
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
        cls.TARGET_URL = reverse('delete_book',
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

    def test_delete_book_get__when_valid__expect_right_form_user_choices(self):
        self._login(**self.CREDENTIALS)
        expect_choices = [(0, 'nobody')] + [(user.pk, user.username) for user in
                                            UserModel.objects.exclude(pk=self.USER.pk)]
        response = self.client.get(self.TARGET_URL)

        form = response.context.get('form')
        result_choices = form.fields.get('user').choices
        self.assertListEqual(expect_choices, result_choices)

    def test_delete_book_post__when_to_nobody__expect_book_owner_change(self):
        self._login(**self.CREDENTIALS)
        self.client.get(self.TARGET_URL)
        self.client.post(self.TARGET_URL, data={'user': '0'})

        result_book = Book.objects.get(pk=self.BOOK.pk)
        self.assertIsNone(result_book.owner)
        self.assertIsNone(result_book.next_owner)
        self.assertIsNone(result_book.previous_owner)
        self.assertEqual(self.USER, result_book.ex_owners.last())
        self.assertEqual(0, Notification.objects.count())

    def test_delete_book_post__when_to_another_user__expect_book_owner_change_next_owner_set_notf(self):
        self._login(**self.CREDENTIALS)
        self.client.get(self.TARGET_URL)
        self.client.post(self.TARGET_URL, data={'user': self.SECOND_USER.pk})

        result_book = Book.objects.get(pk=self.BOOK.pk)
        result_notf = Notification.objects.get(book=result_book)
        self.assertIsNone(result_book.owner)
        self.assertIsNone(result_book.next_owner)
        self.assertIsNone(result_book.previous_owner)
        self.assertEqual(self.USER, result_book.ex_owners.last())
        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(self.USER, result_notf.sender)
        self.assertEqual(self.SECOND_USER, result_notf.recipient)
        self.assertIsNone(result_notf.offer)
        self.assertFalse(result_notf.is_read)
        self.assertFalse(result_notf.is_answered)

    def test_delete_book__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_delete_book__when_user_is_not_owner_of_the_book__expect_status_code_403(self):
        self._login(**self.SECOND_CREDENTIALS)

        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)
