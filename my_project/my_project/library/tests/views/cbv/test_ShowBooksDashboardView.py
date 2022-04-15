from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book
from my_project.library.views import ShowBooksDashboardView

UserModel = get_user_model()


class ShowBooksDashboardViewTest(django_test.TestCase):
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
        cls._create_books(5, second_user)


    @staticmethod
    def _create_books(number, owner):
        for i in range(number):
            Book.objects.create(
                title=f"Test title",
                author=f"Test author",
                owner=owner,
            )

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    def test_show_book_dashboard_when_user_with_ulr_pk_do_not_exist__expect_status_code_404(self):
        target_url = reverse('show_books_dashboard',
                             kwargs={'pk': 99999})
        response = self.client.get(target_url)

        self.assertEqual(404, response.status_code)

    def test_show_book_dashboard_when_user_visit_his_own_dashboard__expect_right_context_and_query(self):
        target_url = reverse('show_books_dashboard',
                             kwargs={'pk': self.USER.pk})
        self._login()
        response = self.client.get(target_url)

        expected_books_to_show = Book.objects.filter(owner=self.USER)
        self.assertEqual('My books', response.context.get('title'))
        self.assertEqual(self.USER, response.context.get('owner'))
        self.assertQuerysetEqual(expected_books_to_show,
                                 response.context.get(ShowBooksDashboardView.context_object_name))

    def test_show_book_dashboard_when_user_visit_other_dashboard__expect_right_context_and_query(self):
        target_url = reverse('show_books_dashboard',
                             kwargs={'pk': self.SECOND_USER.pk})
        self._login()
        response = self.client.get(target_url)

        expected_books_to_show = Book.objects.filter(owner=self.SECOND_USER)

        self.assertEqual(f"{self.SECOND_USER.username}'s book", response.context.get('title'))
        self.assertEqual(self.SECOND_USER, response.context.get('owner'))
        self.assertQuerysetEqual(expected_books_to_show,
                                 response.context.get(ShowBooksDashboardView.context_object_name))
