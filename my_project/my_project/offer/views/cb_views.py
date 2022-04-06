from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView

from my_project.common.helpers.mixins import PaginationShowMixin, AuthorizationRequiredMixin
from my_project.common.models import Notification
from my_project.library.models import Book
from my_project.offer.forms import CreateOfferForm, NegotiateOfferForm
from my_project.offer.models import Offer


class CreateOfferView(LoginRequiredMixin, CreateView):
    template_name = 'offer/create_offer.html'
    form_class = CreateOfferForm
    success_url = reverse_lazy('show_home')

    def get_initial(self):
        wanted_book = self.__get_wanted_book()
        sender = self.request.user
        recipient = wanted_book.owner
        return {
            'wanted_book': wanted_book,
            'sender': sender,
            'recipient': recipient,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.__get_wanted_book()
        return context

    def form_valid(self, form):
        form = self.__create_valid_form(form)
        result = super().form_valid(form)
        offer = self.object
        offer.recipient_books.add(self.__get_wanted_book())
        offer.save()
        self.__send_notification(offer)
        return result

    def __get_wanted_book(self):
        return Book.objects.get(pk=self.kwargs.get('pk'))

    def __create_valid_form(self, form):
        wanted_book = self.__get_wanted_book()
        form.instance.sender = self.request.user
        form.instance.recipient = wanted_book.owner
        return form

    def __send_notification(self, offer):
        notification = Notification(
            sender=offer.sender,
            recipient=offer.recipient,
            book=self.__get_wanted_book(),
            offer=offer,
            massage=self.__get_notification_massage(offer),
        )
        notification.save()

    def __get_notification_massage(self, offer):
        return f'{offer.sender} makes offer for your book {self.__get_wanted_book()}' \
               f'{" and others" if len(offer.recipient_books.all()) > 1 else ""}'


class NegotiateOfferView(LoginRequiredMixin, AuthorizationRequiredMixin, UpdateView):
    template_name = 'offer/negotiate_offer.html'
    form_class = NegotiateOfferForm
    model = Offer
    context_object_name = 'offer'
    success_url = reverse_lazy('show_notifications')
    authorizing_fields = ['recipient']

    def form_valid(self, form):
        """Deactivate old offer"""
        obj = form.save(commit=False)
        obj.is_active = False
        obj.save()
        """Create new offer"""
        obj.is_active = True
        obj.previous_offer = self.old_offer
        obj.sender, obj.recipient = obj.recipient, obj.sender
        obj.pk = None
        return super().form_valid(form)

    def get_success_url(self):
        self.__send_notification()
        return super().get_success_url()

    def __send_notification(self):
        notification = Notification(
            sender=self.request.user,
            recipient=self.__get_recipient(),
            offer=self.object,
            massage=self.__get_notification_massage(),
        )
        notification.save()

    def __get_notification_massage(self):
        return f'{self.request.user} makes counter offer to your offer {self.old_offer.pk}'

    def __get_recipient(self):
        return self.object.recipient if self.request.user == self.object.sender else self.object.sender

    @property
    def old_offer(self):
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


class ShowOfferView(LoginRequiredMixin, PaginationShowMixin,  ListView):
    template_name = 'offer/show_offers_list.html'
    context_object_name = 'offers'
    model = Offer
    paginate_by = 40

    def get_queryset(self):
        return Offer.objects.filter(Q(recipient=self.request.user) | Q(sender=self.request.user))

