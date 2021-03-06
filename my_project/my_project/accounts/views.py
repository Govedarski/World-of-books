from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView, PasswordChangeView
# Create your views here.
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView, DeleteView

from my_project.accounts.forms import CreateUserForm, ProfileForm, MyLoginForm, MySetPasswordForm, EditEmailForm, \
    MyPasswordChangeForm, EditContactForm
from my_project.accounts.helpers.custom_mixins import LogoutRequiredMixin
from my_project.accounts.models import Profile, ContactForm
from my_project.library.models import Book
from my_project.offer.models import Offer

UserModel = get_user_model()


class RegisterUserView(LogoutRequiredMixin, CreateView):
    form_class = CreateUserForm
    model = UserModel
    success_url = reverse_lazy('done_registration')
    template_name = 'accounts/create_user.html'
    second_form = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = self.second_form
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        profile = ProfileForm(self.request.POST, self.request.FILES)
        profile.instance.user = user

        if profile.is_valid():
            redirect_to_success_url = super().form_valid(form)
            profile.save()
            login(self.request, self.object,
                  backend='my_project.accounts.backend.EmailOrUsernameModelBackend')
            return redirect_to_success_url
        return self.form_invalid(form)

    def form_invalid(self, form):
        self.second_form = ProfileForm(self.request.POST)
        return super().form_invalid(form)


class DoneRegistrationView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/done_registration.html'


class LoginUserView(LogoutRequiredMixin, LoginView):
    template_name = 'accounts/login_page.html'
    form_class = MyLoginForm

    def get_success_url(self):
        next_page = self.request.GET.get('next')
        return next_page if next_page else reverse_lazy('show_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_login"] = True
        return context


class LogoutUserView(LogoutView):
    def get_next_page(self):
        return reverse_lazy('show_home')


class MyResetPasswordView(PasswordResetView):
    template_name = 'accounts/reset_password.html'


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/reset_password_done.html'


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = MySetPasswordForm
    template_name = "accounts/change_password.html"


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/reset_completed.html'


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    form_class = MyPasswordChangeForm

    def get_success_url(self):
        return f'{self.request.user.get_absolute_url()}?password_change=done'


class AccountDetailsView(DetailView):
    model = UserModel
    template_name = 'accounts/account_details.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_staff_view_user_info'] = self.request.user.has_perm('accounts.view_worldofbooksuser')
        context['can_staff_view_cf'] = self.request.user.has_perm('accounts.view_worldofbooksuser')
        context['can_staff_edit'] = self.request.user.has_perm('accounts.change_worldofbooksuser')
        context['password_change'] = self.request.GET.get('password_change')
        return context


class EditEmailView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/edit_email.html'
    form_class = EditEmailForm

    def get_object(self, queryset=None):
        return UserModel.objects.get(pk=self.request.user.pk)

    def get_success_url(self):
        return self.request.user.get_absolute_url()


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/edit_profile.html'
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return Profile.objects.get(user_id=self.request.user.pk)

    def get_success_url(self):
        return self.request.user.get_absolute_url()


class EditContactsView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/edit_contacts.html'
    form_class = EditContactForm

    def get_object(self, queryset=None):
        return ContactForm.objects.get(user_id=self.request.user.pk)

    def get_success_url(self):
        next_page = self.request.GET.get('next')
        return next_page if next_page else self.request.user.get_absolute_url()


class DeactivateUserView(LoginRequiredMixin, DeleteView):
    template_name = 'accounts/deactivate_user.html'
    model = UserModel
    fields = "__all__"
    success_url = reverse_lazy('show_home')

    def get_object(self, queryset=None):
        return UserModel.objects.get(pk=self.request.user.pk)

    def post(self, request, *args, **kwargs):
        result = super().post(request, *args, **kwargs)
        logout(request)
        return result

    def form_valid(self, form):
        user = self.object
        user.is_active = False
        user.save()
        books = Book.objects.prefetch_related('owner').filter(owner=user)
        self._make_books_untradable(books)
        offers = Offer.objects.prefetch_related('sender', 'recipient') \
            .filter(Q(sender=user) | Q(recipient=user), is_active=True)
        self._make_offer_inactive(offers)
        self._delete_information(Profile, user)
        self._delete_information(ContactForm, user)
        return redirect(self.success_url)

    @staticmethod
    def _make_books_untradable(books):
        for book in books:
            book.is_tradable = False
            book.save()

    @staticmethod
    def _make_offer_inactive(offers):
        for offer in offers:
            offer.is_active = False
            offer.save()

    @staticmethod
    def _delete_information(my_model, user):
        obj = my_model.objects.get(pk=user.pk)
        obj.delete()
        my_model(user=user).save()
