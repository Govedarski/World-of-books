from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book
from my_project.library.views import ShowBooksDashboardView, ShowBooksOnAWayView

UserModel = get_user_model()


class ShowBooksOnAWayViewTest(django_test.TestCase):
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
        cls.USER = user
        cls.SECOND_USER = second_user
        cls._create_books(5, user)
        cls.TARGET_URL = reverse('show_books_on_a_way')

    @staticmethod
    def _create_books(number, owner):
        for i in range(number):
            Book.objects.create(
                title=f"Test title",
                author=f"Test author",
                next_owner=owner,
            )

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    def test_show_books_on_a_way_when_user_have_books_on_a_way__expect_right_context_and_to_show_books(self):
        self._create_books(5, self.SECOND_USER)
        self._login()
        expected_books_to_show = Book.objects.filter(next_owner=self.USER)

        response = self.client.get(self.TARGET_URL)

        self.assertEqual(ShowBooksOnAWayView.TITLE, response.context.get('title'))
        self.assertEqual(self.USER, response.context.get('owner'))
        self.assertQuerysetEqual(expected_books_to_show,
                                 response.context.get(ShowBooksOnAWayView.context_object_name))

    def test_show_books_on_a_way_when_user_have_no_books_on_a_way__expect_right_context_no_book_to_show(self):
        self._login(**self.SECOND_CREDENTIALS)

        response = self.client.get(self.TARGET_URL)

        self.assertEqual(ShowBooksOnAWayView.TITLE, response.context.get('title'))
        self.assertEqual(self.SECOND_USER, response.context.get('owner'))
        self.assertFalse(response.context.get(ShowBooksOnAWayView.context_object_name))

    def test_show_book_on_a_way__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
