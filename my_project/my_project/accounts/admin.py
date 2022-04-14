from django.contrib import admin
# Register your models here.
from django.contrib.auth import get_user_model
from django.db.models import Count

from my_project.accounts.models import Profile, ContactForm


class ProfileInline(admin.StackedInline):
    model = Profile
    classes = ['collapse']

    def has_delete_permission(self, request, obj=None):
        return None


class ContactFormInline(admin.TabularInline):
    model = ContactForm
    classes = ['collapse']

    def has_delete_permission(self, request, obj=None):
        return None


class ContactFormFilter(admin.SimpleListFilter):
    title = ('is contact form done')
    parameter_name = 'is_cf_done'

    def lookups(self, request, model_admin):
        return (
            ('True', ('True')),
            ('False', ('False')),
        )

    def queryset(self, request, queryset):
        contact_forms = ContactForm.objects.all()
        print(self.value())
        if self.value() == 'True':
            contact_forms = [cf for cf in contact_forms if cf.is_completed]
        elif self.value() == 'False':
            contact_forms = [cf for cf in contact_forms if not cf.is_completed]
        return queryset.filter(contactform__in=contact_forms)


@admin.register(get_user_model())
class UserModelAdmin(admin.ModelAdmin):
    view_on_site = True
    inlines = (ProfileInline, ContactFormInline)
    list_display_staff = ('id', 'username', 'name', 'is_contact_form_done', 'books_number', 'is_staff')
    list_display_superuser_extra = ('is_staff', 'is_superuser')
    list_display_links = ('id', 'username')
    list_filter_staff = ('username', ContactFormFilter)
    list_filter_superuser_extra = ('is_staff', 'is_superuser')
    list_per_page = 20
    search_fields = ('username', 'profile__first_name', 'last__first_name')
    sortable_by = ('id', 'username', 'name', 'books_number')

    PRIMARY_FIELDS_DESCRIPTION = 'Very important fields'
    exclude = ['password']

    fieldsets_staff = (
        ('AUTHENTICATION INFO',
         {'fields': (('username', 'email'), 'is_active',),
          'description': f'{PRIMARY_FIELDS_DESCRIPTION}',
          }
         ),
    )
    fieldsets_superuser_extra = (
        ('ROLES',
         {'fields': ('is_superuser',),
          'classes': ['collapse', ],
          }
         ),
        ('GROUPS',
         {'fields': ('groups',),
          'classes': ['collapse in', ],
          }
         ),
    )

    def get_list_display(self, request, ):
        if request.user.is_superuser:
            return self.list_display_staff + self.list_display_superuser_extra
        return self.list_display_staff

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return self.fieldsets_staff + self.fieldsets_superuser_extra
        return self.fieldsets_staff

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return self.list_filter_staff + self.list_filter_superuser_extra
        return self.list_filter_staff

    @admin.display(empty_value='unknown')
    def name(self, obj):
        return obj.PROFILE.full_name

    @admin.display(boolean=True)
    def is_contact_form_done(self, obj):
        return obj.contactform.is_completed

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('own_books', 'profile', 'contactform') \
            .annotate(books_count=Count('own_books'))
        return qs

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_staff and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def books_number(self, inst):
        return inst.books_count

    books_number.admin_order_field = 'books_count'
