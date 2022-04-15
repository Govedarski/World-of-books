from django import test as django_test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse

from my_project.library.models import Book
from my_project.library.views import ShowBooksDashboardView, DetailsBookView

UserModel = get_user_model()


class DetailsBookViewTest(django_test.TestCase):
    CREDENTIALS = {
        'username': 'user',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserModel.objects.create_user(**cls.CREDENTIALS)
        cls.USER = user

    @staticmethod
    def _create_book(owner=None, next_owner=None, previous_owner=None, is_tradable=True):
        return Book.objects.create(
            title=f"Test title",
            author=f"Test author",
            owner=owner,
            next_owner=next_owner,
            previous_owner=previous_owner,
            is_tradable=is_tradable,
        )

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    @staticmethod
    def _adding_permissions(user, *args):
        for perm in args:
            permission = Permission.objects.get(codename=perm)
            user.user_permissions.add(permission)
        user.save()

    def test_details_book__when_regular_user_and_valid_book__expect_right_template_and_book_to_show(self):
        book = self._create_book(owner=self.USER)
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})

        response = self.client.get(target_url)

        self.assertTemplateUsed(response, 'library/book_details.html')
        self.assertEqual(book, response.context.get(DetailsBookView.context_object_name))
        self.assertFalse(response.context.get('can_staff_edit'))

    def test_details_book__when_regular_user_and_deleted_book__expect_status_code_404(self):
        self._login()
        book = self._create_book()
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})

        response = self.client.get(target_url)

        self.assertEqual(404, response.status_code)

    def test_details_book__when_staff_user_with_perm_and_valid_book__expect_right_template_and_book_to_show(self):
        book = self._create_book(owner=self.USER)
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})

        self._adding_permissions(self.USER, 'view_book')
        self._login()

        response = self.client.get(target_url)

        self.assertTemplateUsed(response, 'library/book_details.html')
        self.assertEqual(book, response.context.get(DetailsBookView.context_object_name))
        self.assertTrue(response.context.get('can_staff_edit'))

    def test_details_book__when_staff_user_with_perm_and_deleted_book__expect_right_template_and_book_to_show(self):
        book = self._create_book()
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})

        self._adding_permissions(self.USER, 'view_book')
        self._login(**self.CREDENTIALS)

        response = self.client.get(target_url)

        self.assertTemplateUsed(response, 'library/book_details.html')
        self.assertEqual(book, response.context.get(DetailsBookView.context_object_name))
        self.assertTrue(response.context.get('can_staff_edit'))

    def test_change_tradable__when_user_and_his_book__expect_book_to_change(self):
        book = self._create_book(owner=self.USER)
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})

        self._login()

        response = self.client.post(target_url)

        not_tradable_book = Book.objects.get(pk=book.pk)
        self.assertFalse(not_tradable_book.is_tradable)

        response = self.client.post(target_url)

        tradable_book = Book.objects.get(pk=book.pk)
        self.assertTrue(tradable_book.is_tradable)

    def test_change_tradable__when_user_and_not_his_book__expect_status_code_403(self):
        book = self._create_book(next_owner=self.USER)
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})

        self._login()

        response = self.client.post(target_url)

        self.assertEqual(403, response.status_code)

    def test_change_tradable__when_not_authenticated_user__expect_status_code_403(self):
        book = self._create_book(owner=self.USER)
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})

        response = self.client.post(target_url)

        self.assertEqual(403, response.status_code)

    def test_details_book__when_user_is_next_book_owner__expect_right_template(self):
        second_user = UserModel.objects.create_user(username="second",
                                                    email="second@mail.com",
                                                    password="testp@ss")

        book = self._create_book(next_owner=self.USER,
                                 previous_owner=second_user)
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})
        self._login()

        response = self.client.get(target_url)

        self.assertTemplateUsed(response, 'library/book_to_receive_info.html')

    def test_details_book__when_user_is_previous_book_owner__expect_right_template(self):
        second_user = UserModel.objects.create_user(username="second",
                                                    email="second@mail.com",
                                                    password="testp@ss")

        book = self._create_book(next_owner=second_user,
                                 previous_owner=self.USER, )
        target_url = reverse('book_details',
                             kwargs={'pk': book.pk})
        self._login()

        response = self.client.get(target_url)

        self.assertTemplateUsed(response, 'library/book_to_send_info.html')

    def test_details_book__when_not_existing_book_owner__expect_status_code_404(self):
        target_url = reverse('book_details',
                             kwargs={'pk': 1})

        response = self.client.get(target_url)

        self.assertEqual(404, response.status_code)
