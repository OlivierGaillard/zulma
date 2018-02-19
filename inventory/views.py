from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
#from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django_filters import FilterSet, CharFilter, ChoiceFilter, NumberFilter
from django_filters.views import FilterView
from django.views.generic import ListView, TemplateView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.models import User
from .models import Article, Employee, Arrivage, Category
from .forms import  ArticleUpdateForm, ArrivalCreateForm, HandlePicturesForm, ArrivalUpdateForm
from .forms import UploadPicturesZipForm, CategoryFormCreate, CategoryFormUpdate, CategoryFormDelete
from cart.cartutils import article_already_in_cart, get_cart_items
from django.conf import settings
import os
from zipfile import ZipFile
from django.db.utils import IntegrityError
import subprocess
import shutil


IMAGE_RESIZE_PERCENT = getattr(settings, 'IMAGE_DEFAULT_RESIZE_PERCENT', '40%')


def resize_pics():
    pictures_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
    os.chdir(pictures_dir)
    subprocess.call(["mogrify", "-resize", IMAGE_RESIZE_PERCENT, "*.jpg"])


def handle_pics_zip(f):
    pictures_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
    target_dir = os.path.join(settings.MEDIA_ROOT, 'articles')
    file_name = os.path.join(pictures_dir, f.name)
    with open(file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    shutil.unpack_archive(file_name, pictures_dir)
    zipfile = ZipFile(file_name)
    first_element = zipfile.namelist()[0]
    if first_element:
        if first_element.endswith('/'): # zipped directory
            zipped_dir = os.path.join(pictures_dir, first_element)
            os.chdir(zipped_dir)
            with os.scandir('.') as it:
                for entry in it:
                    shutil.move(entry.name, pictures_dir)
            os.rmdir(zipped_dir)
    os.unlink(file_name)
    resize_pics()


@csrf_exempt
def upload_pictures_zip(request):
    if request.method == 'POST':
        form = UploadPicturesZipForm(request.POST, request.FILES)
        if form.is_valid():
            handle_pics_zip(request.FILES['pictures_zip'])
            return HttpResponseRedirect("/inventory/handle_pics/")
        else:
            return render(request, "inventory/upload_zipics.html", {'form': form})
    else:
        form = UploadPicturesZipForm()
        return render(request, "inventory/upload_zipics.html", {'form': form})


def handle_pictures(request):
    pictures_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
    target_dir = os.path.join(settings.MEDIA_ROOT, 'articles')
    files = os.listdir(pictures_dir)


    if request.method == 'POST':
        form = HandlePicturesForm(request.POST)
        if form.is_valid():
            arrival = form.cleaned_data['arrival']
            nb = 0
            for f in files:
                nb += 1
                source_path = os.path.join(pictures_dir, f)
                target_path = os.path.join(target_dir, f)
                a = Article(photo=os.path.join('articles', f), arrival=arrival)
                try:
                    a.save()
                except IntegrityError:
                    os.unlink(source_path)
                    return HttpResponse('This pic already exists and was deleted.')
                os.rename(source_path, target_path)
            return HttpResponseRedirect("/inventory/articles/")
        else:
            return HttpResponse("Will not handle pictures. Form not valid")


    else:

        form = HandlePicturesForm()
        return render(request, "inventory/handle_pics.html", {'form': form, 'pics_count' : len(files)})

class CategoryCreateView(CreateView):
    model = Category
    template_name = 'inventory/category_create.html'
    form_class = CategoryFormCreate
    context_object_name = 'category'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'inventory/category_detail.html'
    context_object_name = 'category'


class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'inventory/category_update.html'
    form_class = CategoryFormUpdate
    context_object_name = 'category'

class CategoryListView(ListView):
    model = Category
    template_name = 'inventory/categories.html'
    context_object_name = 'categories'

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'inventory/category_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('inventory:categories')

class ArrivalCreateView(CreateView):
    model = Arrivage
    template_name = 'inventory/arrival_create.html'
    form_class = ArrivalCreateForm
    context_object_name = 'arrival'

class ArrivalDetailView(DetailView):
    model = Arrivage
    template_name = 'inventory/arrival_detail.html'
    context_object_name = 'arrival'

class ArrivalUpdateView(UpdateView):
    model = Arrivage
    template_name = 'inventory/arrival_update.html'
    context_object_name = 'arrival'
    form_class = ArrivalUpdateForm


class ArrivalListView(ListView):
    model = Arrivage
    template_name = 'inventory/arrivals.html'
    context_object_name = 'arrivals'


class ArticleFilter(FilterSet):

    quantity__gt = NumberFilter(name='quantity', lookup_expr='gt', label=_('quantity greater than'))

    class Meta:
        model = Article
        fields = {'name' : ['icontains'],
                  'category__name' : ['icontains'],
                  'id' : ['exact'],
                  'quantity' : ['exact'],
                  'solde': ['exact'],
                  }



@login_required()
def articles(request):
    #enterprise_of_current_user = Employee.get_enterprise_of_current_user(request.user)
    #qs = Article.objects.filter(enterprise=enterprise_of_current_user)
    qs = Article.objects.all()
    get_query = request.GET.copy()
    if 'quantity__gt' not in get_query:
        get_query['quantity__gt'] = '0'


    article_filter = ArticleFilter(get_query,
                                   queryset=qs)
    context = {}
    # Extracting the filter parameters
    meta = request.META
    q = meta['QUERY_STRING']
    # the whole url is .e.g. "marque__nom__icontains=&nom__icontains=&id=&genre_article=&type_client=H&solde=S&page=2"
    if q.find('name') > 0: # checking if a filter param exist?
        # it contains a filter
         try:
            idx = q.index('page')
            q = q[:idx-1] # removing the page part of the url:
            #print('filter part:', q)
            context['q'] = q
         except ValueError:
            #print('no page or page 1, setting the filter')
            context['q'] = q

    paginator = Paginator(article_filter.qs, 25)
    page = request.GET.get('page')
    start_index = 1
    try:
        articles = paginator.page(page)
        start_index = articles.start_index()
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages) # last page
        start_index = articles.start_index()
    context['articles'] = articles
    context['count'] = article_filter.qs.count()
    context['filter'] = article_filter
    context['start_index'] = start_index
    return render(request, 'inventory/articles.html', context)





@method_decorator(login_required, name='dispatch')
class ArticleDetailView(DetailView):
    context_object_name = 'article'
    template_name = 'inventory/article.html'
    model = Article
    fields = ['name']

    def get_context_data(self, **kwargs):
        ctx = super(ArticleDetailView, self).get_context_data(**kwargs)
        #ctx = add_cart_counter_to_context(self.request, ctx)
        #ctx = add_total_books(ctx)
        cart_items = get_cart_items(self.request)
        ctx['article_in_cart'] = article_already_in_cart(cart_items, self.object)
        #return add_categories_to_context(ctx)
        return ctx

@method_decorator(login_required, name='dispatch')
class ArticleUpdateView(UpdateView):
    template_name = 'inventory/article_update.html'
    context_object_name = 'article'
    model = Article
    form_class = ArticleUpdateForm

    def get_success_url(self):
        return reverse('inventory:articles')




@method_decorator(login_required, name='dispatch')
class ArticlesListView(ListView):
    context_object_name = 'articles'
    template_name = 'inventory/articles.html'
    model = Article

    def get_queryset(self):
        #enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        #qs = Article.objects.filter(entreprise=enterprise_of_current_user)
        qs = Article.objects.all()
        return qs

# @method_decorator(login_required, name='dispatch')
# class ArticleCreateView(CreateView):
#     model = Article
#     template_name = "inventory/article_create.html"
#     #success_url = "inventory/articles.html"
#     form_class = ArticleCreateForm
#
#     def form_valid(self, form):
#         if form.is_valid():
#             print('Form is valid')
#             self.object = form.save()
#             #return HttpResponseRedirect(self.success_url)
#             return HttpResponseRedirect(self.get_success_url())
#         else:
#
#             print('Form is NOT valid')
#
#
#     def get_success_url(self):
#         return reverse('inventory:articles')

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


# def upload_pic(request, pk):
#     "pk is Article ID"
#     if request.method == 'POST':
#         form = AddPhotoForm(request.POST, request.FILES)
#         if form.is_valid():
#             article = Article.objects.get(pk=pk)
#             photo = Photo()
#             photo.photo = form.cleaned_data['image']
#             photo.article = article
#             photo.save()
#             return HttpResponseRedirect("/inventory/article_detail/" + str(article.pk))
#         else:
#             article = Article.objects.get(pk=pk)
#             return render(request, "inventory/photo_add.html", {'article': article, 'form': form})
#
#     else:
#         article = Article.objects.get(pk=pk)
#         return render(request, "inventory/photo_add.html", {'article': article})
#
