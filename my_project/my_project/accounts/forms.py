import os
from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm

from my_project.accounts.models import Profile


class ModifyAuthFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'my_form_control-one-on-line opacity-format'})
            field.help_text = None

class CreateUserForm(ModifyAuthFormMixin, UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Enter password again'})
        self.fields['password2'].label = "Confirm Password"

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']


class CreateProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'my_form_control-two-on-line opacity-format'})
        self.fields['date_of_birth'].widget.attrs.update({'class': 'date-form-control opacity-format'})
        self.fields['description'].widget.attrs.update({'class': 'my_form_control-one-on-line opacity-format'})

        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter last name'})
        self.fields['city'].widget.attrs.update({'placeholder': 'Enter city you live'})
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


class MyLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'my_form_control-one-on-line opacity-format'})

class MySetPasswordForm(ModifyAuthFormMixin, SetPasswordForm):
    pass


#
# class EditProfileForm(CreateProfileForm):
#     class Meta(CreateProfileForm.Meta):
#         fields = '__all__'
#         exclude = ['user']
#         widgets = {
#             'description': forms.Textarea(
#                 attrs={'rows': 3}
#             ),
#         }
