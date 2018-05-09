from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from costs.models import Costs
from cart.models import Vente
from inventory.models import Article, Branch, Losses
from .forms import DateForm
from .charts import BarChart


def build_context_data_for_main(start_date=None, end_date=None):
    """
    Ambiguity here: does 'MAIN',  because the param 'branch' does not exist,
    mean ALL, main included, or MAIN excluded?
    :param start_date:
    :param end_date:
    :return:
    """
    #purchases = 5000
    purchases = Article.objects.total_purchasing_price(start_date=start_date, end_date=end_date)
    costs_main = Costs.objects.total_costs(branch="MAIN", start_date=start_date, end_date=end_date)
    costs  = Costs.objects.total_costs(start_date=start_date, end_date=end_date)
    losses_main = Losses.objects.total_costs(branch="MAIN", start_date=start_date, end_date=end_date)
    losses = Losses.objects.total_costs(start_date=start_date, end_date=end_date)
    sellings = Vente.objects.total_sellings(start_date=start_date, end_date=end_date)

    grand_total_costs = purchases + costs + losses
    balance = sellings - grand_total_costs
    barchart = BarChart()
    barchart.purchases = -(purchases)
    barchart.costs = -(costs)
    barchart.losses = -(losses)
    barchart.all_costs = -(grand_total_costs)
    barchart.sellings = sellings
    barchart.balance = balance

    articles_count = Article.objects.all().count()

    context = {'grand_total_costs': grand_total_costs,
               'purchases': purchases,
               'costs': costs,
               'costs_main': costs_main,
               'losses' : losses,
               'losses_main': losses_main,
               'total_sellings': sellings,
               'balance': balance,
               'articles_count': articles_count,
               'barchart': barchart,
               }
    return context


def build_context_data_for_branch(branch=None, start_date=None, end_date=None):
    """
    Holds data for one branch other than 'MAIN'.
    :param branch:
    :param start_date:
    :param end_date:
    :return:
    """
    purchases = Article.objects.total_purchasing_price(branch=branch, start_date=start_date, end_date=end_date)
    costs = Costs.objects.total_costs(branch=branch, start_date=start_date, end_date=end_date)
    losses = Losses.objects.total_costs(branch=branch, start_date=start_date, end_date=end_date)
    grand_total_costs = purchases + costs + losses
    sellings = Vente.objects.total_sellings(branch=branch, start_date=start_date, end_date=end_date)
    balance = Costs.objects.get_balance(branch=branch, start_date=start_date, end_date=end_date)



    barchart = BarChart()
    barchart.grand_total_costs = -(costs + losses)
    barchart.purchases = -(purchases)
    barchart.costs = -(costs)
    barchart.losses = -(losses)
    barchart.all_costs = -(grand_total_costs)
    barchart.sellings = sellings
    barchart.balance = balance

    if branch:
        articles_count = Article.objects.filter(branch=branch).count()
    else:
        articles_count = Article.objects.all().count()

    context = {'grand_total_costs': grand_total_costs,
               'purchases': purchases,
               'costs': costs,
               'losses' : losses,
               'total_sellings': sellings,
               'balance': balance,
               'branches': Branch.objects.all(),
               'articles_count': articles_count,
               'barchart': barchart,
               }
    return context

@method_decorator(login_required, name='dispatch')
class MainBalanceView(TemplateView):
    template_name = 'dashboard/main.html'


    def get_context_data(self, start_date=None, end_date=None):
        context = build_context_data_for_main(start_date=start_date, end_date=end_date)
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

login_required()
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
            context = build_context_data_for_branch(branch=branch, start_date=d1, end_date=d2)
            context['form'] = form
        else:
            context = {'form': form}
            render(request=request, template_name='dashboard/branch.html', context=context)
    else:
        form = DateForm()
        context = build_context_data_for_branch(branch=branch)
        context['form'] = form
    context['branch'] = branch
    return render(request=request, template_name=template_name, context=context)
