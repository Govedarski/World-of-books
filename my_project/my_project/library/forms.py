from django import forms
from django.contrib.auth import get_user_model
from django.db import models

from my_project.common.helpers.custom_mixins import AddCCSMixin
from my_project.library.models import Book, Category

UserModel = get_user_model()


class BookForm(AddCCSMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs('my_form_control', 'width-100', 'opacity-format')
        self.fields['category_name'].widget.attrs.update(
            {'placeholder': 'If you cannot find right category in the dropdown menu add it here'})

    category_name = forms.CharField(
        max_length=Category.NAME_MAX_LENGTH,
        label='',
        required=False
    )

    class Meta:
        model = Book
        fields = ['title', 'author', 'image', 'category']


class UsersListForm(AddCCSMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs('opacity-format')
        self.fields['user'].help_text = "If you choose nobody, this book will be deleted permanently"

    user = forms.ChoiceField(
        label='',
        choices=(),
    )


class SearchForm(forms.Form):
    class SearchByChoices(models.TextChoices):
        title = "title"
        author = "author"
        owner = "owner"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search'].widget.attrs.update({"class": 'my_form_control width-28 opacity-format'})
        self.fields['search_by'].widget.attrs.update({"class": 'opacity-format'})

    search = forms.CharField(
        max_length=max(
            Book.TITTLE_MAX_LENGTH,
            Book.AUTHOR_MAX_LENGTH,
            get_user_model().USERNAME_MAX_LENGTH
        ),
        required=False,
    )

    search_by = forms.ChoiceField(
        label='by',
        choices=SearchByChoices.choices,
    )
