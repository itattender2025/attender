from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    return dictionary.get(key, "A")
@register.filter
def get_item(dictionary, key):
    """Returns the value of a dictionary using a dynamic key in Django templates"""
    return dictionary.get(key, "")