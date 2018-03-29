from django.conf.urls import url
from . import views


app_name = 'dashboard'

urlpatterns = [
    url(r'^main/$', views.MainBalanceView.as_view(), name='main'),
    ]
