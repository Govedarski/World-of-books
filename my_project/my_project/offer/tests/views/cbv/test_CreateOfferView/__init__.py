from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book

UserModel = get_user_model()


class RegisterUserViewTests(django_test.TestCase):
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
        cls._create_book(
            title="wanted book",
            author="wanted author",
            owner=second_user
        )
        wanted_book = Book.objects.first()
        cls.TARGET_URL = reverse('create_offer',
                                 kwargs={'pk': wanted_book.pk})
        cls.USER = user
        cls.WANTED_BOOK = wanted_book
        cls.SECOND_USER = second_user

    def _login(self):
        self.client.login(
            username=self.CREDENTIALS.get('username'),
            password=self.CREDENTIALS.get('password'),
        )

    @staticmethod
    def _create_book(title, author, owner):
        Book(
            title=title,
            author=author,
            owner=owner,
        ).save()

    def _set_user_cf(self):
        cf = self.USER.contactform
        cf.city = "test"
        cf.address = "test"
        cf.save()

    def test_create_offer_get__when_one_on_one_books__expect_right_initial(self):
        self._create_book(
            title='Offered book',
            author='Offered author',
            owner=self.USER
        )
        self._set_user_cf()
        self._login()

        response = self.client.get(self.TARGET_URL)

        form = response.context.get('form')
        expected_init_sender_books = Book.objects.filter(owner=self.USER)
        expected_init_recipient_books = Book.objects.filter(owner=self.SECOND_USER).exclude(pk=self.WANTED_BOOK.pk)
        result_init_sender_books = form.fields.get('sender_books').queryset.all()
        result_init_recipient_books = form.fields.get('recipient_books').queryset.all()

        self.assertEqual(self.USER, form.initial.get('sender'))
        self.assertEqual(self.SECOND_USER, form.initial.get('recipient'))
        self.assertQuerysetEqual(expected_init_sender_books, result_init_sender_books)
        self.assertQuerysetEqual(expected_init_recipient_books, result_init_recipient_books)

    def test_create_offer_get__when_one_on_many_books__expect_right_initial(self):
        self._create_book(
            title='Offered book',
            author='Offered author',
            owner=self.USER
        )
        self._create_book(
            title='Offered book',
            author='Offered author',
            owner=self.SECOND_USER
        )

        self._set_user_cf()
        self._login()

        response = self.client.get(self.TARGET_URL)

        form = response.context.get('form')
        expected_init_sender_books = Book.objects.filter(owner=self.USER)
        expected_init_recipient_books = Book.objects.filter(owner=self.SECOND_USER).exclude(pk=self.WANTED_BOOK.pk)
        result_init_sender_books = form.fields.get('sender_books').queryset.all()
        result_init_recipient_books = form.fields.get('recipient_books').queryset.all()

        self.assertEqual(self.USER, form.initial.get('sender'))
        self.assertEqual(self.SECOND_USER, form.initial.get('recipient'))
        self.assertQuerysetEqual(expected_init_sender_books, result_init_sender_books)
        self.assertQuerysetEqual(expected_init_recipient_books, result_init_recipient_books)

    def test_create_offer_get__when_many_on_many_books__expect_right_initial(self):
        for _ in range(3):
            self._create_book(
                title='Offered book',
                author='Offered author',
                owner=self.USER
            )
            self._create_book(
                title='Offered book',
                author='Offered author',
                owner=self.SECOND_USER
            )

        self._set_user_cf()
        self._login()

        response = self.client.get(self.TARGET_URL)

        form = response.context.get('form')
        expected_init_sender_books = Book.objects.filter(owner=self.USER)
        expected_init_recipient_books = Book.objects.filter(owner=self.SECOND_USER).exclude(pk=self.WANTED_BOOK.pk)
        result_init_sender_books = form.fields.get('sender_books').queryset.all()
        result_init_recipient_books = form.fields.get('recipient_books').queryset.all()

        self.assertEqual(self.USER, form.initial.get('sender'))
        self.assertEqual(self.SECOND_USER, form.initial.get('recipient'))
        self.assertQuerysetEqual(expected_init_sender_books, result_init_sender_books)
        self.assertQuerysetEqual(expected_init_recipient_books, result_init_recipient_books)

    def test_create_offer__when_valid_many_for_many_books_expect_successfully_created_offer(self):
        pass

    def test_create_offer__when_valid_many_for_one_books_expect_successfully_created_offer(self):
        pass

    def test_create_offer__when_valid_many_for_one_books_expect_successfully_created_offer(self):
        pass

    def test_create_offer__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
