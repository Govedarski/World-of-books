from django import forms
from django.contrib.auth import get_user_model
from django.db import models

from my_project.common.helpers.mixins import AddCCSMixin
from my_project.library.models import Book


class CreateBookForm(AddCCSMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_ccs('my_form_control', 'width-100', 'opacity-format')

    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'image']


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
