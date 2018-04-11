from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import TemplateView
from costs.models import Costs
from cart.models import Vente
from inventory.models import Article, Branch
from .forms import DateForm


class MainBalanceView(TemplateView):
    template_name = 'dashboard/main.html'


    def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        context = {'grand_total_costs': Costs.objects.grand_total(),
                   'purchases': Article.objects.total_purchasing_price(),
                   'costs': Costs.objects.total_costs(),
                   'total_sellings': Vente.objects.total_sellings(),
                   'balance': Costs.objects.get_balance(),
                   'branches': Branch.objects.all(),
                   'articles_count': Article.objects.count(),

                   }
        return context

    def get(self, request, start_date=None, end_date=None):
        d1 = request.GET.get('start_date')
        d2 = request.GET.get('end_date')
        context = self.get_context_data()
        if d1 or d2:
            context['form'] = form = DateForm(request.GET)
            if form.is_valid():
                d1 = form.cleaned_data['start_date']
                d2 = form.cleaned_data['end_date']
                context['grand_total_costs'] = Costs.objects.grand_total(start_date=d1, end_date=d2)
                context['purchases'] = Article.objects.total_purchasing_price(start_date=d1, end_date=d2)
                context['costs'] = Costs.objects.total_costs(start_date=d1, end_date=d2)
                context['total_sellings'] = Vente.objects.total_sellings(start_date=d1, end_date=d2)
                context['balance'] = Costs.objects.get_balance(start_date=d1, end_date=d2)
                context['branches'] = Branch.objects.all()
                context['articles_count'] = Article.objects.count()
        else:
            context['form'] = DateForm()
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
