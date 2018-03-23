from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from datetime import date
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
from .forms import ArticleLossesForm
import costs.models
from cart.cartutils import article_already_in_cart, get_cart_items
from django.conf import settings
import os
from zipfile import ZipFile
from django.db.utils import IntegrityError
from django.contrib import messages
import subprocess
import shutil
import logging
import tempfile
from urllib.parse import urlparse

logger = logging.getLogger('django')


IMAGE_RESIZE_PERCENT = getattr(settings, 'IMAGE_DEFAULT_RESIZE_PERCENT', '40%')


def resize_pics():
    logger.debug('starting resize...')
    pictures_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
    logger.debug('chdir into %s' % pictures_dir)
    os.chdir(pictures_dir)
    logger.debug('calling mogrify with -resize %s for all *.jpg' % IMAGE_RESIZE_PERCENT)
    returncode = subprocess.call(["mogrify", "-resize", IMAGE_RESIZE_PERCENT, "*.jpg"])
    logger.debug('result: %s' % returncode)
    if returncode == 0:
        logger.debug('resize completed.')
    else:
        logger.warning('resize failed')
        logger.warning('cleaning temporary folder')

def handle_pics_zip(f):
    logger.debug('in handle_pics_zip.')
    pictures_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
    file_name = os.path.join(pictures_dir, f.name)
    logger.debug('filename: %s', file_name)
    with open(file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    logger.debug('file saved. Will unzip')

    with tempfile.TemporaryDirectory() as tempdir:
        logger.debug('will unpack in tempdir: ', tempdir)
        shutil.unpack_archive(file_name, tempdir)
        logger.debug('unzipped in tempdir.')
        #ZipFile.extractall(file_name, path=tempdir)
        logger.debug('will walk into ', tempdir)
        for dirpath, dirnames, filenames in os.walk(tempdir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                logger.debug('handling %s...' % filepath)
                file, ext = os.path.splitext(filepath)
                if ext.upper() == ".JPG" or ext.upper() == ".JPEG":
                    logger.debug('mv %s into tmp.' % filepath)
                    shutil.move(filepath, pictures_dir)
                else:
                    logger.debug('not moved file %s' % filepath)
                logger.debug('end.')
    #logger.debug('rmdir %s' % zipped_dir)
     #       os.rmdir(zipped_dir)
    logger.debug('rm zip file %s' % file_name)
    os.unlink(file_name)
    logger.debug('zip file deleted. Will resize pics now.')
    resize_pics()


@csrf_exempt
def upload_pictures_zip(request):
    if request.method == 'POST':
        logger.debug('upload_pictures_zip is called.')
        form = UploadPicturesZipForm(request.POST, request.FILES)
        if form.is_valid():
            logger.debug('form is valid. handle_pics_zip will be called...')
            handle_pics_zip(request.FILES['pictures_zip'])
            return HttpResponseRedirect("/inventory/handle_pics/")
        else:
            return render(request, "inventory/upload_zipics.html", {'form': form})
    else:
        form = UploadPicturesZipForm()
        return render(request, "inventory/upload_zipics.html", {'form': form})


def handle_pictures(request):
    logger.debug("starting pictures handling to make Article's instances.")
    pictures_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
    target_dir = os.path.join(settings.MEDIA_ROOT, 'articles')
    files = os.listdir(pictures_dir)
    logger.debug('%s pictures to handle.' % str(len(files)))
    if request.method == 'POST':
        form = HandlePicturesForm(request.POST)
        if form.is_valid():
            arrival = form.cleaned_data['arrival']
            logger.debug('Arrival: %s' % arrival)
            category = form.cleaned_data['category']
            logger.debug('Category: %s' % category)
            nb = 0
            for f in files:
                nb += 1
                source_path = os.path.join(pictures_dir, f)
                target_path = os.path.join(target_dir, f)
                a = Article(photo=os.path.join('articles', f), arrival=arrival)
                if category:
                    logger.debug('saving category %s' % category)
                    a.category = category
                else:
                    logger.debug('no category selected.')
                try:
                    logger.debug('creating article with pic %s' % f)
                    a.save()
                    logger.debug('article saved.')
                    logger.debug('moving the pic from "tmp" into "articles" directory.')
                    messages.info(request, 'Article with pic %s created.' % f)
                    os.rename(source_path, target_path)
                except IntegrityError:
                    msg = 'The pic %s already exists and was deleted.' % f
                    logger.warning(msg)
                    messages.warning(request, msg)
                    os.unlink(source_path)

            logger.debug('handling pics job is ended. Return the articles list.')
            return HttpResponseRedirect("/inventory/articles/")
        else:
            logger.warning('form is not valid. Pictures will not be handled.')
            return HttpResponse("Will not handle pictures. Form not valid")


    else:
        logger.debug('GET part of handle_pictures.')
        form = HandlePicturesForm()
        logger.debug('%s pictures to handle.' % str(len(files)))
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
    purchasing_price__gt = NumberFilter(name='purchasing_price', lookup_expr='gt',
                                        label=_('greater than'))
    selling_price__gt = NumberFilter(name='selling_price', lookup_expr='gt',
                                        label=_('greater than'))
    class Meta:
        model = Article
        fields = {'name' : ['icontains'],
                  'category__name' : ['icontains'],
                  'id' : ['exact'],
                  'quantity' : ['exact'],
                  'solde': ['exact'],
                  'arrival__nom' : ['icontains'],
                  }

def make_summary(queryset):
    summary = {}
    summary['total'] = total = len(queryset)
    summary['quantity_zero'] = quantity_zero = len(queryset.filter(quantity=0))
    summary['quantity_zero_percent'] = "{0}".format(str(int((quantity_zero / total) * 100)))
    summary['reduced'] = reduced = len(queryset.filter(solde='S'))

    summary['reduced_percent'] = "{0}".format(str(int((reduced / total) * 100)))
    summary['no_name'] = no_name = len(queryset.filter(name='n.d.'))
    summary['no_name_percent']     = "{0}".format(str(int((no_name / total) * 100)))
    summary['no_category'] = no_category = len(queryset.filter(category=None))
    summary['no_category_percent'] = "{0}".format(str(int((no_category / total) * 100)))
    summary['selling_price_zero'] = selling_price_zero = len(queryset.filter(selling_price = 0.0))
    summary['no_selling_price_percent'] = "{0}".format(str(int((selling_price_zero / total) * 100)))
    summary['purchasing_price_zero'] = purchasing_price_zero = len(queryset.filter(purchasing_price=0.0))
    summary['no_purchasing_price_percent'] = "{0}".format(str(int((purchasing_price_zero / total) * 100)))
    return summary

@login_required()
def articles(request):
    #enterprise_of_current_user = Employee.get_enterprise_of_current_user(request.user)
    #qs = Article.objects.filter(enterprise=enterprise_of_current_user)
    qs = Article.objects.all()
    summary = make_summary(qs)
    context = {'summary': summary, }

    # Constructing filter for query
    get_query = request.GET.copy()
    meta = request.META  # voir https://docs.djangoproject.com/fr/1.11/ref/request-response/
    try:
        HTTP_REFERER = meta['HTTP_REFERER']
        logger.debug('REFERER: %s' % HTTP_REFERER)
        r = urlparse(HTTP_REFERER)
        logger.debug('query of current page: %s' % get_query)
        # 1st time the list is requested, and without a page=1 or page=2 query.
        if '/inventory/articles/' in r and not('page' in get_query):
            logger.debug('Request referrer is articles list. Saving query parameters: "%s".' % get_query)
            request.session['get_query'] = get_query
        else:
            logger.debug('Request referrer is NOT articles list OR we are in articles list within the paginator. Trying to retrieve from session.')
            get_query = request.session.get('get_query', '')
            logger.debug('value retrieved: %s' % get_query)
    except KeyError:
        logger.debug('REFERER is empty')
    # Creating filterk passing the filter params
    article_filter = ArticleFilter(get_query, queryset=qs)

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

# @method_decorator(login_required, name='dispatch')
# class ArticleLossesView(UpdateView):
#     template_name = 'inventory/losses_form.html'
#     context_object_name = 'article'
#     model = Article
#     form_class = ArticleLossesForm

@login_required()
def add_one_loss(request, pk):
    if request.method == 'POST':
        form = ArticleLossesForm(request.POST)
        if form.is_valid():
            db_instance = Article.objects.get(pk=pk)
            db_instance.losses += form.cleaned_data['losses']
            db_instance.amount_losses += form.cleaned_data['amount_losses']
            db_instance.quantity -= form.cleaned_data['losses']
            db_instance.save()
            category_losses = None
            try:
                category_losses = costs.models.Category.objects.get(name='Losses')
            except ObjectDoesNotExist :
                category_losses = costs.models.Category.objects.create(name='Losses')
            url_msg = "/inventory/article_detail/%s" % pk
            name = "Article-ID: %s " % db_instance.pk
            costs.models.Costs.objects.create(category = category_losses, amount=form.cleaned_data['amount_losses'],
                                              name=name, billing_date=date.today(),
                                              article_link=url_msg)
            return HttpResponseRedirect("/inventory/article_detail/%s" % pk)
        else:
            return render(request=request, template_name='inventory/losses_form.html',
                          context={'form': form})

    else:
        # article = Article.objects.get(pk=pk)
        # form = ArticleLossesForm(instance=article)
        form = ArticleLossesForm()
        return render(request, "inventory/losses_form.html", {'form' : form})




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

@method_decorator(login_required, name='dispatch')
class ArticleDeleteView(DeleteView):
    context_object_name = 'article'
    template_name = 'inventory/article_delete.html'
    model = Article
    success_url = 'inventory/articles/'





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
