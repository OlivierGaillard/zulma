from django.conf.urls import url
from . import views


app_name = 'costs'

urlpatterns = [
    url(r'^category_create/$', views.CategoryCreateView.as_view(), name='category_create'),
    url(r'^category_details/(?P<pk>[0-9]+)$', views.CategoryDetailView.as_view(), name='category_details'),
    url(r'^category_update/(?P<pk>[0-9]+)$', views.CategoryUpdateView.as_view(), name='category_update'),
    url(r'^category_delete/(?P<pk>[0-9]+)$', views.CategoryDeleteView.as_view(), name='category_delete'),
    url(r'^categories/$', views.CategoryListView.as_view(), name='categories'),
    url(r'^enterprise_create/$', views.EnterpriseCreateView.as_view(), name='enterprise_create'),
    url(r'^enterprise_details/(?P<pk>[0-9]+)$', views.EnterpriseDetailView.as_view(), name='enterprise_details'),
    url(r'^enterprise_update/(?P<pk>[0-9]+)$', views.EnterpriseUpdateView.as_view(), name='enterprise_update'),
    url(r'^enterprise_delete/(?P<pk>[0-9]+)$', views.EnterpriseDeleteView.as_view(), name='enterprise_delete'),
    url(r'^enterprises/$', views.EnterpriseListView.as_view(), name='enterprises'),
    url(r'^costs_create/$', views.CostsCreateView.as_view(), name='costs_create'),
    url(r'^costs/$', views.CostsListView.as_view(), name='costs'),
    url(r'^costs_branch/(?P<pk>[0-9]+)$', views.CostsPerBranch.as_view(), name='costs_branch'),
    url(r'^costs_details/(?P<pk>[0-9]+)$', views.CostsDetailView.as_view(), name='costs_details'),
    url(r'^costs_update/(?P<pk>[0-9]+)$', views.CostsUpdateView.as_view(), name='costs_update'),
    url(r'^costs_delete/(?P<pk>[0-9]+)$', views.CostsDeleteView.as_view(), name='costs_delete'),
    ]
