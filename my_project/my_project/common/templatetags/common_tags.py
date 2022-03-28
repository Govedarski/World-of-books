from django import template

from my_project.library.models import Book

register = template.Library()


@register.inclusion_tag("common/tags/paginate_pages.html", takes_context=True)
def pagination(context):
    return context
