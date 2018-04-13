from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import TemplateView
from costs.models import Costs
from cart.models import Vente
from inventory.models import Article, Branch
from .forms import DateForm
from .charts import BarChart


class MainBalanceView(TemplateView):
    template_name = 'dashboard/main.html'


    def get_context_data(self, start_date=None, end_date=None):
        #context = super().get_context_data(**kwargs)
        grand_total_costs =  Costs.objects.grand_total(start_date=start_date, end_date=end_date)
        purchases = Article.objects.total_purchasing_price(start_date=start_date, end_date=end_date)
        costs = Costs.objects.total_costs(start_date=start_date, end_date=end_date)
        sellings = Vente.objects.total_sellings(start_date=start_date, end_date=end_date)
        balance  = Costs.objects.get_balance(start_date=start_date, end_date=end_date)

        barchart = BarChart()
        barchart.grand_total_costs = -(grand_total_costs)
        barchart.purchases = -(purchases)
        barchart.costs = -(costs)
        barchart.sellings = sellings
        barchart.balance = balance

        context = {'grand_total_costs': grand_total_costs,
                   'purchases': purchases,
                   'costs': costs,
                   'total_sellings': sellings,
                   'balance': balance,
                   'branches': Branch.objects.all(),
                   'articles_count': Article.objects.count(),
                   'barchart': barchart,
                   }
        return context

    def get(self, request, start_date=None, end_date=None):
        d1 = request.GET.get('start_date')
        d2 = request.GET.get('end_date')
        if d1 or d2:
            form = DateForm(request.GET)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                context = self.get_context_data(start_date, end_date)
                context['form'] = form
        else:
            context = self.get_context_data()
            context['form'] = DateForm()
        return render(request=request, template_name='dashboard/main.html', context=context)


def branch_dashboard(request, pk, start_date=None, end_date=None):
    template_name = 'dashboard/branch.html'
    branch = get_object_or_404(Branch, pk=pk)
    d1 = request.GET.get('start_date')
    d2 = request.GET.get('end_date')
    if d1 or d2:
        form = DateForm(request.GET)
        if form.is_valid():
            d1 = form.cleaned_data['start_date']
            d2 = form.cleaned_data['end_date']
    else:
        form = DateForm()
    context = {'grand_total_costs': Costs.objects.grand_total(branch=branch, start_date=d1, end_date=d2),
               'purchases': Article.objects.total_purchasing_price(branch=branch, start_date=d1, end_date=d2),
               'costs': Costs.objects.total_costs(branch=branch, start_date=d1, end_date=d2),
               'total_sellings': Vente.objects.total_sellings(branch=branch, start_date=d1, end_date=d2),
               'balance': Costs.objects.get_balance(branch=branch, start_date=d1, end_date=d2),
               'branch' : branch,
               'articles_count' : Article.objects.filter(branch=branch).count(),
               'form' : form
               }
    return render(request=request, template_name=template_name, context=context)
