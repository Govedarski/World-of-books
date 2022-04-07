from django import template

register = template.Library()

@register.inclusion_tag("common/tags/paginate_pages.html", takes_context=True)
def pagination(context):
    return context
