from django.core.exceptions import PermissionDenied
from django.urls import reverse

from my_project.library.models import Book
from my_project.offer.tests.views.cbv.test_CreateOfferView.setup import SetupCreateOfferViewTests
from my_project.offer.views import CreateOfferView


class CreateOfferViewTestsDispatch(SetupCreateOfferViewTests):

    def test_create_offer__when_no_authenticated_user__expect_redirect_to_login_with_next(self):
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('login_user')}?next={self.TARGET_URL}"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_create_offer__when_user_but_cf_not_completed__expect_redirect_edited_cf_with_next(self):
        self._login()
        response = self.client.get(self.TARGET_URL)
        redirect_url_with_next = f"{reverse('edit_contacts')}?next={self.TARGET_URL}#edit"
        self.assertRedirects(response, redirect_url_with_next, status_code=302, target_status_code=200)

    def test_create_offer__when_user_try_to_make_offer_for_his_own_book__expect_status_code_403_and_right_exception(
            self):
        self._login(**self.SECOND_CREDENTIALS)
        self._set_user_cf(self.SECOND_USER)

        response = self.client.get(self.TARGET_URL)
        result_exception = response.context.get('exception')

        self.assertEqual(403, response.status_code)
        self.assertEqual(CreateOfferView.PERMISSION_DENIED_MASSAGE, result_exception)
