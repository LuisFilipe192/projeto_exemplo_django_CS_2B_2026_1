from django import template
import re
register = template.Library()

@register.filter
def regex_replace(value, pattern):
    """Remove caracteres usando regex: {{ value|regex_replace:'\\D' }}"""
    return re.sub(pattern, '', value)
