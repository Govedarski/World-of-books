from datetime import date

from django import template

register = template.Library()


@register.inclusion_tag('accounts/tags/profile_info.html', takes_context=True)
def profile_info(context):
    return context


@register.inclusion_tag('accounts/tags/contact_info.html', takes_context=True)
def contacts_info(context):
    return context


@register.inclusion_tag('accounts/tags/email_info.html', takes_context=True)
def email_info(context):
    return context
