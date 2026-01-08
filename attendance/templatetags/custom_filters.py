from django import template

register = template.Library()


@register.filter
def split_lines(text):
    """Split text by newlines and return a list of non-empty lines"""
    if not text:
        return []
    lines = text.split('\n')
    # Filter out empty lines and strip whitespace
    return [line.strip() for line in lines if line.strip()]
