from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView
from .models import Category, Enterprise, Costs
from .forms import CategoryCreateForm, CategoryUpdateForm, EnterpriseCreateForm, EnterpriseUpdateForm, CostsCreateForm, CostsUpdateForm
from inventory.models import Branch

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'costs/category_details.html'
    context_object_name = 'category'


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'costs/category_create.html'
    context_object_name = 'category'
    form_class = CategoryCreateForm
    success_url = reverse_lazy('costs:categories')


class CategoryListView(ListView):
    model = Category
    template_name = 'costs/categories.html'
    context_object_name = 'categories'

class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'costs/category_update.html'
    context_object_name = 'category'
    form_class = CategoryUpdateForm

    def get_success_url(self):
        return '/costs/category_details/%s' % self.object.pk

class CategoryDeleteView(DeleteView):
    model = Category
    context_object_name = 'category'
    template_name = 'costs/category_delete.html'
    success_url = reverse_lazy('costs:categories')


class EnterpriseCreateView(CreateView):
    model = Enterprise
    template_name = 'costs/enterprise_create.html'
    context_object_name = 'enterprise'
    form_class = EnterpriseCreateForm

    def get_success_url(self):
        return '/costs/enterprises'


class EnterpriseDetailView(DetailView):
    model = Enterprise
    template_name = 'costs/enterprise_details.html'
    context_object_name = 'enterprise'


class EnterpriseListView(ListView):
    model = Enterprise
    template_name = 'costs/enterprises.html'
    context_object_name = 'enterprises'


class EnterpriseUpdateView(UpdateView):
    model = Enterprise
    template_name = 'costs/enterprise_update.html'
    context_object_name = 'enterprise'
    form_class = EnterpriseUpdateForm

    def get_success_url(self):
        return '/costs/enterprise_details/%s' % self.object.pk

class EnterpriseDeleteView(DeleteView):
    model = Enterprise
    template_name = 'costs/enterprise_delete.html'
    context_object_name = 'enterprise'
    success_url = reverse_lazy('costs:enterprises')

class CostsCreateView(CreateView):
    model = Costs
    template_name = 'costs/costs_create.html'
    context_object_name = 'cost'
    success_url = reverse_lazy('costs:costs')
    form_class = CostsCreateForm

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



class CostsDetailView(DetailView):
    model = Costs
    template_name = 'costs/costs_details.html'
    context_object_name = 'costs'

class CostsUpdateView(UpdateView):
    model = Costs
    template_name = 'costs/costs_update.html'
    context_object_name = 'costs'
    form_class = CostsUpdateForm

    def get_success_url(self):
        return '/costs/costs_details/%s' % self.object.pk

class CostsDeleteView(DeleteView):
    model = Costs
    template_name = 'costs/costs_delete.html'
    context_object_name = 'costs'
    success_url = reverse_lazy('costs:costs')






