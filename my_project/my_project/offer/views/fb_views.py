from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from my_project.common.models import Notification
from my_project.offer.models import Offer


def deactivate_offer(pk):
    offer = Offer.objects.filter(pk=pk).first()
    offer.is_active = False
    offer.save()
    return offer


def check_offer(request, offer):
    '''Check if all books still belong to offer's sender and recipient'''
    s_missing_books = [book for book in offer.sender_books.all() if not book.owner == offer.sender]
    r_missing_books = [book for book in offer.recipient_books.all() if not book.owner == offer.recipient]
    context = {'offer': offer}
    if s_missing_books or r_missing_books:
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
    offer = deactivate_offer(pk)
    redirect_to_inactive = check_offer(request, offer)
    if redirect_to_inactive:
        return redirect_to_inactive

    change_books_owner(offer.sender_books.all(), offer.recipient)
    change_books_owner(offer.recipient_books.all(), offer.sender)
    offer.is_accept = True
    offer.save()

    '''Create new notification'''
    recipient = offer.recipient if request.user == offer.sender else offer.sender
    massage = f'{request.user} accept your offer {offer.pk}!'
    notification = Notification(
        sender=request.user,
        recipient=recipient,
        offer=offer,
        massage=massage,
        is_answered=True
    )
    notification.save()
    '''Return to render'''
    return redirect('show_offer_details', pk=pk)


@login_required
def decline_offer_view(request, pk):
    '''Deactivate offer'''
    offer = deactivate_offer(pk)
    '''Create new notification'''
    recipient = offer.recipient if request.user == offer.sender else offer.sender
    massage = f'{request.user} canceled offer {offer.pk}!'
    notification = Notification(
        sender=request.user,
        recipient=recipient,
        offer=offer,
        massage=massage,
        is_answered=True
    )
    notification.save()
    '''Return to notifications'''
    return redirect('show_offer_details', pk=pk)
