import os
from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm, \
    PasswordChangeForm

from my_project.accounts.models import Profile, ContactForm
from my_project.common.helpers.custom_mixins import AddCCSMixin, RemoveHelpTextMixin


class CreateUserForm(AddCCSMixin, RemoveHelpTextMixin, UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs("my_form_control", 'width-100', 'opacity-format')
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Enter password again'})
        self.fields['password2'].label = "Confirm Password"

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']


class ProfileForm(AddCCSMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs('my_form_control', 'width-28', 'opacity-format')
        self.fields['date_of_birth'].widget.attrs.update({'class': 'date-form-control opacity-format'})
        self.fields['description'].widget.attrs.update({'class': 'my_form_control-one-on-line opacity-format'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter last name'})
        self.fields['nationality'].widget.attrs.update({'placeholder': 'Enter nationality'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Enter description'})

    class Meta:
        model = Profile
        exclude = ['user', 'picture_url']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
        }
        widgets = {
            'date_of_birth': forms.SelectDateWidget(years=range(date.today().year, 1920, -1))
        }


class MyLoginForm(AddCCSMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs('my_form_control', 'width-100', 'opacity-format')
        self.fields["username"].label = 'Username or email'


class MySetPasswordForm(AddCCSMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs('my_form_control', 'width-100' 'opacity-format')


class MyPasswordChangeForm(AddCCSMixin, RemoveHelpTextMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs('my_form_control', 'width-100', 'opacity-format')


class EditEmailForm(AddCCSMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs('my_form_control', 'width-75', 'opacity-format')

    class Meta:
        model = get_user_model()
        fields = ['email']


class EditContactForm(AddCCSMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].label_suffix = ':\n +359/'
        self._add_ccs('my_form_control', 'width-100')
        self.fields['city'].required = True
        self.fields['address'].required = True

    class Meta:
        model = ContactForm
        exclude = ['user']


