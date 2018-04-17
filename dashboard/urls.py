from django.conf.urls import url
from . import views


app_name = 'dashboard'

urlpatterns = [
    #url(r'^main/(?P<start_date>[0-9]{4}-[0-9]{2}-[0-9]{2})*$', views.MainBalanceView.as_view(), name='main'),
    url(r'^main/(?P<start_date>[0-9]{4}-[0-9]{2}-[0-9]{2})*$', views.MainBalanceView.as_view(), name='main'),
    url(r'^main/(?P<start_date>[0-9]{4}-[0-9]{2}-[0-9]{2})(?P<end_date>[0-9]{4}-[0-9]{2}-[0-9]{2})$', views.MainBalanceView.as_view(), name='main'),
    url(r'^branch/(?P<pk>[0-9]+)/', views.branch_dashboard, name='branch'),
    ]
