from django import forms
from django.core.exceptions import ValidationError

from my_project.common.helpers.custom_mixins import AddCCSMixin
from my_project.library.models import Book
from my_project.offer.models import Offer


class CreateOfferForm(AddCCSMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''CSS'''
        self.fields['sender_books'].widget.attrs.update({'class': 'height-90'})
        self._add_ccs('my_form_control', 'width-100', 'opacity-format')
        '''Get sender, recipient and wanted book'''
        initial = kwargs.get('initial')
        wanted_book = initial.get('wanted_book')
        sender = initial.get('sender')
        recipient = initial.get('recipient')
        '''filter many-to-many-field to show only books that belong to sender'''
        self.fields['sender_books'].queryset = Book.objects.filter(owner=sender, is_tradable=True)
        '''filter many-to-many-field to show only books that belong to recipient 
        but the one book that is included already'''
        want_more_books = Book.objects.filter(owner=recipient, is_tradable=True).exclude(pk=wanted_book.pk)
        self.fields['recipient_books'].queryset = want_more_books
        self.fields['recipient_books'].required = False

    class Meta:
        model = Offer
        fields = ['recipient_books', 'sender_books']


class NegotiateOfferForm(AddCCSMixin, forms.ModelForm):
    NOT_CHANGE_ERROR = 'You have not changed anything!'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''CSS'''
        self._add_ccs('my_form_control', 'width-100', 'opacity-format')
        old_offer = kwargs.get('instance')
        '''Change the last offer's sender and recipient books for the new one'''
        new_sender = old_offer.recipient
        new_recipient = old_offer.sender
        self.initial['sender_books'], self.initial['recipient_books'] = self.initial['recipient_books'], self.initial[
            'sender_books']
        self.fields['sender_books'].queryset = Book.objects.filter(owner=new_sender, is_tradable=True)
        self.fields['recipient_books'].queryset = Book.objects.filter(owner=new_recipient, is_tradable=True)

    class Meta:
        model = Offer
        fields = ['recipient_books', 'sender_books']

    def clean(self):
        if all(self.initial[field] == list(self.cleaned_data[field]) for field in self.initial):
            raise ValidationError(self.NOT_CHANGE_ERROR)
        return super().clean()
