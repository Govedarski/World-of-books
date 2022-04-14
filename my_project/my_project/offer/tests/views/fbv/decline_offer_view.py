from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.common.models import Notification
from my_project.offer.models import Offer
from my_project.offer.views import ShowOffersView

UserModel = get_user_model()


class DeclineOfferViewTest(django_test.TestCase):
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
        cls.USER = user
        cls.SECOND_USER = second_user
        cls._create_offers(user, second_user)
        offer = Offer.objects.first()
        cls.OFFER = offer
        cls.TARGET_URL = reverse('decline_offer',
                                 kwargs={'pk': offer.pk})

    def _login(self, **kwarg):
        if kwarg:
            self.client.login(**kwarg)
        else:
            self.client.login(
                username=self.CREDENTIALS.get('username'),
                password=self.CREDENTIALS.get('password'),
            )

    @staticmethod
    def _create_offers(sender, recipient):
        Offer(
            sender=sender,
            recipient=recipient,
        ).save()

    def test_decline_offer__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_decline_offer__when_user_is_not_recipient__expect_status_code_403(self):
        self._login(**self.CREDENTIALS)
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(403, response.status_code)

    def test_decline_offer__when_valid_user__expect_inactive_offer_notf_created_right_redirect(self):
        self._login(**self.SECOND_CREDENTIALS)

        response = self.client.get(self.TARGET_URL)

        result_offer = Offer.objects.get(pk=self.OFFER.pk)
        result_notification = Notification.objects.order_by('pk').last()
        redirect_url = reverse('show_offer_details',
                               kwargs={'pk': self.OFFER.pk})

        self.assertFalse(result_offer.is_active)
        self.assertFalse(result_offer.is_accept)

        self.assertTrue(result_notification.is_answered)
        self.assertEqual(self.SECOND_USER, result_notification.sender)
        self.assertEqual(self.USER, result_notification.recipient)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
