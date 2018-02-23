from django.test import TestCase, RequestFactory
from inventory.models import Article, Arrivage
from django.db.models import ImageField
from cart.models import CartItem
from cart import cartutils
from datetime import date


class TestCartUtils(TestCase):

    def setUp(self):
        #self.factory    = RequestFactory()
        self.session_id = cartutils._generate_cart_id()
        self.arrival    = Arrivage.objects.create(nom='carnaval', date_arrivee=date(2018,2,17))
        self.a          = Article.objects.create(name='a', quantity=2, arrival=self.arrival, photo="a.jpg")
        self.b          = Article.objects.create(name='b', quantity=12, arrival=self.arrival, photo="b.jpg")

    def test_add_item_to_cart(self):
        #request = self.factory.get('/')
        cart = CartItem.objects.create(cart_id=self.session_id, article=self.a, quantity=1)
        cart.augment_quantity(1) # it is how one item is added
        self.assertEqual(2, cart.quantity)

    def test_change_quantity_of_cart_item_normal_case(self):
        cart = CartItem.objects.create(cart_id=self.session_id, article=self.b, quantity=1)
        cart.set_quantity(5)
        self.assertEqual(5, cart.quantity)

    def test_change_quantity_of_cart_item_edge_case_exceed(self):
        cart = CartItem.objects.create(cart_id=self.session_id, article=self.b, quantity=1)
        cart.set_quantity(15)
        self.assertEqual(12, cart.quantity)

    def test_change_quantity_of_cart_item_edge_case_exceed_warning_msg(self):
        cart = CartItem.objects.create(cart_id=self.session_id, article=self.b, quantity=1)
        msg = cart.set_quantity(15)
        self.assertEqual("Warning: quantity set to max stock available.", msg)





