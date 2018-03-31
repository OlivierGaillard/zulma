from django import template
from django.template.loader import get_template
from inventory.models import Branch


register = template.Library()

#@register.inclusion_tag('branches_menu.html')
def show_branches():
    branches = Branch.objects.all()
    return {'branches' : branches}


t = get_template('inventory/branches_menu.html')
register.inclusion_tag(t)(show_branches)
