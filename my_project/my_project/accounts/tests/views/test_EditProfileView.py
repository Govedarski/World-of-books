from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.accounts.models import ContactForm, Profile

UserModel = get_user_model()


class EditProfileViewTests(django_test.TestCase):
    CREDENTIALS = {
        'username': 'User',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = UserModel.objects.create_user(**cls.CREDENTIALS)

    def setUp(self) -> None:
        self.valid_profile_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'gender': Profile.GenderChoices.DO_NOT_SHOW,
            'description': 'Test text',
        }

    def _login(self):
        self.client.login(
            username=self.CREDENTIALS.get('username'),
            password=self.CREDENTIALS.get('password'),
        )

    def test_edit_profile_with_valid_data__expect_save_changed_cf_and_correct_success_url(self):
        self._login()

        response = self.client.post(
            reverse('edit_profile'),
            data=self.valid_profile_data,
        )

        profile_edited = Profile.objects.get(pk=self.USER.pk)
        self.assertEqual(self.valid_profile_data['first_name'], profile_edited.first_name)
        self.assertEqual(self.valid_profile_data['last_name'], profile_edited.last_name)
        self.assertEqual(self.valid_profile_data['description'], profile_edited.description)
        self.assertEqual(Profile.GenderChoices.DO_NOT_SHOW, profile_edited.gender)

    def test_edit_profile_with_invalid_first_name__expect_not_save_and_error(self):
        self._login()
        invalid_first_name = {'first_name': 'invalid name'}
        self.valid_profile_data.update(invalid_first_name)

        response = self.client.post(
            reverse('edit_profile'),
            data=self.valid_profile_data,
        )

        profile_edited = Profile.objects.get(pk=self.USER.pk)
        profile_form = response.context.get('form')
        self.assertIsNone(profile_edited.first_name)
        self.assertIsNone(profile_edited.last_name)
        self.assertIsNone(profile_edited.description)
        self.assertEqual(Profile.GenderChoices.DO_NOT_SHOW, profile_edited.gender)
        self.assertNotEqual({}, profile_form.errors)

    def test_edit_profile_with_invalid_last_name__expect_not_save_and_error(self):
        self._login()
        invalid_last_name = {'last_name': 'invalidname123'}
        self.valid_profile_data.update(invalid_last_name)

        response = self.client.post(
            reverse('edit_profile'),
            data=self.valid_profile_data,
        )

        profile_edited = Profile.objects.get(pk=self.USER.pk)
        profile_form = response.context.get('form')
        self.assertIsNone(profile_edited.first_name)
        self.assertIsNone(profile_edited.last_name)
        self.assertIsNone(profile_edited.description)
        self.assertEqual(Profile.GenderChoices.DO_NOT_SHOW, profile_edited.gender)
        self.assertNotEqual({}, profile_form.errors)

    def test_edit_profile__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(reverse('edit_profile'))

        redirect_url_with_next = f"{reverse('login_user')}?next={reverse('edit_profile')}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
