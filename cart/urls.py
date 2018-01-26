from django.conf.urls import url
from . import views


app_name = 'cart'

urlpatterns = [
    url(r'^add_item/(?P<pk>[0-9]+)$', views.add_cart_item, name='add_item'),
    url(r'^cart_content/$', views.CartView.as_view(), name='cart_content'),
    url(r'^checkout/(?P<pk>[0-9]+)$', views.CheckoutView.as_view(), name='checkout'),
    url(r'^remove_item/(?P<pk>[0-9]+)$', views.remove_cart_item, name='remove_item'),
    url(r'^edit_price/(?P<pk>[0-9]+)$', views.edit_price, name='edit_price'),
    url(r'^vente/(?P<pk>[0-9]+)$', views.VenteDetail.as_view(), name='vente'),
    url(r'^vente_delete/(?P<pk>[0-9]+)$', views.VenteDeleteView.as_view(), name='vente_delete'),
    url(r'^ventes/$', views.VenteListView.as_view(), name='ventes'),
    url(r'^clients/$', views.ClientListView.as_view(), name='clients'),
    url(r'^client/(?P<pk>[0-9]+)$', views.ClientDetailView.as_view(), name='client'),
    url(r'^client_create/$', views.ClientCreateView.as_view(), name='client_create'),
    url(r'^paiements/$', views.PaiementListView.as_view(), name='paiements'),
    url(r'^paiement_create/$', views.PaiementCreateView.as_view(), name='paiement_create'),
    url(r'^paiement_add/(?P<vente_pk>[0-9]+)$', views.add_paiement, name='paiement_add'),
    #url(r'^paiement_add/$', views.add_paiement, name='paiement_add'),
    url(r'^paiement/(?P<pk>[0-9]+)$', views.PaiementDetailView.as_view(), name='paiement'),
    ]