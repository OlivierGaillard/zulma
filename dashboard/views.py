from django.shortcuts import render, reverse
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
                   'branches' : Branch.objects.all()}
        return render(request=request, template_name='dashboard/main.html', context=context)
