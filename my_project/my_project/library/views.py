from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import Lower
from django.http import Http404
from django.shortcuts import redirect
# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from my_project.common.helpers.mixins import PaginationShowMixin
from my_project.common.models import Notification
from my_project.library.forms import CreateBookForm, UsersListForm, SearchForm
from my_project.library.models import Book


class ShowBookListView(PaginationShowMixin, ListView):
    template_name = 'library/book_list.html'
    model = Book
    context_object_name = 'books'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.request.GET.get("ord", '') if self.request.GET else '-'
        ord_by = self.request.GET.get("ord_by", '')
        search = self.request.GET.get("search", '')
        search_by = self.request.GET.get("search_by", '')
        context['form'] = SearchForm(
            initial={
                'search': search,
                'search_by': search_by}
        )
        context['ord'] = order
        context['ord_by'] = ord_by
        context['search'] = search
        context['search_by'] = search_by
        return context

    def get_queryset(self):
        query_set = super().get_queryset().filter(owner__isnull=False).annotate(like_count=Count('likes')).order_by(
            '-like_count')
        order = self.request.GET.get("ord", '')
        order_by = self.request.GET.get("ord_by", '')
        search = self.request.GET.get("search", '')
        search_by = self.request.GET.get("search_by", '')

        if search_by == SearchForm.SearchByChoices.owner:
            owner = get_user_model().objects.filter(username__icontains=search)
            query_set = query_set.filter(owner__in=owner)
        elif search_by:
            query_filter = {f'{search_by}__icontains': search}
            query_set = query_set.filter(**query_filter)
        if order_by:
            if order:
                query_set = query_set.order_by(Lower(order_by).desc())
            else:
                query_set = query_set.order_by(Lower(order_by))

        return query_set


class ShowBookView(PaginationShowMixin, ListView):
    template_name = 'library/show_books.html'
    context_object_name = 'books'
    model = Book
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", '')
        context['search'] = search
        owner = self._get_owner()
        context['owner'] = owner
        context['title'] = 'My books' \
            if owner == self.request.user else \
            f"{owner}'s book"
        return context

    def _get_owner(self):
        owner = get_user_model().objects.filter(pk=self.kwargs.get('pk'))
        owner = owner[0] if owner else self.request.user
        return owner

    def get_queryset(self):
        field = self._get_query_filter()
        owner = self._get_owner()
        search = self.request.GET.get("search", '')
        query_filter = {field: owner,
                        'title__icontains': search}
        query_set = Book.objects.filter(**query_filter)
        return query_set

    @staticmethod
    def _get_query_filter(self):
        return ''


class ShowBooksDashboardView(ShowBookView):
    def _get_query_filter(self):
        return 'owner'


class ShowBooksOnAWayView(ShowBookView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Books on a way to you'
        return context

    def _get_query_filter(self):
        return 'next_owner'


class ShowBooksToSendView(ShowBookView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Books you have to send!'
        return context

    def _get_query_filter(self):
        return 'previous_owner'


class CreateBookView(CreateView):
    template_name = 'library/create_book.html'
    form_class = CreateBookForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.request.user.pk
        return reverse_lazy('show_books_dashboard', kwargs={'pk': pk})


class DetailsBookView(DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'library/book_details.html'

    def dispatch(self, request, *args, **kwargs):
        book = self.get_object()
        if not book.owner and not book.next_owner:
            raise Http404("Book does not exist")
        if self.request.user == book.next_owner:
            self.template_name = 'library/receive_book_info.html'
        if self.request.user == book.previous_owner:
            self.template_name = 'library/book_to_send_info.html'
        # Todo if self.request.user is not book owner -> not authorized
        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        book = self.get_object()
        book.is_available = not book.is_available
        book.save()
        return self.render_to_response(context={'book': book})


class EditBookView(UpdateView):
    template_name = 'library/edit_book.html'
    form_class = CreateBookForm
    model = Book

    def get_success_url(self):
        return reverse_lazy('book_details', kwargs=self.kwargs)


class DeleteBookView(DeleteView):
    template_name = 'library/delete_book.html'
    model = Book
    form_class = UsersListForm

    def get(self, *args, **kwargs):
        choices = [(0, 'nobody')] + [(user.pk, user.username) for user in
                                     get_user_model().objects.exclude(pk=self.request.user.pk)]
        self.form_class.base_fields['user'].choices = choices
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        user_pk = self.request.POST.get('user')
        book = self.get_object()
        book.ex_owners.add(book.owner)
        book.owner = None
        book.save()
        if not user_pk == '0':
            user = get_user_model().objects.get(pk=user_pk)
            notification = Notification(
                sender=self.request.user,
                recipient=user,
                book=book,
                massage=self.__get_notification_massage()
            )
            notification.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        pk = self.request.user.pk
        return reverse_lazy('show_books_dashboard', kwargs={'pk': pk})

    def __get_notification_massage(self):
        return f'{self.request.user} send {self.get_object()} to you without deal between you?'


def like_book_view(request, pk):
    book = Book.objects.get(pk=pk)
    back = request.GET.get('back', '/')
    if request.user == book.owner:
        return redirect(back)

    notification = Notification(
        sender=request.user,
        recipient=book.owner,
        book=book,
        is_answered=True,
    )
    if request.user in book.likes.all():
        action = 'dislikes'
        book.likes.remove(request.user)
    else:
        action = 'likes'
        book.likes.add(request.user)

    notification.massage = f'{request.user} {action} your book {book}'
    book.save()
    notification.save()

    return redirect(back)


def accept_delete_book_view(request, pk):
    notification = Notification.objects.get(pk=pk)
    if not notification.recipient == request.user:
        return redirect('')  # Todo to unauthorized

    notification.is_answered = True
    notification.save()
    book = notification.book
    book.next_owner = request.user
    book.previous_owner = book.ex_owners.last()
    book.save()

    return redirect('show_books_dashboard', pk=request.user.pk)


def reject_delete_book_view(request, pk):
    notification = Notification.objects.get(pk=pk)
    if not notification.recipient == request.user:
        return redirect('')  # Todo to unauthorized

    notification.is_answered = True
    notification.save()
    return redirect('show_books_dashboard', pk=request.user.pk)


def receive_book_view(request, pk):
    book = Book.objects.get(pk=pk)
    book.owner = book.next_owner
    book.previous_owner = None
    book.next_owner = None
    if request.user in book.likes.all():
        book.likes.remove(request.user)
    book.save()
    return redirect('show_books_dashboard', pk=request.user.pk)
