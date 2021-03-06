from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView

from my_project.common.helpers.custom_mixins import PaginationShowMixin, AuthorizationRequiredMixin
from my_project.library.models import Book
from my_project.offer.forms import CreateOfferForm, NegotiateOfferForm
from my_project.offer.models import Offer


class CreateOfferView(LoginRequiredMixin, CreateView):
    PERMISSION_DENIED_MASSAGE = 'You cannot make offer for your own book!'
    template_name = 'offer/create_offer.html'
    form_class = CreateOfferForm
    success_url = reverse_lazy('show_offer_list')

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        if self.request.user.is_authenticated and not self.request.user.contactform.is_completed:
            return redirect(reverse_lazy('edit_contacts') + f"?next={self.request.path}#edit")
        if self.request.user == self._get_wanted_book().owner:
            raise PermissionDenied(self.PERMISSION_DENIED_MASSAGE)
        return result

    def get_initial(self):
        wanted_book = self._get_wanted_book()
        sender = self.request.user
        recipient = wanted_book.owner
        return {
            'wanted_book': wanted_book,
            'sender': sender,
            'recipient': recipient,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self._get_wanted_book()
        return context

    def form_valid(self, form):
        form = self._create_valid_form(form)
        result = super().form_valid(form)
        offer = self.object
        offer.recipient_books.add(self._get_wanted_book())
        offer.save()
        return result

    def _get_wanted_book(self):
        return Book.objects.get(pk=self.kwargs.get('pk'))

    def _create_valid_form(self, form):
        wanted_book = self._get_wanted_book()
        form.instance.sender = self.request.user
        form.instance.recipient = wanted_book.owner
        return form


class NegotiateOfferView(LoginRequiredMixin, AuthorizationRequiredMixin, UpdateView):
    template_name = 'offer/negotiate_offer.html'
    form_class = NegotiateOfferForm
    model = Offer
    context_object_name = 'offer'
    success_url = reverse_lazy('show_offer_list')
    authorizing_fields = ['recipient']

    def form_valid(self, form):
        """Deactivate old offer"""
        obj = form.save(commit=False)
        obj.is_active = False
        obj.save()
        """Create new offer"""
        obj.is_active = True
        obj.previous_offer = self.get_old_offer()
        obj.sender, obj.recipient = obj.recipient, obj.sender
        obj.pk = None
        return super().form_valid(form)

    def get_old_offer(self):
        return Offer.objects.filter(pk=self.kwargs.get('pk')).first()


class ShowOfferDetailsView(LoginRequiredMixin, AuthorizationRequiredMixin, DetailView):
    model = Offer
    context_object_name = 'offer'
    template_name = 'offer/show_offer_details.html'
    authorizing_fields = ['sender', 'recipient']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offer = self.get_object()
        is_my_offer = self.request.user == offer.sender
        context['is_my_offer'] = is_my_offer
        context['my_books'] = offer.sender_books.all() if is_my_offer else offer.recipient_books.all()
        context['others_books'] = offer.sender_books.all() if not is_my_offer else offer.recipient_books.all()
        return context


class ShowOffersView(LoginRequiredMixin, PaginationShowMixin, ListView):
    template_name = 'offer/show_offers_list.html'
    context_object_name = 'offers'
    model = Offer
    paginate_by = 40

    def get_queryset(self):
        return Offer.objects.prefetch_related('recipient', 'sender').filter(
            Q(recipient=self.request.user) | Q(sender=self.request.user))
