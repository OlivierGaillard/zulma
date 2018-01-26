from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
#from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django_filters import FilterSet, CharFilter, ChoiceFilter
from django_filters.views import FilterView
from django.views.generic import ListView, TemplateView, CreateView, DetailView
from django.contrib.auth.models import User
from .models import Article, Employee, Photo
from .forms import  ArticleCreateForm, AddPhotoForm
from cart.cartutils import article_already_in_cart, get_cart_items

# class ProductView(ListView):
#     model = Product
#     template_name = 'products/products.html'
#     paginate_by = 5
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data()
#         context['product_list'] = ProductFilter(self.request.GET, queryset=Product.objects.order_by('id'))
#         return context


class ArticleFilter(FilterSet):
    genre_choices = (
        ('A', 'Accessoire'),
        ('V', 'Vêtement'),
        ('C', 'Chaussure'),
        ('S', 'Sous-vêtement'),
    )

    clients_choices = (
        ('H', 'Homme'),
        ('F', 'Femme'),
        ('M', 'Mixte'),
        ('E', 'Enfant'),
    )

    solde_choices = (
        ('N', '-'),
        ('S', 'en solde'),
    )

    genre_article = ChoiceFilter(choices=genre_choices)
    type_client = ChoiceFilter(choices=clients_choices)
    solde = ChoiceFilter(choices=solde_choices)
    class Meta:
        model = Article
        fields = {'marque__nom' : ['icontains'],
                  'nom': ['icontains'],
                  'id' : ['exact'],
                  }
    @property
    def qs(self):
        parent = super(ArticleFilter, self).qs
        enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        return parent.filter(entreprise=enterprise_of_current_user)



@method_decorator(login_required, name='dispatch')
class ArticleFilteredView(FilterView):
    filterset_class = ArticleFilter
    template_name = 'inventory/articles.html' # filtered list
    context_object_name = 'articles'

    def test_func(self):
        return  Employee.is_current_user_employee(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ArticleFilteredView, self).get_context_data(**kwargs)
        enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        context['enterprise'] = enterprise_of_current_user

        # paginator = Paginator(entreprise=enterprise_of_current_user), 25)
        # page = self.request.GET.get('page')
        # articles = paginator._get_page(page)

        return context


@method_decorator(login_required, name='dispatch')
class ArticleDetailView(DetailView):
    context_object_name = 'article'
    template_name = 'inventory/article.html'
    model = Article
    fields = ['arrivage', 'nom', 'marque', ]

    def get_context_data(self, **kwargs):
        ctx = super(ArticleDetailView, self).get_context_data(**kwargs)
        #ctx = add_cart_counter_to_context(self.request, ctx)
        #ctx = add_total_books(ctx)
        cart_items = get_cart_items(self.request)
        ctx['article_in_cart'] = article_already_in_cart(cart_items, self.object)
        #return add_categories_to_context(ctx)
        return ctx



@method_decorator(login_required, name='dispatch')
class ArticlesListView(ListView):
    context_object_name = 'articles'
    template_name = 'inventory/articles.html'
    model = Article

    def get_queryset(self):
        enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        qs = Article.objects.filter(entreprise=enterprise_of_current_user)
        return qs

@method_decorator(login_required, name='dispatch')
class ArticleCreateView(CreateView):
    model = Article
    template_name = "inventory/article_create.html"
    #success_url = "inventory/articles.html"
    form_class = ArticleCreateForm

    def form_valid(self, form):
        if form.is_valid():
            print('Form is valid')
            self.object = form.save()
            #return HttpResponseRedirect(self.success_url)
            return HttpResponseRedirect(self.get_success_url())
        else:

            print('Form is NOT valid')


    def get_success_url(self):
        return reverse('inventory:articles')

    # def form_valid(self, form):
    #     #self.object = form.save()
    #     print("inside form_valid")
    #     #self.object.update_marque_ref(form['marque'].value(), form['marque_ref'].value())
    #     return HttpResponseRedirect('inventory/articles.html')

    # Todo: filtrer les arrivages de l'utilisateur


    # def get_form_kwargs(self):
    #     kwargs = super(ArticleCreateView, self).get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs


def upload_pic(request, pk):
    "pk is Article ID"
    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            article = Article.objects.get(pk=pk)
            photo = Photo()
            photo.photo = form.cleaned_data['image']
            photo.article = article
            photo.save()
            return HttpResponseRedirect("/inventory/article_detail/" + str(article.pk))
        else:
            article = Article.objects.get(pk=pk)
            return render(request, "inventory/photo_add.html", {'article': article, 'form': form})

    else:
        article = Article.objects.get(pk=pk)
        return render(request, "inventory/photo_add.html", {'article': article})

