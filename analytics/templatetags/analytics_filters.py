from django import template

register = template.Library()

@register.filter(name='div')
def div(value, arg):
    """Divides the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
    
@register.filter(name='mul')
def mul(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0
    
@register.filter(name='sub')
def sub(value, arg):
    """Subtracts the argument from the value"""
    try:
        return float(value) - float(arg)
    except ValueError:
        return 0
    
@register.filter(name='add')
def add(value, arg):
    """Adds the argument to the value"""
    try:
        return float(value) + float(arg)
    except ValueError:
        return 0
