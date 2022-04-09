from django import forms
from django.contrib import admin

# Register your models here.
from django.db import models
from django.db.models import Count

from my_project.library.models import Book, Category


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    view_on_site = True
    list_display = ('id', 'title', 'author',
                    'owner', 'is_tradable', 'number_of_ex_owners', 'number_of_likes')
    list_display_links = ('id', 'title',)
    list_filter = ('category', 'is_tradable')
    list_per_page = 20
    search_fields = ('title', 'author', 'owner',)
    sortable_by = list_display
    readonly_fields = ['number_of_likes', 'number_of_ex_owners']
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
        fields = super().get_readonly_fields(request, *args, **kwargs)
        if not request.user.is_superuser:
            fields.extend(['owner', 'next_owner', 'previous_owner', 'ex_owners', 'likes'])
        return fields


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
