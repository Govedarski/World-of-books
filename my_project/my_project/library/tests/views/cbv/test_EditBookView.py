from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book

UserModel = get_user_model()


class EditBookViewTest(django_test.TestCase):
    CREDENTIALS = {
        'username': 'user',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = UserModel.objects.create_user(**cls.CREDENTIALS)
        book = cls._create_book()

        cls.TARGET_URL = reverse('edit_book',
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
    def _create_book():
        return Book.objects.create(
            title=f"Test title",
            author=f"Test author",
        )

    def test_edit_book__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_edit_book__when_user_is_not_owner_of_the_book__expect_status_code_403(self):
        self._login()
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)
