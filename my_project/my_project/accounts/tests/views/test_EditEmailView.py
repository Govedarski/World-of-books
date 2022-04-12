from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

UserModel = get_user_model()


class RegisterUserViewTests(django_test.TestCase):
    def setUp(self) -> None:
        self.credentials = {
            'username': 'User',
            'email': 'user@email.com',
            'password': 'testp@ss',
        }
        self.user = UserModel.objects.create_user(**self.credentials)
        self.new_email = {'email': 'editeduser@email.com'}

    def test_edit_email_with_valid_email__expect_save_changed_email_and_success_url(self):
        self.client.login(
            username=self.credentials.get('username'),
            password=self.credentials.get('password'),
        )
        response = self.client.post(
            reverse('edit_email'),
            data=self.new_email,
        )
        user_edited_email = UserModel.objects.get(pk=self.user.pk).email
        self.assertEqual(self.new_email['email'], user_edited_email)
        redirect_url = reverse('show_account_details',
                               kwargs={"pk": self.user.pk})

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_email_with_invalid_email__expect_old_email_and_form_error(self):
        self.client.login(
            username=self.credentials.get('username'),
            password=self.credentials.get('password'),
        )
        new_email = {'email': 'invaliduseremail.com'}
        response = self.client.post(
            reverse('edit_email'),
            data=new_email,
        )

        form = response.context.get('form')
        user_edited_email = UserModel.objects.get(pk=self.user.pk).email
        self.assertEqual(self.user.email, user_edited_email)
        self.assertNotEqual({}, form.errors)

    def test_edit_email__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(reverse('edit_email'))

        redirect_url_with_next = f"{reverse('login_user')}?next={reverse('edit_email')}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
