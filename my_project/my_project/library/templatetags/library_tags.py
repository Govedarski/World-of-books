from django import template

from my_project.library.models import Book

register = template.Library()


@register.inclusion_tag("library/tags/one_book_details.html")
def book_details(pk):
    return {"book": Book.objects.filter(pk=pk)[0]}


@register.inclusion_tag("library/tags/book_list.html", takes_context=True)
def book_list(context):
    return context
