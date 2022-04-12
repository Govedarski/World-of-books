from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.accounts.models import Profile, ContactForm

UserModel = get_user_model()


class RegisterUserViewTests(django_test.TestCase):
    VALID_USER_CREDENTIALS = {
        'username': 'testuser',
        'email': 'testuser@gmail.com',
        'password1': '12q3e45ew',
        'password2': '12q3e45ew',
    }

    VALID_PROFILE_DATA = {
        'first_name': 'TestFName',
        'last_name': 'TestLName',
        'gender': Profile.GenderChoices.MALE,
    }

    INVALID_USER_CREDENTIALS = {
        'username': 'invalidtestuser',
        'email': 'invalidtestuser@gmail.com',
        'password1': '56545250',
        'password2': '56545250',
    }

    INVALID_PROFILE_DATA = {
        'first_name': 'Test1Name',
        'last_name': 'a',
    }

    def setUp(self) -> None:
        self.existing_user_credentials = {
            'username': 'ExistingUser',
            'email': 'existing_user@email.com',
            'password': 'testp@ss',
        }
        self.existing_user = UserModel.objects.create_user(**self.existing_user_credentials)

        self.default_profile_data = {'gender': self._get_gender_default_choice()}

    def _get_gender_default_choice(self):
        profile_form = self.client.get(reverse('create_user')).context.get('profile_form')
        gender = profile_form.base_fields.get('gender').initial
        return gender

    def test_register_user__when_valid_user_credentials_and_no_profile_data__expect_created_user_profile_and_contactform(
            self):
        profile_data = self.default_profile_data
        data = self.VALID_USER_CREDENTIALS | profile_data

        response = self.client.post(
            reverse('create_user'),
            data=data,
        )

        new_created_user = UserModel.objects.order_by('pk').last()

        self.assertEqual(2, UserModel.objects.count())
        self.assertEqual(2, Profile.objects.count())
        self.assertEqual(2, ContactForm.objects.count())
        self.assertEqual(self.VALID_USER_CREDENTIALS['username'], new_created_user.username)
        self.assertEqual(self.VALID_USER_CREDENTIALS['email'], new_created_user.email)
        self.assertTrue(new_created_user.has_usable_password)

    def test_register_user__when_valid_user_and_profile_data__expect_created_user_profile_with_data_contactform(self):
        profile_data = self.default_profile_data
        profile_data.update(self.VALID_PROFILE_DATA)
        data = self.VALID_USER_CREDENTIALS | profile_data

        response = self.client.post(
            reverse('create_user'),
            data=data,
        )

        new_created_user = UserModel.objects.order_by('pk').last()
        new_created_profile = Profile.objects.order_by('pk').last()

        self.assertEqual(2, UserModel.objects.count())
        self.assertEqual(2, Profile.objects.count())
        self.assertEqual(2, ContactForm.objects.count())
        self.assertEqual(self.VALID_USER_CREDENTIALS['username'], new_created_user.username)
        self.assertEqual(self.VALID_USER_CREDENTIALS['email'], new_created_user.email)
        self.assertTrue(new_created_user.has_usable_password)
        self.assertEqual(self.VALID_PROFILE_DATA['first_name'], new_created_profile.first_name)
        self.assertEqual(self.VALID_PROFILE_DATA['last_name'], new_created_profile.last_name)
        self.assertEqual(self.VALID_PROFILE_DATA['gender'], new_created_profile.gender)

    def test_register_user__when_invalid_user_credentials_and_valid_profile_data__expect_user_error_and_instances(self):
        profile_data = self.default_profile_data
        profile_data.update(self.VALID_PROFILE_DATA)
        data = self.INVALID_USER_CREDENTIALS | profile_data

        response = self.client.post(
            reverse('create_user'),
            data=data,
        )

        user_form = response.context.get('form')
        profile_form = response.context.get('profile_form')
        self.assertNotEqual({}, user_form.errors)
        self.assertDictEqual({}, profile_form.errors)
        self.assertEqual(self.INVALID_USER_CREDENTIALS['username'], user_form.instance.username)
        self.assertEqual(self.VALID_PROFILE_DATA['first_name'], profile_form.instance.first_name)
        self.assertEqual(1, UserModel.objects.count())
        self.assertEqual(1, Profile.objects.count())
        self.assertEqual(1, ContactForm.objects.count())

    def test_register_user__when_valid_user_credentials_and_invalid_profile_data__expect_error_and_instances(self):
        profile_data = self.default_profile_data
        profile_data.update(self.INVALID_PROFILE_DATA)
        data = self.VALID_USER_CREDENTIALS | profile_data

        response = self.client.post(
            reverse('create_user'),
            data=data,
        )

        user_form = response.context.get('form')
        profile_form = response.context.get('profile_form')

        self.assertDictEqual({}, user_form.errors)
        self.assertNotEqual({}, profile_form.errors)
        self.assertEqual(self.VALID_USER_CREDENTIALS['username'], user_form.instance.username)
        self.assertEqual(self.INVALID_PROFILE_DATA['first_name'], profile_form.instance.first_name)
        self.assertEqual(1, UserModel.objects.count())
        self.assertEqual(1, Profile.objects.count())
        self.assertEqual(1, ContactForm.objects.count())

    def test_register_user__when_invalid_user_credentials_and_invalid_profile_data__expect_errors_and_instances_for_both(
            self):
        profile_data = self.default_profile_data
        profile_data.update(self.INVALID_PROFILE_DATA)
        data = self.INVALID_USER_CREDENTIALS | profile_data

        response = self.client.post(
            reverse('create_user'),
            data=data,
        )

        user_form = response.context.get('form')
        profile_form = response.context.get('profile_form')

        self.assertNotEqual({}, user_form.errors)
        self.assertNotEqual({}, profile_form.errors)
        self.assertEqual(self.INVALID_USER_CREDENTIALS['username'], user_form.instance.username)
        self.assertEqual(self.INVALID_PROFILE_DATA['first_name'], profile_form.instance.first_name)
        self.assertEqual(1, UserModel.objects.count())
        self.assertEqual(1, Profile.objects.count())
        self.assertEqual(1, ContactForm.objects.count())

    def test_register_user__when_user_username_is_another_user_email_and_no_profile_data__expect_errors(
            self):
        user_data_repeated_email = {
            'username': 'existing_user@email.com',
            'email': 'valid@email.com',
            'password1': 'validp@ss',
            'password2': 'validp@ss',
        }
        profile_data = self.default_profile_data
        data = user_data_repeated_email | profile_data
        response = self.client.post(
            reverse('create_user'),
            data=data,
        )

        user_form = response.context.get('form')
        profile_form = response.context.get('profile_form')

        user_expected_error_massage = UserModel.USERNAME_VALIDATION_ERROR_MASSAGE
        user_actual_error_massage = user_form.errors.get('username')[0]
        self.assertEqual(user_expected_error_massage, user_actual_error_massage)
        self.assertEqual({}, profile_form.errors)
        self.assertEqual(user_data_repeated_email['email'], user_form.instance.email)
        self.assertEqual(self.default_profile_data['gender'], profile_form.instance.gender)
        self.assertEqual(1, UserModel.objects.count())
        self.assertEqual(1, Profile.objects.count())
        self.assertEqual(1, ContactForm.objects.count())

    def test_dispatch__when_request_user_is_authenticated__expect_redirect_home(self):
        valid_credentials_username = {
            'username': 'ExistingUser',
            'password': 'testp@ss', }

        self.client.login(**valid_credentials_username)
        response = self.client.get(reverse('create_user'))

        self.assertRedirects(response, reverse('show_home'), status_code=302, target_status_code=200)
