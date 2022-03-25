from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView, PasswordChangeView
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin

from my_project.accounts.forms import CreateUserForm, CreateProfileForm, MyLoginForm, MySetPasswordForm
from my_project.accounts.models import Profile
from my_project.common.helpers.mixins import CustomLoginRequiredMixin


class RegisterUserView(CreateView):
    form_class = CreateUserForm
    model = get_user_model()
    success_url = reverse_lazy('done_registration')
    template_name = 'accounts/create_user.html'
    second_form = CreateProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = self.second_form
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        profile = CreateProfileForm(self.request.POST)
        profile.instance.user = user

        if profile.is_valid():
            redirect_to_success_url = super().form_valid(form)
            profile.save()
            login(self.request, self.object,
                  backend='my_project.accounts.backend.EmailOrUsernameModelBackend')  # must addd backend
            return redirect_to_success_url
        return self.form_invalid(form)

    def form_invalid(self, form):
        self.second_form = CreateProfileForm(self.request.POST)
        return super().form_invalid(form)


class DoneRegistrationView(TemplateView):
    template_name = 'accounts/done_registration.html'


class LoginUserView(LoginView):
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
        next_page = self.request.GET.get('next')
        return next_page if next_page else reverse_lazy('show_home')


class MyResetPasswordView(PasswordResetView):
    template_name = 'accounts/reset_password.html'


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/reset_password_done.html'


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = MySetPasswordForm
    template_name = "accounts/change_password.html"


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/reset_completed.html'


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/change_password.html'

    def get_success_url(self):
        next_page = self.request.GET.get('next')
        return next_page if next_page else reverse_lazy('show_home')


class AccountDetailsView(CustomLoginRequiredMixin, TemplateView):
    template_name = 'accounts/account_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_user_model().objects.filter(pk=self.request.user.pk)
        if user:
            user = user[0]
            context['user'] = user

        return context
