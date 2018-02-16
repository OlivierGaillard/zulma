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
from .views import ArticleDetailView, upload_pic, articles, ArticleUpdateView, ArrivalCreateView, ArrivalDetailView
from .views import ArrivalListView, ArrivalUpdateView
from .views import handle_pictures, upload_pictures_zip

app_name = 'inventory'


urlpatterns = [
    url(r'^arrival_create/$', ArrivalCreateView.as_view(), name='arrival_create'),
    url(r'^arrival_detail/(?P<pk>[0-9]+)$', ArrivalDetailView.as_view(), name='arrival_detail'),
    url(r'^arrival_update/(?P<pk>[0-9]+)$', ArrivalUpdateView.as_view(), name='arrival_update'),
    url(r'^arrivals/$', ArrivalListView.as_view(), name='arrivals'),
    url('articles/', articles, name='articles'),
    #url('article_create', ArticleCreateView.as_view(), name='article_create'),
    url(r'article_update/(?P<pk>[0-9]+)$', ArticleUpdateView.as_view(), name='article_update'),
    url(r'^article_detail/(?P<pk>[0-9]+)$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^upload_pic/(?P<pk>[0-9]+)$', upload_pic, name='upload_pic'),
    url(r'^handle_pics/$', handle_pictures, name='handle_pics'),
    url(r'^upload_zipics/$', upload_pictures_zip, name='upload_zipics'),
]

