from my_project.common.models import Notification
from my_project.library.models import Book
from my_project.offer.models import Offer
from my_project.offer.tests.views.cbv.test_CreateOfferView.setup import SetupCreateOfferViewTests


class CreateOfferViewTestsPost(SetupCreateOfferViewTests):
    def test_create_offer__when_valid_books_expect_created_offer_and_notification(self):
        self._create_book(self.USER)
        sender_book_pk = Book.objects.get(owner=self.USER).pk
        self._set_user_cf()
        self._login()

        response = self.client.post(self.TARGET_URL,
                                    data={'sender_books': [sender_book_pk]})

        offer = Offer.objects.first()
        self.assertEqual(1, Offer.objects.count())
        self.assertEqual(self.USER, offer.sender)
        self.assertEqual(self.SECOND_USER, offer.recipient)
        self.assertQuerysetEqual(Book.objects.filter(owner=self.USER), offer.sender_books.all())
        self.assertQuerysetEqual(Book.objects.filter(owner=self.SECOND_USER), offer.recipient_books.all())
        self.assertFalse(offer.is_accept)
        self.assertTrue(offer.is_active)
        self.assertIsNone(offer.previous_offer)

        notification = Notification.objects.first()
        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(self.USER, notification.sender)
        self.assertEqual(self.SECOND_USER, notification.recipient)
        self.assertIsNone(notification.book)
        self.assertEqual(offer, notification.offer)
        self.assertFalse(notification.is_read)
        self.assertFalse(notification.is_answered)


    def test_create_offer__when_zero_for_wanted_book_expect_not_created_offer_and_error(self):
        self._set_user_cf()
        self._login()

        response = self.client.post(self.TARGET_URL,
                                    data={'sender_books': []})

        form = response.context.get('form')
        self.assertIsNotNone(form.errors)
        self.assertNotEqual({}, form.errors)
