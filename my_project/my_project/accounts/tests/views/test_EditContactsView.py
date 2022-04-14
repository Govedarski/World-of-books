from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

from my_project.accounts.models import ContactForm

UserModel = get_user_model()


class EditContactsViewTests(django_test.TestCase):
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
        self.valid_contact_form = {
            'city': 'Sofia',
            'address': 'some street',
            'phone_number': '123456789',
        }

    def _login(self):
        self.client.login(
            username=self.CREDENTIALS.get('username'),
            password=self.CREDENTIALS.get('password'),
        )

    def _assert_success_edit(self):
        cf_edited = ContactForm.objects.get(pk=self.USER.pk)
        self.assertEqual(self.valid_contact_form['city'], cf_edited.city)
        self.assertEqual(self.valid_contact_form['address'], cf_edited.address)
        self.assertEqual(self.valid_contact_form['phone_number'], cf_edited.phone_number)
        self.assertTrue(cf_edited.is_completed)

    def _assert_fail_edit(self, response):
        cf_edited = ContactForm.objects.get(pk=self.USER.pk)
        form = response.context.get('form')
        self.assertIsNone(cf_edited.city)
        self.assertIsNone(cf_edited.city)
        self.assertIsNone(cf_edited.city)
        self.assertFalse(cf_edited.is_completed)
        self.assertNotEqual({}, form.errors)

    def test_edit_cf_with_valid_email_and_no_next__expect_save_changed_cf_and_correct_success_url(self):
        self._login()
        response = self.client.post(
            reverse('edit_contacts'),
            data=self.valid_contact_form,
        )
        self._assert_success_edit()
        redirect_url = reverse('show_account_details',
                               kwargs={"pk": self.USER.pk})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_cf_with_valid_email_and_next__expect_save_changed_cf_and_correct_success_url(self):
        self._login()

        url_with_next = f"{reverse('edit_contacts')}?next={reverse('create_book')}"
        response = self.client.post(
            url_with_next,
            data=self.valid_contact_form,
        )

        self._assert_success_edit()
        redirect_url = reverse('create_book')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_cf_with_no_city__expect_not_save_and_error(self):
        self._login()
        no_city = {'city': ''}
        self.valid_contact_form.update(no_city)
        response = self.client.post(
            reverse('edit_contacts'),
            data=self.valid_contact_form,
        )

        self._assert_fail_edit(response)

    def test_edit_cf_with_no_address__expect_not_save_and_error(self):
        self._login()
        no_address = {'address': ''}
        self.valid_contact_form.update(no_address)
        response = self.client.post(
            reverse('edit_contacts'),
            data=self.valid_contact_form,
        )

        self._assert_fail_edit(response)

    def test_edit_cf_with_no_phone_number__expect_save_changed_cf(self):
        self._login()
        no_phone_number = {'phone_number': ''}
        self.valid_contact_form.update(no_phone_number)
        response = self.client.post(
            reverse('edit_contacts'),
            data=self.valid_contact_form,
        )

        cf_edited = ContactForm.objects.get(pk=self.USER.pk)
        self.assertEqual(self.valid_contact_form['city'], cf_edited.city)
        self.assertEqual(self.valid_contact_form['address'], cf_edited.address)
        self.assertIsNone(cf_edited.phone_number)
        self.assertTrue(cf_edited.is_completed)

    def test_edit_cf_with_invalid_phone_number__expect_not_save_and_error(self):
        self._login()
        invalid_phone_number = {'phone_number': 'invalid_number_1221'}
        self.valid_contact_form.update(invalid_phone_number)

        response = self.client.post(
            reverse('edit_contacts'),
            data=self.valid_contact_form,
        )

        self._assert_fail_edit(response)

    def test_edit_cf__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(reverse('edit_contacts'))

        redirect_url_with_next = f"{reverse('login_user')}?next={reverse('edit_contacts')}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
