from django.contrib import admin
from django.db.models import Count, Q

from my_project.library.models import Book, Category


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author',
                    'owner', 'previous_owner', 'next_owner', 'number_of_ex_owners', 'number_of_likes', 'is_tradable')
    list_display_links = ('id', 'title',)
    list_filter = ('category', 'is_tradable')
    list_per_page = 20
    search_fields = ('title', 'author',)
    sortable_by = list_display
    readonly_fields = ('number_of_likes', 'number_of_ex_owners')
    readonly_fields_owner_info = ('owner', 'next_owner', 'previous_owner', 'ex_owners', 'likes')
    fieldsets = (
        ("Book's info",
         {'fields': (('title', 'author', 'category', 'is_tradable',),),
          }
         ),
        ("Image",
         {'fields': (('image',),),
          'classes': ['collapse', ],
          }
         ),
        ("'Owner's history",
         {'fields': (('owner', 'next_owner', 'previous_owner', 'ex_owners', 'number_of_ex_owners'),),
          'classes': ['collapse', ],
          }
         ),
        ("Likes",
         {'fields': (('likes', 'number_of_likes'),),
          'classes': ['collapse', ],
          }
         ),
    )

    def view_on_site(self, obj):
        return obj.get_absolute_url()

    @staticmethod
    def lost_permission_check(func):
        '''Admin lost his permissions if
        he has accepted offer for this book'''

        def wrapper(instance, request, obj=None, *args, **kwargs):
            result = func(instance, request, obj=None, *args, **kwargs)
            if obj and request.user in [obj.next_owner, obj.previous_owner]:
                return False
            return result

        return wrapper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('likes', 'ex_owners', 'owner') \
            .annotate(like_count=Count('likes'), ex_owners_count=Count('ex_owners'))

    def number_of_ex_owners(self, inst):
        return inst.ex_owners_count

    number_of_ex_owners.admin_order_field = 'ex_owners_count'

    def number_of_likes(self, inst):
        return inst.like_count

    number_of_likes.admin_order_field = 'like_count'

    def get_readonly_fields(self, request, *args, **kwargs):
        book = args[0]
        if not request.user.is_superuser or request.user == book.owner:
            return self.readonly_fields + self.readonly_fields_owner_info
        return self.readonly_fields

    @lost_permission_check
    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj)

    @lost_permission_check
    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'books_in')
    list_display_links = ('id',)
    ordering = ('id',)
    sortable_by = ('id', 'name', 'books_in')
    search_fields = ('name',)
    list_per_page = 20
    list_editable = ('name',)

    class Meta:
        verbose_name_plural = "Categories"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('book_set').annotate(book_count=Count('book'))

    def books_in(self, inst):
        return inst.book_count

    books_in.admin_order_field = 'book_count'
