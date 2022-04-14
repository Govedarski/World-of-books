from django import test as django_test
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse

from my_project.accounts.models import ContactForm, Profile
from my_project.library.models import Book
from my_project.offer.models import Offer

UserModel = get_user_model()


class DeactivateUserViewTests(django_test.TestCase):
    CREDENTIALS = {
        'username': 'User',
        'email': 'user@email.com',
        'password': 'testp@ss',
    }
    SECOND_CREDENTIALS = {
        'username': 'second_user',
        'email': 'second_user@email.com',
        'password': 'testp@ss',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserModel.objects.create_user(**cls.CREDENTIALS)
        profile = Profile.objects.get(pk=user.pk)
        cf = ContactForm.objects.get(pk=user.pk)
        cls._set_profile_data(profile)
        cls._set_cf_data(cf)
        cls.USER = user
        cls.PROFILE = profile
        cls.CF = cf
        cls.SECOND_USER = UserModel.objects.create_user(**cls.SECOND_CREDENTIALS)

    @staticmethod
    def _set_profile_data(profile):
        profile.first_name = 'Test'
        profile.last_name = 'User'
        profile.description = 'Test description'
        profile.gender = Profile.GenderChoices.MALE
        profile.save()

    @staticmethod
    def _set_cf_data(cf):
        cf.city = "Sofia"
        cf.address = "Test street"
        cf.phone_number = "123456789"
        cf.save()

    def _login(self):
        self.client.login(
            username=self.CREDENTIALS.get('username'),
            password=self.CREDENTIALS.get('password'),
        )

    def _create_books(self, number, user):
        for i in range(number):
            Book(title=f"Book {i}",
                 author=f'Author {i}',
                 owner=user).save()

    def _create_offers(self, number, sender, recipient):
        for i in range(number):
            Offer(sender=sender,
                  recipient=recipient).save()

    def test_deactivate_user__when_get_request_authenticated_user__expect_object_equal_user(self):
        self._login()

        response = self.client.get(reverse('deactivate_user'))

        obj = response.context.get('object')
        self.assertEqual(self.USER, obj)

    def test_deactivate_user__when_post_request_authenticated_user__expect_deactivated_user(self):
        self._login()

        self.client.post(reverse('deactivate_user'))

        deactivated_user = UserModel.objects.get(pk=self.USER.pk)
        self.assertFalse(deactivated_user.is_active)

    def test_deactivate_user__when_post_request_authenticated_user__expect_delete_existing_profile_data(self):
        self._login()

        self.client.post(reverse('deactivate_user'))

        deactivated_profile = Profile.objects.get(pk=self.USER.pk)
        self.assertIsNone(deactivated_profile.first_name)
        self.assertIsNone(deactivated_profile.last_name)
        self.assertIsNone(deactivated_profile.description)
        self.assertEqual(Profile.GenderChoices.DO_NOT_SHOW, deactivated_profile.gender)

    def test_deactivate_user__when_post_request_authenticated_user__expect_delete_existing_cf_data(self):
        self._login()

        self.client.post(reverse('deactivate_user'))

        deactivated_cf = ContactForm.objects.get(pk=self.USER.pk)
        self.assertIsNone(deactivated_cf.city)
        self.assertIsNone(deactivated_cf.address)
        self.assertIsNone(deactivated_cf.phone_number)

    def test_deactivate_user__when_post_request_authenticated_user__expect_books_that_own_set_untradable_and_not_change_rest(
            self):
        self._create_books(5, self.USER)
        self._create_books(5, self.SECOND_USER)
        self._login()

        self.client.post(reverse('deactivate_user'))
        user_books = Book.objects.filter(owner=self.USER)
        other_books = Book.objects.exclude(owner=self.USER)
        self.assertFalse(any(book.is_tradable for book in user_books))
        self.assertTrue(all(book.is_tradable for book in other_books))

    def test_deactivate_user__when_post_request_authenticated_user__expect_user_offers_set_inactive_and_not_change_rest(
            self):
        credentials = {
            'username': 'Extra User',
            'email': 'extrauser@email.com',
            'password': 'testp@ss',
        }
        extra_user = UserModel.objects.create_user(**credentials)

        self._create_offers(5, self.USER, self.SECOND_USER)
        self._create_offers(5, self.SECOND_USER, self.USER)
        self._create_offers(5, self.SECOND_USER, extra_user)
        self._login()

        self.client.post(reverse('deactivate_user'))
        user_offers = Offer.objects.filter(Q(sender=self.USER) | Q(recipient=self.USER))
        other_offers = Offer.objects.exclude(Q(sender=self.USER) | Q(recipient=self.USER))
        self.assertFalse(any(offer.is_active for offer in user_offers))
        self.assertTrue(all(offer.is_active for offer in other_offers))

    def test_deactivate_user__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(reverse('deactivate_user'))
        redirect_url_with_next = f"{reverse('login_user')}?next={reverse('deactivate_user')}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)
