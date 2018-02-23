from django.test import TestCase, RequestFactory
from inventory.models import Article, Arrivage
from cart.models import CartItem
from cart import cartutils
from datetime import date


class TestCartUtils(TestCase):

    def setUp(self):
        #self.factory    = RequestFactory()
        self.session_id = cartutils._generate_cart_id()
        self.arrival    = Arrivage.objects.create(nom='carnaval', date_arrivee=date(2018,2,17))
        self.a          = Article.objects.create(name='a', quantity=2, arrival=self.arrival)


    def test_add_item_to_cart(self):
        #request = self.factory.get('/')
        self.cart = CartItem.objects.create(cart_id=self.session_id, article=self.a, quantity=1)
        self.cart.augment_quantity(1) # it is how one item is added
        self.assertEqual(2, self.cart.quantity)





