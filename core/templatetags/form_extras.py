from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    existing = field.field.widget.attrs.get('class', '') if hasattr(field, 'field') else ''
    combined = (existing + ' ' + css).strip()
    return field.as_widget(attrs={**getattr(field.field.widget, 'attrs', {}), 'class': combined})
