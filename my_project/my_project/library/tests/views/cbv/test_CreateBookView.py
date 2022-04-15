from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book, Category

UserModel = get_user_model()


class CreateBookViewTest(django_test.TestCase):
    CREDENTIALS = {
        'username': 'user',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }
    TITLE = 'test_book'
    AUTHOR = 'test_author'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserModel.objects.create_user(**cls.CREDENTIALS)
        cls.TARGET_URL = reverse('create_book')
        cls.USER = user
        cls._create_category()
        cls.CATEGORY = Category.objects.first()

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    @staticmethod
    def _create_category():
        Category.objects.create(name='test cat')

    @staticmethod
    def _set_user_cf(user):
        cf = user.contactform
        cf.city = "test"
        cf.address = "test"
        cf.save()

    def test_create_book_when__user_create_book_with_selected_category__expect_valid_book_add_to_db(self):
        self._set_user_cf(self.USER)
        self._login()
        post_data = {
            'title': self.TITLE,
            'author': self.AUTHOR,
            'category': self.CATEGORY.pk
        }
        self.client.post(self.TARGET_URL,
                         data=post_data)

        result_book = Book.objects.first()
        self.assertEqual(self.TITLE, result_book.title)
        self.assertEqual(self.AUTHOR, result_book.author)
        self.assertEqual(self.CATEGORY, result_book.category)

    def test_create_book_when__user_create_book_with_typed_category__expect_valid_book_and_cat_add_to_db(self):
        new_category_name = 'new category'
        self._set_user_cf(self.USER)
        self._login()
        post_data = {
            'title': self.TITLE,
            'author': self.AUTHOR,
            'category_name': new_category_name,
        }
        self.client.post(self.TARGET_URL,
                         data=post_data)

        result_book = Book.objects.first()
        self.assertEqual(self.TITLE, result_book.title)
        self.assertEqual(self.AUTHOR, result_book.author)
        self.assertEqual(new_category_name, result_book.category.name)
        self.assertEqual(2, Category.objects.count())

    def test_create_book_when__user_create_book_with_typed_category_that_exist__expect_valid_book_to_db_cat_not(self):
        new_category_name = self.CATEGORY.name
        self._set_user_cf(self.USER)
        self._login()
        post_data = {
            'title': self.TITLE,
            'author': self.AUTHOR,
            'category_name': new_category_name,
        }
        self.client.post(self.TARGET_URL,
                         data=post_data)

        result_book = Book.objects.first()
        self.assertEqual(self.TITLE, result_book.title)
        self.assertEqual(self.AUTHOR, result_book.author)
        self.assertEqual(self.CATEGORY, result_book.category)
        self.assertEqual(1, Category.objects.count())

    def test_create_book_when__user_create_book_with_selected_and_typed_category__expect_valid_book_add_to_db_cat_not(
            self):
        new_category_name = 'new category'
        self._set_user_cf(self.USER)
        self._login()
        post_data = {
            'title': self.TITLE,
            'author': self.AUTHOR,
            'category': self.CATEGORY.pk,
            'category_name': new_category_name,

        }
        self.client.post(self.TARGET_URL,
                         data=post_data)

        result_book = Book.objects.first()
        self.assertEqual(self.TITLE, result_book.title)
        self.assertEqual(self.AUTHOR, result_book.author)
        self.assertEqual(self.CATEGORY, result_book.category)
        self.assertEqual(1, Category.objects.count())

    def test_create_book_redirect__when_next__expect_redirect_to_next(self):
        pass

    def test_create_book__when_user_but_cf_not_completed__expect_redirect_edited_cf_with_next(self):
        self._login()
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('edit_contacts')}?next={self.TARGET_URL}#edit"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_create_book__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
