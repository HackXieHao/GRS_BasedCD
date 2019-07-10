from django import template
register = template.Library()
i=0
@register.filter(name='forlist')
def forlist(value,i):
    # global i
    if i<=len(value):
        value = value[i - 1]
        i=i+1
        return str(value)
    else:
        return "0"