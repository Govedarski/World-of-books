from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView

from my_project.common.models import Notification
from my_project.library.forms import CreateBookForm, UsersListForm, SearchForm
from my_project.library.models import Book


class ShowBookList(ListView):
    template_name = 'library/book_list.html'
    model = Book
    context_object_name = 'books'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        ord = self.request.GET.get("ord", '')
        ord_by = self.request.GET.get("ord_by", '')
        search = self.request.GET.get("search", '')
        search_by = self.request.GET.get("search_by", '')
        context['form'] = SearchForm(
            initial={
                'search': search,
                'search_by': search_by}
        )
        context['ord'] = ord
        context['ord_by'] = ord_by
        context['search'] = search
        context['search_by'] = search_by
        return context

    def get_queryset(self):
        query_set = super().get_queryset()
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
            query_set = query_set.order_by(f'{order}{order_by}')

        return query_set


class ShowBooksDashboardView(ListView):
    template_name = 'library/books_dashboard.html'
    context_object_name = 'books'
    model = Book
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(self.object_list) > self.paginate_by:
            context['see_more'] = True
        return context

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)


class CreateBookView(CreateView):
    template_name = 'library/create_book.html'
    form_class = CreateBookForm
    success_url = reverse_lazy('show_books_dashboard')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class DetailsBookView(DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'library/book_details.html'

    def post(self, *args, **kwargs):
        book = self.get_object()
        book.available = not book.available
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
    success_url = reverse_lazy('show_books_dashboard')

    def get(self, *args, **kwargs):
        default_choice = self.form_class.base_fields['user'].choices.copy()
        choice_to_remove = (self.request.user.pk, self.request.user.username)
        self.form_class.base_fields['user'].choices.remove(choice_to_remove)
        result = super().get(*args, **kwargs)
        self.form_class.base_fields['user'].choices = default_choice
        return result

    def post(self, *args, **kwargs):
        user_pk = self.request.POST.get('user')
        if user_pk == '0':
            return super().post(*args, **kwargs)

        user = get_user_model().objects.get(pk=user_pk)
        book_pk = self.kwargs.get('pk')
        book = Book.objects.get(pk=book_pk)
        book.owner = None
        book.save()
        notification = Notification(
            sender=self.request.user,
            recipient=user,
            book=book,
            type=Notification.TypeChoices.CHANGE_OWNER,
        )
        notification.save()
        return redirect(self.success_url)


def receive_book_view(request, pk):
    notification = Notification.objects.get(pk=pk)
    if not notification.recipient == request.user:
        return redirect('')  # Todo to unauthorized

    notification.is_answered = True
    notification.save()
    book = notification.book
    book.owner = request.user
    book.save()
    return redirect('show_books_dashboard')


def not_receive_book_view(request, pk):
    notification = Notification.objects.get(pk=pk)
    if not notification.recipient == request.user:
        return redirect('')  # Todo to unauthorized

    notification.is_answered = True
    notification.save()
    return redirect('show_books_dashboard')
