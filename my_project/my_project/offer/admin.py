from django.contrib import admin

# Register your models here.
from my_project.offer.models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    pass

