from django.conf.urls import url
from . import views


app_name = 'cart'

urlpatterns = [
    url(r'^add_item/(?P<pk>[0-9]+)$', views.add_cart_item, name='add_item'),
    url(r'^cart_content/$', views.CartView.as_view(), name='cart_content'),
    url(r'^save_cart_item/(?P<pk>[0-9]+)$', views.save_cart_item, name='save_cart_item'),
    url(r'^checkout/$', views.CheckoutView.as_view(), name='checkout'),
    url(r'^remove_item/(?P<pk>[0-9]+)$', views.remove_cart_item, name='remove_item'),
    url(r'^remove_item_from_vente/(?P<pk>[0-9]+)$', views.remove_article_from_vente_and_update_article_quantity,
        name='remove_article_from_vente'),
    url(r'^edit_price/(?P<pk>[0-9]+)$', views.edit_price, name='edit_price'),
    url(r'^edit_quantity/(?P<pk>[0-9]+)$', views.edit_quantity, name='edit_quantity'),
    url(r'^vente/(?P<pk>[0-9]+)$', views.VenteDetail.as_view(), name='vente'),
    url(r'^vente_update/(?P<pk>[0-9]+)$', views.VenteUpdateView.as_view(), name='vente_update'),
    #url(r'^vente_delete/(?P<pk>[0-9]+)$', views.VenteDeleteView.as_view(), name='vente_delete'),
    url(r'^vente_delete/(?P<pk>[0-9]+)$', views.vente_delete, name='vente_delete'),
    url(r'^ventes/$', views.VenteListView.as_view(), name='ventes'),
    url(r'^clients/$', views.ClientListView.as_view(), name='clients'),
    url(r'^client/(?P<pk>[0-9]+)$', views.ClientDetailView.as_view(), name='client'),
    url(r'^client_update/(?P<pk>[0-9]+)$', views.ClientUpdateView.as_view(), name='client_update'),
    url(r'^client_create/$', views.ClientCreateView.as_view(), name='client_create'),
    url(r'^paiements/$', views.PaiementListView.as_view(), name='paiements'),
    url(r'^paiement_add/(?P<vente_pk>[0-9]+)$', views.add_paiement, name='paiement_add'),
    url(r'^paiement/(?P<pk>[0-9]+)$', views.PaiementDetailView.as_view(), name='paiement'),
    url(r'^paiement_update/(?P<pk>[0-9]+)$', views.PaiementUpdateView.as_view(), name='paiement_update'),
    ]
