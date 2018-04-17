from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import TemplateView
from costs.models import Costs
from cart.models import Vente
from inventory.models import Article, Branch
from .forms import DateForm
from .charts import BarChart

def build_context_data(branch=None, start_date=None, end_date=None):
    grand_total_costs = Costs.objects.grand_total(branch=branch, start_date=start_date, end_date=end_date)
    purchases = Article.objects.total_purchasing_price(branch=branch, start_date=start_date, end_date=end_date)
    costs = Costs.objects.total_costs(branch=branch, start_date=start_date, end_date=end_date)
    sellings = Vente.objects.total_sellings(branch=branch, start_date=start_date, end_date=end_date)
    balance = Costs.objects.get_balance(branch=branch, start_date=start_date, end_date=end_date)

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

class MainBalanceView(TemplateView):
    template_name = 'dashboard/main.html'


    def get_context_data(self, start_date=None, end_date=None):
        context = build_context_data(start_date=start_date, end_date=end_date)
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
                context = {'form' : form }
                render(request=request, template_name='dashboard/main.html', context=context)
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
            context = build_context_data(branch=branch, start_date=d1, end_date=d2)
            context['form'] = form
        else:
            context = {'form': form}
            render(request=request, template_name='dashboard/branch.html', context=context)
    else:
        form = DateForm()
        context = build_context_data(branch=branch)
        context['form'] = form
    context['branch'] = branch
    return render(request=request, template_name=template_name, context=context)
