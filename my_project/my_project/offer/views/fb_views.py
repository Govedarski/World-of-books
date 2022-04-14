from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from my_project.offer.models import Offer


def get_offer(request, pk):
    offer = Offer.objects.filter(pk=pk).first()
    if not offer.recipient == request.user:
        raise PermissionDenied
    offer.is_active = False
    return offer


def check_offer(request, offer):
    '''Check if all books still belong to offer's sender and recipient'''
    s_missing_books = [book for book in offer.sender_books.all() if not book.owner == offer.sender]
    r_missing_books = [book for book in offer.recipient_books.all() if not book.owner == offer.recipient]
    context = {'offer': offer}

    if s_missing_books or r_missing_books:
        offer = get_offer(request, offer.pk)
        offer.save()
        context['s_missing_books'] = s_missing_books
        context['r_missing_books'] = r_missing_books
        return render(request, 'offer/inactive_offer.html', context)


def change_books_owner(books, new_owner):
    for book in books:
        book.ex_owners.add(book.owner)
        book.previous_owner = book.owner
        book.next_owner = new_owner
        book.owner = None
        book.save()
    return books


@login_required
def accept_offer_view(request, pk):
    offer = get_offer(request, pk)

    redirect_to_inactive = check_offer(request, offer)
    if redirect_to_inactive:
        return redirect_to_inactive

    change_books_owner(offer.sender_books.all(), offer.recipient)
    change_books_owner(offer.recipient_books.all(), offer.sender)
    offer.is_accept = True
    offer.save()

    return redirect('show_offer_details', pk=pk)


@login_required
def decline_offer_view(request, pk):
    offer = get_offer(request, pk)
    offer.save()
    return redirect('show_offer_details', pk=pk)
