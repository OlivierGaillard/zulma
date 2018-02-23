from django.test import TestCase
from inventory.models import Article
from cart.models import CartItem
from cart import cartutils

class TestCartUtils(TestCase):

    def setUp(self):
        self.a = Article.objects.create(name='a', quantity=2)

    def test_add_item_to_cart(self):
        pass




