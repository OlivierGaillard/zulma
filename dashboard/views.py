from django.shortcuts import render, reverse
from django.views.generic import TemplateView
from costs.models import Costs
from cart.models import Vente

class MainBalanceView(TemplateView):
    template_name = 'dashboard/main.html'


    def get(self, request, *args, **kwargs):
        context = {'grand_total_costs' : Costs.objects.grand_total(),
                   'total_sellings' : Vente.objects.total_sellings(),
                   'balance' : Costs.objects.get_balance()}
        return render(request=request, template_name='dashboard/main.html', context=context)
