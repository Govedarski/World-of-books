from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from my_project.common.helpers.custom_mixins import PaginationShowMixin, AuthorizationRequiredMixin
from my_project.common.models import Notification
from my_project.library.forms import SearchForm, BookForm, UsersListForm
from my_project.library.models import Book, Category

UserModel = get_user_model()


class ShowBookListView(PaginationShowMixin, ListView):
    template_name = 'library/book_list.html'
    model = Book
    context_object_name = 'books'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm(
            initial={
                'search': self.search,
                'search_by': self.search_by}
        )
        context['ord'] = self.order
        context['ord_by'] = self.ord_by
        context['search'] = self.search
        context['search_by'] = self.search_by
        return context

    def get_queryset(self):
        query_set = Book.objects.prefetch_related('owner', 'category', 'likes').filter(
            owner__isnull=False, owner__is_active=True).annotate(like_count=Count('likes')).order_by(
            '-like_count', 'title')
        if self.search_by == SearchForm.SearchByChoices.owner:
            owner = UserModel.objects.filter(username__icontains=self.search)
            query_set = query_set.filter(owner__in=owner)
        elif self.search_by:
            query_filter = {f'{self.search_by}__icontains': self.search}
            query_set = query_set.filter(**query_filter)
        if self.ord_by:
            query_set = query_set.order_by(self.ord_by)
            if self.order:
                query_set = query_set.reverse()
        return query_set

    @property
    def order(self):
        return self.request.GET.get("ord", '') if self.request.GET else '-'

    @property
    def ord_by(self):
        return self.request.GET.get("ord_by", '')

    @property
    def search(self):
        return self.request.GET.get("search", '')

    @property
    def search_by(self):
        return self.request.GET.get("search_by", '')


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
            f"{owner.nickname}'s book"
        return context

    def get_queryset(self):
        field = self._get_query_filter_field()
        owner = self._get_owner()
        search = self.request.GET.get("search", '')
        query_filter = {field: owner,
                        'title__icontains': search}
        query_set = Book.objects.prefetch_related(field).filter(**query_filter)
        return query_set

    def _get_owner(self):
        pk = self.kwargs.get('pk', self.request.user.pk)
        return get_object_or_404(UserModel, pk=pk)

    @staticmethod
    def _get_query_filter_field():
        return ''


class ShowBooksDashboardView(ShowBookView):
    def _get_query_filter_field(self):
        return 'owner'


class ShowBooksOnAWayView(LoginRequiredMixin, ShowBookView):
    TITLE = 'Books on the way to you'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.TITLE
        return context

    def _get_query_filter_field(self):
        return 'next_owner'


class ShowBooksToSendView(LoginRequiredMixin, ShowBookView):
    TITLE = 'Books you have to send!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.TITLE
        return context

    def _get_query_filter_field(self):
        return 'previous_owner'


class CreateBookView(LoginRequiredMixin, CreateView):
    template_name = 'library/create_book.html'
    form_class = BookForm

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        if self.request.user.is_authenticated and not self.request.user.contactform.is_completed:
            return redirect(reverse_lazy('edit_contacts') + f"?next={self.request.path}#edit")
        return result

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.category = self._set_category(form)
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.request.user.pk
        default_redirect = reverse_lazy('show_books_dashboard', kwargs={'pk': pk})
        next_page = self.request.GET.get('next')
        return next_page if next_page else default_redirect

    @staticmethod
    def _set_category(form):
        category = form.cleaned_data.get('category')
        category_name = form.cleaned_data.get('category_name')
        if category or not category_name:
            return category
        new_category, created = Category.objects.get_or_create(name=category_name)
        return new_category


class DetailsBookView(DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'library/book_details.html'

    def dispatch(self, request, *args, **kwargs):
        book = self.get_object()
        if not (book.owner or book.next_owner or self.request.user.has_perm('library.view_book')):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_staff_edit'] = self.request.user.has_perm('library.view_book')
        return context

    def post(self, *args, **kwargs):
        book = self.get_object()
        if not self.request.user == book.owner:
            raise PermissionDenied
        book.is_tradable = not book.is_tradable
        book.save()
        return redirect(self.request.path)

    def get_template_names(self):
        book = self.get_object()
        template_name = super().get_template_names()
        if self.request.user == book.next_owner:
            template_name = 'library/book_to_receive_info.html'
        if self.request.user == book.previous_owner:
            template_name = 'library/book_to_send_info.html'
        return template_name


class EditBookView(LoginRequiredMixin, AuthorizationRequiredMixin, UpdateView):
    template_name = 'library/edit_book.html'
    form_class = BookForm
    model = Book
    authorizing_fields = ['owner']

    def get_success_url(self):
        return reverse_lazy('book_details', kwargs=self.kwargs)


class DeleteBookView(LoginRequiredMixin, AuthorizationRequiredMixin, DeleteView):
    template_name = 'library/delete_book.html'
    model = Book
    form_class = UsersListForm
    authorizing_fields = ['owner']

    def get(self, *args, **kwargs):
        choices = [(0, 'nobody')] + [(user.pk, user.username) for user in
                                     UserModel.objects.exclude(pk=self.request.user.pk)]
        self.form_class.base_fields['user'].choices = choices
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        user_pk = self.request.POST.get('user')
        book = self.get_object()
        book.ex_owners.add(book.owner)
        book.owner = None
        book.save()
        if not user_pk == '0':
            user = UserModel.objects.get(pk=user_pk)
            Notification.create_notification_for_deleted_book(
                kwargs={'sender': self.request.user,
                        'recipient': user,
                        'book': book, }
            )
        return redirect(self.get_success_url())

    def get_success_url(self):
        pk = self.request.user.pk
        return reverse_lazy('show_books_dashboard', kwargs={'pk': pk})
