from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.common.models import Notification
from my_project.common.views import DetailsNotificationView
from my_project.offer.models import Offer

UserModel = get_user_model()


class DetailsNotificationViewTests(django_test.TestCase):
    CREDENTIALS = {
        'username': f'user',
        'email': f'user@email.com',
        'password': f'testp@ss',
    }
    SECOND_CREDENTIALS = {
        'username': f'second_user',
        'email': f'second_user@email.com',
        'password': f'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserModel.objects.create_user(**cls.CREDENTIALS)
        second_user = UserModel.objects.create_user(**cls.SECOND_CREDENTIALS)
        Notification(
            sender=user,
            recipient=second_user,
            massage='Test massage',
        ).save()
        cls.NOTIFICATION = Notification.objects.first()
        cls.USER = user
        cls.SECOND_USER = second_user

    def _login(self):
        self.client.login(
            username=self.CREDENTIALS.get('username'),
            password=self.CREDENTIALS.get('password'),
        )

    def test_details_notf__when_user_is_notf_recipient_and_no_offer__expect_notf_read(self):
        self._login()
        Notification(
            sender=self.SECOND_USER,
            recipient=self.USER,
            massage='Test massage',
        ).save()

        test_notf = Notification.objects.get(recipient=self.USER)
        target_url = reverse('notification_details',
                             kwargs={'pk': test_notf.pk})

        response = self.client.get(target_url)

        context_notf = response.context.get(DetailsNotificationView.context_object_name)
        result_notf = Notification.objects.get(pk=test_notf.pk)
        self.assertEqual(test_notf, context_notf)
        self.assertTrue(result_notf.is_read)

    def test_details_notf__when_user_is_notf_recipient_and_notf_has_offer__expect_notf_read_and_redirect_offer_details(
            self):
        self._login()
        Offer(
            sender=self.SECOND_USER,
            recipient=self.USER
        ).save()
        offer = Offer.objects.first()

        test_notf = Notification.objects.get(recipient=self.USER)
        target_url = reverse('notification_details',
                             kwargs={'pk': test_notf.pk})

        response = self.client.get(target_url)

        redirect_url_with_next = reverse('show_offer_details',
                                         kwargs={'pk': offer.pk})
        result_notf = Notification.objects.get(pk=test_notf.pk)

        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
        self.assertTrue(result_notf.is_read)

    def test_details_notf__when_user_is_not_notf_recipient__expect_respond_status_code_403_and_notf_not_read(self):
        self._login()
        test_notf = self.NOTIFICATION
        target_url = reverse('notification_details',
                             kwargs={'pk': test_notf.pk})
        response = self.client.get(target_url)
        result_notf = Notification.objects.get(pk=test_notf.pk)
        self.assertEqual(403, response.status_code)
        self.assertFalse(result_notf.is_read)

    def test_details_notf__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        target_url = reverse('notification_details',
                             kwargs={'pk': self.NOTIFICATION.pk})
        response = self.client.get(target_url)
        redirect_url_with_next = f"{reverse('login_user')}?next={target_url}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
