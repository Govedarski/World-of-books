from django import test as django_test
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.urls import reverse

from my_project.library.models import Book, Category
from my_project.library.views import ShowBookListView

UserModel = get_user_model()


class ShowBookListViewTest(django_test.TestCase):
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
        cls.TARGET_URL = reverse('book_list')

    def setUp(self) -> None:
        self.most_liked_book = self._set_likes()

    def _set_likes(self):
        most_liked_book = Book.objects.first()
        second_most_liked_book = Book.objects.last()
        most_liked_book.likes.set([user.pk for user in UserModel.objects.all()])
        second_most_liked_book.likes.set([UserModel.objects.first().pk])
        return most_liked_book

    @staticmethod
    def _create_books(number, owner):
        for i in range(number):
            Book.objects.create(
                title=f"Test title {i} {owner}",
                author=f"Test author {i} {owner}",
                owner=owner,
                category=Category.objects.create(name=f'Test category {i} {owner}')
            )

    def test_show_books_list_when_no_query_params__expect_show_all_books_order_by_likes_and_ord_equal_dash_in_context(
            self):
        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')

        response = self.client.get(self.TARGET_URL)

        result_books = response.context.get(ShowBookListView.context_object_name)
        self.assertQuerysetEqual(expected_books, result_books)
        self.assertEqual('-', response.context.get('ord'))
        self.assertEqual(self.most_liked_book, result_books.first())

    def test_show_books_list_when_ord_title__expect_show_all_books_order_by_title(self):
        ord_by = 'title'
        query_data = {'ord_by': ord_by}

        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')
        expected_books = expected_books.order_by(ord_by)

        response = self.client.get(self.TARGET_URL,
                                   data=query_data)

        result_books = response.context.get(ShowBookListView.context_object_name)

        self.assertQuerysetEqual(expected_books, result_books)

    def test_show_books_list_when_ord_author__expect_show_all_books_order_by_author(self):
        ord_by = 'author'
        query_data = {'ord_by': ord_by}

        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')
        expected_books = expected_books.order_by(ord_by)

        response = self.client.get(self.TARGET_URL,
                                   data=query_data)

        result_books = response.context.get(ShowBookListView.context_object_name)
        self.assertQuerysetEqual(expected_books, result_books)

    def test_show_books_list_when_ord_category__expect_show_all_books_order_by_category(self):
        ord_by = 'category'
        query_data = {'ord_by': ord_by}

        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')
        expected_books = expected_books.order_by(ord_by)

        response = self.client.get(self.TARGET_URL,
                                   data=query_data)

        result_books = response.context.get(ShowBookListView.context_object_name)
        self.assertQuerysetEqual(expected_books, result_books)

    def test_show_books_list_when_ord_owner__expect_show_all_books_order_by_owner(self):
        ord_by = 'owner'
        query_data = {'ord_by': ord_by}

        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')
        expected_books = expected_books.order_by(ord_by)

        response = self.client.get(self.TARGET_URL,
                                   data=query_data)

        result_books = response.context.get(ShowBookListView.context_object_name)
        self.assertQuerysetEqual(expected_books, result_books)

    def test_show_books_list_when_search_title__expect_show_all_books_contains_searched_title(self):
        search_by = 'title'
        search = '1'
        query_data = {'search_by': search_by,
                      'search': search}

        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')
        expected_books = expected_books.filter(title__icontains=search)

        response = self.client.get(self.TARGET_URL,
                                   data=query_data)

        result_books = response.context.get(ShowBookListView.context_object_name)
        self.assertQuerysetEqual(expected_books, result_books)
        self.assertEqual(2, result_books.count())

    def test_show_books_list_when_search_author__expect_show_all_books_contains_searched_author(self):
        search_by = 'author'
        search = '1'
        query_data = {'search_by': search_by,
                      'search': search}

        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')
        expected_books = expected_books.filter(author__icontains=search)

        response = self.client.get(self.TARGET_URL,
                                   data=query_data)

        result_books = response.context.get(ShowBookListView.context_object_name)
        self.assertQuerysetEqual(expected_books, result_books)
        self.assertEqual(2, result_books.count())

    def test_show_books_list_when_search_owner__expect_show_all_books_that_to_owner_contains_searched_owner(self):
        search_by = 'owner'
        search = self.SECOND_CREDENTIALS.get('username')
        query_data = {'search_by': search_by,
                      'search': search}

        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')
        expected_books = expected_books.filter(owner=self.SECOND_USER)

        response = self.client.get(self.TARGET_URL,
                                   data=query_data)

        result_books = response.context.get(ShowBookListView.context_object_name)
        self.assertQuerysetEqual(expected_books, result_books)
        self.assertEqual(5, result_books.count())

    def test_show_books_list_when_search_author_ord_title_reverse__expect_books_contains_searched_author_ord_by_title_reverse_and_right_context(
            self):
        ord_by = 'title'
        ord_ = '-'
        search_by = 'author'
        search = self.SECOND_CREDENTIALS.get('username')
        query_data = {'ord_by': ord_by,
                      'ord': ord_,
                      'search_by': search_by,
                      'search': search}

        expected_books = Book.objects.annotate(like_count=Count('likes')).order_by('-like_count', 'title')
        expected_books = expected_books.filter(author__icontains=search)
        expected_books = expected_books.order_by('-title')

        response = self.client.get(self.TARGET_URL,
                                   data=query_data)

        result_books = response.context.get(ShowBookListView.context_object_name)

        self.assertQuerysetEqual(expected_books, result_books)
        self.assertEqual(5, result_books.count())
        self.assertEqual(ord_, response.context.get('ord'))
        self.assertEqual(ord_by, response.context.get('ord_by'))
        self.assertEqual(search_by, response.context.get('search_by'))
        self.assertEqual(search, response.context.get('search'))
