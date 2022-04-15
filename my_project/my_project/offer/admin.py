from django.contrib import admin

# Register your models here.
from my_project.offer.models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'received_date', 'sender', 'recipient', 'is_accept', 'is_active',
        'previous_offer')

    list_filter = ('is_accept', 'is_active',)
    list_per_page = 20
    search_fields = ('sender', 'recipient',)
    sortable_by = ('__str__', 'received_date', 'sender', 'recipient', 'previous_offer')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('sender', 'sender_books', 'recipient', 'recipient_books', 'previous_offer')
