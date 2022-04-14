import random

from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.library.models import Book

UserModel = get_user_model()


class ShowHomePageViewTestsTests(django_test.TestCase):
    CREDENTIALS = {
        'username': f'user',
        'email': f'user@email.com',
        'password': f'testp@ss',
    }
    NUMBER_OF_USERS = 10

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        UserModel.objects.create_user(**cls.CREDENTIALS)
        cls.USER = UserModel.objects.first()
        cls._create_users(cls.NUMBER_OF_USERS)

    @staticmethod
    def _create_users(number):
        for i in range(2, number + 2):
            credentials = {
                'username': f'user{i}',
                'email': f'user{i}@email.com',
                'password': f'testp{i}@ss',
            }
            UserModel.objects.create_user(**credentials)

    def _create_books(self, number, likes=None):
        for i in range(1, number + 1):
            book = Book(
                id=i,
                title=f"Book {i}",
                author=f"Author {i}",
                owner=self.USER
            )
            book.save()
            if likes:
                self._add_likes(book, likes)
            else:
                self._add_likes(book, random.randint(0, self.NUMBER_OF_USERS - 4))

    def _add_likes(self, book, number):
        for i in range(1, number + 1):
            id = self.USER.id + i
            book.likes.add(UserModel.objects.get(id=id))
        book.save()

    def _test_show_home_page__with_random_top_3_liked_books_out_of_n_books__expect_show_right_books(self,
                                                                                                    number_of_books):

        self._create_books(number_of_books)
        most_liked_books_pks = random.sample(range(1, number_of_books + 1), min(3, number_of_books))
        expected_book_to_show = []

        for i in range(len(most_liked_books_pks)):
            book = Book.objects.get(pk=most_liked_books_pks[i])
            self._add_likes(book, (self.NUMBER_OF_USERS - i))
            expected_book_to_show.append(book)

        response = self.client.get(reverse('show_home'))
        result_book_to_show = list(response.context.get('books_to_show'))
        self.assertListEqual(expected_book_to_show, result_book_to_show)

    def test_show_home_page__with_random_top_3_liked_books_out_of_10_books__expect_show_right_books(self):
        self._test_show_home_page__with_random_top_3_liked_books_out_of_n_books__expect_show_right_books(10)

    def test_show_home_page__with_random_top_3_liked_books_out_of_3_books__expect_show_right_books(self):
        self._test_show_home_page__with_random_top_3_liked_books_out_of_n_books__expect_show_right_books(3)

    def test_show_home_page__with_random_top_liked_books_out_of_2_books__expect_show_right_books(self):
        self._test_show_home_page__with_random_top_3_liked_books_out_of_n_books__expect_show_right_books(2)

    def test_show_home_page__with_no_books__expect_show_right_books(self):
        self._test_show_home_page__with_random_top_3_liked_books_out_of_n_books__expect_show_right_books(0)
