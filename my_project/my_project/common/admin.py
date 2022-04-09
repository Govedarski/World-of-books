from django.contrib import admin

# Register your models here.
from my_project.common.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'received_date', 'massage', 'sender', 'recipient', 'is_read', 'is_book', 'is_offer')
    list_display_links = ('id', 'massage')
    list_filter = ('sender', 'recipient',)
    list_per_page = 20
    search_fields = ('massage',)
    sortable_by = ('id', 'received_date', 'sender', 'recipient', 'is_read', 'is_book', 'is_offer')

    @admin.display(boolean=True)
    def is_offer(self, obj):
        return bool(obj.offer)

    @admin.display(boolean=True)
    def is_book(self, obj):
        return bool(obj.book)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('offer', 'book')
