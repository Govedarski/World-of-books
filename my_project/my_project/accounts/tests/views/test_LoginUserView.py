from django import test as django_test
from django.contrib.auth import get_user_model
from django.urls import reverse

UserModel = get_user_model()


class LoginUserViewTests(django_test.TestCase):
    CREDENTIALS = {
        'username': 'User',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = UserModel.objects.create_user(**cls.CREDENTIALS)

    def test_login_with_username__when_valid_credential__expect_authenticated_user(self):
        credentials = {'username': self.CREDENTIALS.get('username'),
                       'password': self.CREDENTIALS.get('password')}

        response = self.client.post(reverse('login_user'), credentials, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_with_email__when_valid_credential__expect_authenticated_user(self):
        credentials = {'username': self.CREDENTIALS.get('email'),
                       'password': self.CREDENTIALS.get('password')}

        response = self.client.post(reverse('login_user'), credentials, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login__when_invalid_password__expect_authenticated_user(self):
        credentials = {'username': self.CREDENTIALS.get('username'),
                       'password': 'invalid_password'}

        response = self.client.post(reverse('login_user'), credentials, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login__when_invalid_username__expect_authenticated_user(self):
        credentials = {'username': 'invalid_username',
                       'password': self.CREDENTIALS.get('password')}

        response = self.client.post(reverse('login_user'), credentials, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_success_url__when_no_next__expect_redirect_home(self):
        credentials = {'username': self.CREDENTIALS.get('username'),
                       'password': self.CREDENTIALS.get('password')}

        response = self.client.post(reverse('login_user'), credentials, follow=True)
        self.assertRedirects(response, reverse('show_home'), status_code=302, target_status_code=200)

    def test_success_url__when_next__expect_redirect_to_next(self):
        credentials = {'username': self.CREDENTIALS.get('username'),
                       'password': self.CREDENTIALS.get('password')}
        url_with_next = f"{reverse('login_user')}?next={reverse('book_list')}"
        response = self.client.post(url_with_next, credentials, follow=True)
        self.assertRedirects(response, reverse('book_list'), status_code=302, target_status_code=200)
