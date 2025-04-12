from django import template
from django.utils.safestring import mark_safe
import markdown
from markdown.extensions import extra, codehilite, tables, fenced_code

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    if not text:
        return ""
    
    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty'
    ]
    
    html = markdown.markdown(
        text,
        extensions=extensions,
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
            }
        }
    )
    
    return mark_safe(html) 