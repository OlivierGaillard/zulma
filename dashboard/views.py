from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import TemplateView
from costs.models import Costs
from cart.models import Vente
from inventory.models import Article, Branch


class MainBalanceView(TemplateView):
    template_name = 'dashboard/main.html'


    def get(self, request, *args, **kwargs):
        context = {'grand_total_costs' : Costs.objects.grand_total(),
                   'purchases' : Article.objects.total_purchasing_price(),
                   'costs' : Costs.objects.total_costs(),
                   'total_sellings' : Vente.objects.total_sellings(),
                   'balance' : Costs.objects.get_balance(),
                   'branches' : Branch.objects.all(),
                   'articles_count': Article.objects.count()
                   }
        return render(request=request, template_name='dashboard/main.html', context=context)


def branch_dashboard(request, pk):
    template_name = 'dashboard/branch.html'
    branch = get_object_or_404(Branch, pk=pk)
    context = {'grand_total_costs': Costs.objects.grand_total(branch=branch),
               'purchases': Article.objects.total_purchasing_price(branch=branch),
               'costs': Costs.objects.total_costs(branch=branch),
               'total_sellings': Vente.objects.total_sellings(branch=branch),
               'balance': Costs.objects.get_balance(branch=branch),
               'branch' : branch,
               'articles_count' : Article.objects.filter(branch=branch).count()
               }
    return render(request=request, template_name=template_name, context=context)
