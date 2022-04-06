from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView, PasswordChangeView
# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView

from my_project.accounts.forms import CreateUserForm, ProfileForm, MyLoginForm, MySetPasswordForm, EditEmailForm, \
    MyPasswordChangeForm, EditContactForm
from my_project.accounts.models import Profile, ContactForm


class RegisterUserView(CreateView):
    form_class = CreateUserForm
    model = get_user_model()
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
                  backend='my_project.accounts.backend.EmailOrUsernameModelBackend')  # must addd backend
            return redirect_to_success_url
        return self.form_invalid(form)

    def form_invalid(self, form):
        self.second_form = ProfileForm(self.request.POST)
        return super().form_invalid(form)


class DoneRegistrationView(LoginRequiredMixin, TemplateView):
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
    form_class = MyPasswordChangeForm

    def get_success_url(self):
        next_page = self.request.GET.get('next')
        return next_page if next_page else reverse_lazy('show_home')


class MyAccountDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/account_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_user_model().objects.get(pk=self.request.user.pk)
        context['user'] = user
        return context


class AccountDetailsView(DetailView):
    model = get_user_model()
    template_name = 'accounts/account_details.html'
    context_object_name = 'user'


class EditEmailView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/edit_email.html'
    form_class = EditEmailForm
    success_url = reverse_lazy('show_my_account_details')

    def get_object(self, queryset=None):
        return get_user_model().objects.get(pk=self.request.user.pk)


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/edit_profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('show_my_account_details')

    def get_object(self, queryset=None):
        return Profile.objects.get(user_id=self.request.user.pk)


class EditContactsView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/edit_contacts.html'
    form_class = EditContactForm
    success_url = reverse_lazy('show_my_account_details')

    def get_object(self, queryset=None):
        return ContactForm.objects.get(user_id=self.request.user.pk)
