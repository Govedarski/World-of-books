from django.contrib import admin

# Register your models here.
from my_project.library.models import Book, Category


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass