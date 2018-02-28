from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import CartItem
from inventory.models import Article
from .cartutils import get_cart_id_session
#from .views import ArticleDeleteView

class TestInventoryViews(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10)
        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_add_to_cart_view(self):
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





