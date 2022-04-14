from django.urls import reverse

from my_project.library.models import Book
from my_project.offer.tests.views.cbv.test_CreateOfferView.setup import SetupCreateOfferViewTests


class CreateOfferViewTestsInit(SetupCreateOfferViewTests):
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

    def test_create_offer__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
