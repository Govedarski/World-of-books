from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.offer.models import Offer
from my_project.offer.views import ShowOffersView

UserModel = get_user_model()


class ShowOfferDetailsViewTests(django_test.TestCase):
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

    EXTRA_CREDENTIALS = {
        'username': 'EXTRA_User',
        'email': 'EXTRA_user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserModel.objects.create_user(**cls.CREDENTIALS)
        second_user = UserModel.objects.create_user(**cls.SECOND_CREDENTIALS)
        extra_user = UserModel.objects.create_user(**cls.EXTRA_CREDENTIALS)
        cls.USER = user
        cls.SECOND_USER = second_user
        cls.EXTRA_USER = extra_user
        cls.TARGET_URL = reverse('show_offer_list')

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    @staticmethod
    def _create_offers(number, sender, recipient):
        for _ in range(number):
            Offer(
                sender=sender,
                recipient=recipient,
            ).save()

    def test_show_offers_list__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_show_offers_list_queryset__when_valid_user__expect_return_all_offers_which_is_sender_or_recipient_in(self):
        '''create offers, expect 20 offers to return'''
        self._create_offers(5, self.USER, self.SECOND_USER)
        self._create_offers(5, self.SECOND_USER, self.USER)
        self._create_offers(5, self.USER, self.EXTRA_USER)
        self._create_offers(5, self.EXTRA_USER, self.USER)
        self._create_offers(5, self.SECOND_USER, self.EXTRA_USER)
        self._create_offers(5, self.EXTRA_USER, self.SECOND_USER)

        self._login(**self.CREDENTIALS)

        response = self.client.get(self.TARGET_URL)
        offers = response.context.get(ShowOffersView.context_object_name)

        self.assertEqual(20, offers.count())
        self.assertTrue(offer.sender == self.USER or offer.recipient == self.USER for offer in offers)
