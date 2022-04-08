from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model

from my_project.accounts.models import Profile, ContactForm


@admin.register(get_user_model())
class UserModelAdmin(admin.ModelAdmin):
    PRIMARY_FIELDS_DESCRIPTION = 'Very important fields'
    exclude = ['password']
    fieldsets = (
        ('Primary fields',
         {'fields': (('username', 'email'),),
          'description': f'{PRIMARY_FIELDS_DESCRIPTION}'}
         ),
        ('Secondary fields',
         {'fields': ('is_active',),
          'classes': ('collapse',), }
         ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    pass

