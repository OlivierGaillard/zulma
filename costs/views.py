from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView
from .models import Category, Enterprise, Costs
from .forms import CategoryCreateForm, CategoryUpdateForm, EnterpriseCreateForm, EnterpriseUpdateForm, CostsCreateForm, CostsUpdateForm
from inventory.models import Branch

@method_decorator(login_required, name='dispatch')
class CategoryDetailView(DetailView):
    model = Category
    template_name = 'costs/category_details.html'
    context_object_name = 'category'

@method_decorator(login_required, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    template_name = 'costs/category_create.html'
    context_object_name = 'category'
    form_class = CategoryCreateForm
    success_url = reverse_lazy('costs:categories')

@method_decorator(login_required, name='dispatch')
class CategoryListView(ListView):
    model = Category
    template_name = 'costs/categories.html'
    context_object_name = 'categories'

@method_decorator(login_required, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'costs/category_update.html'
    context_object_name = 'category'
    form_class = CategoryUpdateForm

    def get_success_url(self):
        return '/costs/category_details/%s' % self.object.pk

@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    context_object_name = 'category'
    template_name = 'costs/category_delete.html'
    success_url = reverse_lazy('costs:categories')

@method_decorator(login_required, name='dispatch')
class EnterpriseCreateView(CreateView):
    model = Enterprise
    template_name = 'costs/enterprise_create.html'
    context_object_name = 'enterprise'
    form_class = EnterpriseCreateForm

    def get_success_url(self):
        return '/costs/enterprises'

@method_decorator(login_required, name='dispatch')
class EnterpriseDetailView(DetailView):
    model = Enterprise
    template_name = 'costs/enterprise_details.html'
    context_object_name = 'enterprise'

@method_decorator(login_required, name='dispatch')
class EnterpriseListView(ListView):
    model = Enterprise
    template_name = 'costs/enterprises.html'
    context_object_name = 'enterprises'

@method_decorator(login_required, name='dispatch')
class EnterpriseUpdateView(UpdateView):
    model = Enterprise
    template_name = 'costs/enterprise_update.html'
    context_object_name = 'enterprise'
    form_class = EnterpriseUpdateForm

    def get_success_url(self):
        return '/costs/enterprise_details/%s' % self.object.pk

@method_decorator(login_required, name='dispatch')
class EnterpriseDeleteView(DeleteView):
    model = Enterprise
    template_name = 'costs/enterprise_delete.html'
    context_object_name = 'enterprise'
    success_url = reverse_lazy('costs:enterprises')

@method_decorator(login_required, name='dispatch')
class CostsCreateView(CreateView):
    model = Costs
    template_name = 'costs/costs_create.html'
    context_object_name = 'cost'
    success_url = reverse_lazy('costs:costs')
    form_class = CostsCreateForm

@method_decorator(login_required, name='dispatch')
class CostsListView(ListView):
    model = Costs
    template_name = 'costs/costs.html'
    context_object_name = 'costs'

    def get_context_data(self, q=None):
        ctx = super(CostsListView, self).get_context_data()
        q = self.request.GET.get('q')
        if q:
            ctx['option'] = q
            if q.upper() == 'MAIN':
                # costs = Costs.objects.filter(branch=None)
                # total = sum(c.amount for c in costs)
                total = Costs.objects.total_costs(branch='MAIN')
                ctx['total'] = total
            elif q.upper() == 'ALL':
                ctx['total'] = Costs.objects.total_costs()
            else:
                branch = Branch.objects.get(name=q)
                ctx['total'] = Costs.objects.total_costs(branch=branch)
        else:
            ctx['total'] = Costs.objects.total_costs()
        li = [b.name for b in Branch.objects.all()] + ['All', 'Main']
        li.sort()
        ctx['branchs'] = li
        return ctx

    def get_queryset(self):
        queryset = super(CostsListView, self).get_queryset()
        #ctx = super(CostsListView, self).get_context_data()
        q = self.request.GET.get('q')
        if q:
            if q.upper() == 'MAIN':
                queryset = queryset.filter(branch=None)
            elif q.upper() == 'ALL':
                pass
            else:
                queryset = queryset.filter(branch__name__icontains=q)
        return queryset


@method_decorator(login_required, name='dispatch')
class CostsPerBranch(TemplateView):
    template_name = 'costs/costs.html'
    context_object_name = 'costs'

    def get_context_data(self, pk=None):
        if pk:
            costs = Costs.objects.filter(branch=pk)
        else:
            costs = Costs.objects.all()
        context = {'costs' : costs}
        return context

    def get(self, request, pk=None):
        context = self.get_context_data(pk=pk)
        return render(request=request, template_name='costs/costs.html', context=context)


@method_decorator(login_required, name='dispatch')
class CostsDetailView(DetailView):
    model = Costs
    template_name = 'costs/costs_details.html'
    context_object_name = 'costs'

@method_decorator(login_required, name='dispatch')
class CostsUpdateView(UpdateView):
    model = Costs
    template_name = 'costs/costs_update.html'
    context_object_name = 'costs'
    form_class = CostsUpdateForm

    def get_success_url(self):
        return '/costs/costs_details/%s' % self.object.pk

@method_decorator(login_required, name='dispatch')
class CostsDeleteView(DeleteView):
    model = Costs
    template_name = 'costs/costs_delete.html'
    context_object_name = 'costs'
    success_url = reverse_lazy('costs:costs')






