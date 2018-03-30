"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from .views import ArticleDetailView, articles, ArticleUpdateView, ArticleDeleteView
from .views import ArrivalListView, ArrivalUpdateView, ArrivalCreateView, ArrivalDetailView
from .views import handle_pictures, upload_pictures_zip, CategoryCreateView, CategoryUpdateView, CategoryListView
from .views import CategoryDetailView, CategoryDeleteView
from .views import add_one_loss, AddOneLossView, BranchCreateView, BranchDetailView, BranchDeleteView
from .views import BranchListView, BranchEditView


app_name = 'inventory'


urlpatterns = [
    url(r'^arrival_create/$', ArrivalCreateView.as_view(), name='arrival_create'),
    url(r'^arrival_detail/(?P<pk>[0-9]+)$', ArrivalDetailView.as_view(), name='arrival_detail'),
    url(r'^arrival_update/(?P<pk>[0-9]+)$', ArrivalUpdateView.as_view(), name='arrival_update'),
    url(r'^arrivals/$', ArrivalListView.as_view(), name='arrivals'),
    url(r'^categories/$', CategoryListView.as_view(), name='categories'),
    url(r'^category_update/(?P<pk>[0-9]+)$', CategoryUpdateView.as_view(), name='category_update'),
    url(r'^category_create/$', CategoryCreateView.as_view(), name='category_create'),
    url(r'^category_detail/(?P<pk>[0-9]+)$', CategoryDetailView.as_view(), name='category_detail'),
    url(r'^category_delete/(?P<pk>[0-9]+)$', CategoryDeleteView.as_view(), name='category_delete'),
    url('articles/', articles, name='articles'),

    url('branches/', BranchListView.as_view(), name='branches'),
    url('branch_create/$', BranchCreateView.as_view(), name='branch_create'),
    url('branch_detail/(?P<pk>[0-9]+)$', BranchDetailView.as_view(), name='branch_detail'),
    url('branch_delete/(?P<pk>[0-9]+)$', BranchDeleteView.as_view(), name='branch_delete'),
    url('branch_update/(?P<pk>[0-9]+)$', BranchEditView.as_view(), name='branch_update'),

    url(r'article_update/(?P<pk>[0-9]+)$', ArticleUpdateView.as_view(), name='article_update'),
    url(r'article_losses/(?P<pk>[0-9]+)$', add_one_loss, name='article_losses'),
    url(r'add_one_loss/(?P<pk>[0-9]+)$', AddOneLossView.as_view(), name='add_one_loss'),
    url(r'^article_detail/(?P<pk>[0-9]+)$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^article_delete/(?P<pk>[0-9]+)$', ArticleDeleteView.as_view(), name='article_delete'),
    #url(r'^upload_pic/(?P<pk>[0-9]+)$', upload_pic, name='upload_pic'),
    url(r'^handle_pics/$', handle_pictures, name='handle_pics'),
    url(r'^upload_zipics/$', upload_pictures_zip, name='upload_zipics'),
]

