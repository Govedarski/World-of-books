from django import template

from my_project.library.models import Book

register = template.Library()


@register.inclusion_tag("library/tags/one_book_details.html", takes_context=True)
def book_details(context, pk):
    context['book'] = Book.objects.filter(pk=pk)[0]
    return context


@register.inclusion_tag("library/tags/book_list.html", takes_context=True)
def book_list(context):
    return context


@register.inclusion_tag("library/tags/like_button.html", takes_context=True)
def like_book(context):
    return context
