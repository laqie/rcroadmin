# coding=utf-8
from django import template
from django.utils.safestring import SafeUnicode

register = template.Library()

#@register.inclusion_tag("musers/_render_field.html")
#def render_field(field, cssclass='', fieldclass='', render_help=False):
#    label_tag = field.label_tag(attrs={'class': 'control-label'})
#    cssclass = cssclass if cssclass else 'span6'
#    attrs = {'class': cssclass}
#    if not render_help:
#        attrs.update(placeholder=field.help_text)
#
#    errors = field.errors
#    if field.name in ('email', 'alias', 'groups'):
#        attrs.update(rows=5)
#        attrs.update(size=10)
##        attrs['class'] = 'span6 disabled'
#    widget = field.as_widget(attrs=attrs)
#    return {'field': field,
#            'errors': errors,
#            'widget': widget,
#            'label_tag': label_tag,
#            'help_text': field.help_text if render_help else '',
#            'fieldclass': fieldclass,
#            'cssclass': cssclass,
#            }

@register.filter(name=u'size')
def sizify(value):
    """
    Simple kb/mb/gb size snippet for templates:

    {{ product.file.size|sizify }}
    """
    value = unicode(value)
    if value.isdigit():
        value = int(value)
    else:
        return value
    if value < 1024:
        ext = u'б'
    elif value < 512000:
        value /= 1024.0
        ext = u'Кб'
    elif value < 4194304000:
        value /= 1048576.0
        ext = u'Мб'
    else:
        value /= 1073741824.0
        ext = u'Гб'
    return u'%s %s' % (str(round(value, 2)), ext)
