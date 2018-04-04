from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import CartItem, Vente, Paiement, Client as Customer
from inventory.models import Article
from datetime import date

from .cartutils import get_cart_id_session
#from .views import ArticleDeleteView

class TestInventoryViews(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10)
        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def btest_add_to_cart_view(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c.post(reverse('cart:add_item', args=[self.a1.pk]))
        self.assertEqual(CartItem.objects.count(), 1)
        data = {'new_quantity' : "2", 'new_price' : "50"}
        cart_item = CartItem.objects.all()[0]
        c.post(reverse('cart:save_cart_item', args=[cart_item.pk]), data=data)
        cart_item = CartItem.objects.all()[0]
        self.assertEqual(cart_item.prix, 50)
        self.assertEqual(cart_item.total(), 100)
        c.logout()


    def test_add_selling(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c.post(reverse('cart:add_item', args=[self.a1.pk]))
        data = {'new_quantity': "1", 'new_price': "50"}
        cart_item = CartItem.objects.all()[0]
        c.post(reverse('cart:save_cart_item', args=[cart_item.pk]), data=data)
        # Cart item is updated and ready to checkout: i.e. create a selling
        r = c.get(reverse('cart:checkout'))
        self.assertInHTML('50', r.content.decode())
        data = {'montant': 50, 'date': date.today()}
        r = c.post(reverse('cart:checkout'), data=data)
        self.assertEqual(1, Vente.objects.count())
        # Selling is created.
        v = Vente.objects.all()[0]
        data = {'montant' : '50', 'date' : date.today()}
        r = c.post(reverse('cart:paiement_add', args=[v.pk]), data=data)
        self.assertEqual(1, Paiement.objects.count())
        p = Paiement.objects.all()[0]
        self.assertEqual(p.montant, 50)
        v = Vente.objects.get(pk=v.pk)
        self.assertTrue(v.reglement_termine)

    def test_delete_customer(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        cust = Customer.objects.create(name='Gaillard', first_name='Olivier')
        self.assertEqual(1, Customer.objects.count())
        c.post(reverse('cart:client_delete', args=[cust.pk]))
        self.assertEqual(0, Customer.objects.count())



