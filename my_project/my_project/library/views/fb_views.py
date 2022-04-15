from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from my_project.common.models import Notification
from my_project.library.models import Book


def get_object_or_raise_exception(my_model, pk, user, field):
    my_obj = get_object_or_404(my_model, pk=pk)
    if not user == getattr(my_obj, field):
        raise PermissionDenied()
    return my_obj


def is_answer_already(notification):
    massage = "You answer this notification already"
    if notification.is_answered:
        raise PermissionDenied(massage)


@login_required()
def like_book_view(request, pk):
    back = request.GET.get('back', '/')
    access_denied_massage = 'You cannot like your own picture'

    book = get_object_or_404(Book, pk=pk)
    if request.user == book.owner:
        raise PermissionDenied(access_denied_massage)

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


@login_required()
def accept_delete_book_view(request, pk):
    access_grant_field = 'recipient'
    notification = get_object_or_raise_exception(Notification, pk, request.user, access_grant_field)
    book = notification.book
    if not book:
        raise Http404

    is_answer_already(notification)
    notification.is_answered = True
    notification.save()

    book.next_owner = request.user
    book.previous_owner = book.ex_owners.last()
    book.save()

    return redirect('show_books_on_a_way')


@login_required()
def reject_delete_book_view(request, pk):
    access_grant_field = 'recipient'
    notification = get_object_or_raise_exception(Notification, pk, request.user, access_grant_field)
    book = notification.book
    if not book:
        raise Http404
    is_answer_already(notification)

    notification.is_answered = True
    notification.save()
    return redirect('show_notifications')


@login_required()
def receive_book_view(request, pk):
    access_grant_field = 'next_owner'
    book = get_object_or_raise_exception(Book, pk, request.user, access_grant_field)

    book.owner = book.next_owner
    book.previous_owner = None
    book.next_owner = None
    if request.user in book.likes.all():
        book.likes.remove(request.user)
    book.save()
    return redirect('show_books_dashboard', pk=request.user.pk)
