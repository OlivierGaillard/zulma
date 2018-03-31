from django.conf.urls import url
from . import views


app_name = 'dashboard'

urlpatterns = [
    url(r'^main/$', views.MainBalanceView.as_view(), name='main'),
    url(r'^branch/(?P<pk>[0-9]+)/', views.branch_dashboard, name='branch'),
    ]
