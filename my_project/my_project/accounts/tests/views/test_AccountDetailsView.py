from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import Permission
from my_project.accounts.models import Profile, ContactForm

UserModel = get_user_model()


class AccountDetailsViewTests(django_test.TestCase):
    REGULAR_USER_CREDENTIALS = {
        'username': 'user',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }
    STAFF_USER_CREDENTIALS = {
        'username': 'staff_user',
        'email': 'staff_user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.REGULAR_USER = UserModel.objects.create_user(**cls.REGULAR_USER_CREDENTIALS)
        cls.STAFF_USER = UserModel.objects.create_user(**cls.STAFF_USER_CREDENTIALS)

    @staticmethod
    def _adding_permission(user):
        view_user_perm = Permission.objects.get(codename='view_worldofbooksuser')
        edit_user_perm = Permission.objects.get(codename='change_worldofbooksuser')
        user.user_permissions.add(view_user_perm)
        user.user_permissions.add(edit_user_perm)
        user.save()

    def test_account_details__when_staff_user_with_permission_visit_his_another_user__expect_right_context(self):
        self._adding_permission(self.STAFF_USER)
        self.client.login(
            username=self.STAFF_USER_CREDENTIALS.get('username'),
            password=self.STAFF_USER_CREDENTIALS.get('password'),
        )
        target_url = reverse('show_account_details', kwargs={'pk': self.REGULAR_USER.pk, })
        response = self.client.get(target_url)
        self.assertTrue(response.context.get('can_staff_view_user_info'))
        self.assertTrue(response.context.get('can_staff_view_cf'))
        self.assertTrue(response.context.get('can_staff_edit'))

    def test_account_details__when_staff_user_without_permission_visit_his_another_user__expect_right_context(self):
        self.client.login(
            username=self.STAFF_USER_CREDENTIALS.get('username'),
            password=self.STAFF_USER_CREDENTIALS.get('password'),
        )

        target_url = reverse('show_account_details', kwargs={'pk': self.REGULAR_USER.pk, })
        response = self.client.get(target_url)
        self.assertFalse(response.context.get('can_staff_view_user_info'))
        self.assertFalse(response.context.get('can_staff_view_cf'))
        self.assertFalse(response.context.get('can_staff_edit'))

    def test_account_details__when_login_user_visit_his_account__expect_user_equal_object(self):
        self.client.login(
            username=self.REGULAR_USER_CREDENTIALS.get('username'),
            password=self.REGULAR_USER_CREDENTIALS.get('password'),
        )

        target_url = reverse('show_account_details', kwargs={'pk': self.REGULAR_USER.pk, })
        response = self.client.get(target_url)
        self.assertFalse(response.context.get('can_staff_view_user_info'))
        self.assertFalse(response.context.get('can_staff_view_cf'))
        self.assertFalse(response.context.get('can_staff_edit'))
        self.assertTrue(response.context['user'] == response.context['object'])
