from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.common.models import Notification
from my_project.common.views import ShowNotificationsView

UserModel = get_user_model()


class ShowNotificationsViewTests(django_test.TestCase):
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
    EXTRA_CREDENTIALS = {
        'username': f'extra_user',
        'email': f'extra_user@email.com',
        'password': f'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserModel.objects.create_user(**cls.CREDENTIALS)
        second_user = UserModel.objects.create_user(**cls.SECOND_CREDENTIALS)
        extra_user = UserModel.objects.create_user(**cls.EXTRA_CREDENTIALS)
        number_of_notf_of_a_kind = 5


        cls._create_notifications(
            number=number_of_notf_of_a_kind,
            sender=user,
            recipient=second_user)
        cls._create_notifications(
            number=number_of_notf_of_a_kind,
            sender=second_user,
            recipient=extra_user)

        cls.USER = user
        cls.SECOND_USER = second_user
        cls.EXTRA_USER = extra_user
        cls.NUMBER_OF_NOTF_OF_A_KIND = number_of_notf_of_a_kind

    @staticmethod
    def _create_notifications(number, sender, recipient):
        for i in range(number):
            Notification(
                sender=sender,
                recipient=recipient,
                massage='Test massage',
            ).save()

    def _login(self):
        self.client.login(
            username=self.CREDENTIALS.get('username'),
            password=self.CREDENTIALS.get('password'),
        )

    def test_get_queryset__with_all_kind_of_notification__expect_object_list_with_right_notifications(self):
        self._create_notifications(
            number=self.NUMBER_OF_NOTF_OF_A_KIND,
            sender=self.SECOND_USER,
            recipient=self.USER)

        expected_notf_to_show = Notification.objects.filter(recipient=self.USER)
        self._login()
        response = self.client.get(reverse('show_notifications'))
        result_obj_list = response.context.get(ShowNotificationsView.context_object_name)
        self.assertQuerysetEqual(expected_notf_to_show, result_obj_list)
        self.assertEqual(self.NUMBER_OF_NOTF_OF_A_KIND, len(result_obj_list))
        self.assertTrue(all(notf.recipient) == self.USER for notf in result_obj_list)

    def test_get_context__with_less_notf_than_paginate_by__expect_right_context(self):
        self._create_notifications(
            number=int(ShowNotificationsView.paginate_by/2),
            sender=self.SECOND_USER,
            recipient=self.USER)

        self._login()
        response = self.client.get(reverse('show_notifications'))
        self.assertTrue(response.context.get('hide_notifications', False))
        self.assertFalse(response.context.get('see_more', False))


    def test_get_context__with_more_notf_than_paginate_by__expect_right_context(self):
        self._create_notifications(
            number=int(ShowNotificationsView.paginate_by + 1),
            sender=self.SECOND_USER,
            recipient=self.USER)

        self._login()
        response = self.client.get(reverse('show_notifications'))
        self.assertTrue(response.context.get('hide_notifications', False))
        self.assertTrue(response.context.get('see_more', False))

    def test_get_context__with_notf_equal_to_paginate_by__expect_right_context(self):
        self._create_notifications(
            number=int(ShowNotificationsView.paginate_by),
            sender=self.SECOND_USER,
            recipient=self.USER)

        self._login()
        response = self.client.get(reverse('show_notifications'))
        self.assertTrue(response.context.get('hide_notifications', False))
        self.assertFalse(response.context.get('see_more', False))

    def test_get_context__with_no_notf__expect_right_context(self):
        self._login()
        response = self.client.get(reverse('show_notifications'))
        self.assertTrue(response.context.get('hide_notifications', False))
        self.assertFalse(response.context.get('see_more', False))

    def test_show_notifications__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(reverse('show_notifications'))
        redirect_url_with_next = f"{reverse('login_user')}?next={reverse('show_notifications')}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
