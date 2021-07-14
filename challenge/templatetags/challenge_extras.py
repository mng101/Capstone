# Currency filter
# Source: djangosnippets
# URL: https://djangosnippets.org/snippets/552/

from django import template
import locale

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.filter()
def currency(value):
    if value:
        return locale.currency(value, grouping=True)
    else:
        return locale.currency(0.00, grouping=True)
