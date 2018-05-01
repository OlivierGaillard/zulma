from django.test import TestCase, RequestFactory
from inventory.models import Article, Arrivage, Branch
from cart.models import CartItem, Vente
from cart import cartutils
from datetime import date, timedelta
from django.utils import timezone

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
        self.assertEqual("Warning: quantity is greater than stock quantity.", msg)


    def test_get_total_sellings(self):
        Vente.objects.create(montant=10.50, reglement_termine=True)
        Vente.objects.create(montant=20.50, reglement_termine=True)
        self.assertEqual(31.0, Vente.objects.total_sellings())

    def test_get_total_sellings_with_uncomplete(self):
        Vente.objects.create(montant=10.50, reglement_termine=False)
        Vente.objects.create(montant=20.50, reglement_termine=True)
        self.assertEqual(20.50, Vente.objects.total_sellings())

    def test_sellings_with_branches(self):
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1)
        Vente.objects.create(montant=10, reglement_termine=True, branch=b2)
        self.assertEqual(20, Vente.objects.total_sellings(branch=b1))
        self.assertEqual(10, Vente.objects.total_sellings(branch=b2))
        self.assertEqual(30, Vente.objects.total_sellings())

    def test_sellings_last_year(self):
        dnow = date.today()
        dlastyear = dnow - timedelta(days=365)
        Vente.objects.create(montant=20, reglement_termine=True, date=dlastyear)
        Vente.objects.create(montant=10, reglement_termine=True)
        self.assertEqual(30, Vente.objects.total_sellings())
        self.assertEqual(20, Vente.objects.total_sellings(year=dlastyear.year))
        self.assertEqual(10, Vente.objects.total_sellings(year=dnow.year))

    def test_get_sellings_last_year(self):
        # Total of sellings of last year
        dnow = timezone.localdate().today()
        t = timedelta(days=365)
        last_year_date = dnow - t
        self.assertEqual(0, Vente.objects.total_sellings(year=last_year_date.year))
        b1 = Branch.objects.create(name='B1')
        self.assertEqual(0, Vente.objects.total_sellings(year=dnow.year))
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=last_year_date)
        # but this year we have zero selling
        self.assertEqual(0, Vente.objects.total_sellings(year=dnow.year))
        self.assertEqual(20, Vente.objects.total_sellings(year=last_year_date.year))

    def test_get_selling_from_to_dates(self):
        # sellings between two dates
        d1 = date(year=2018, month=3, day=1)
        d2 = date(year=2018, month=3, day=31)
        b1 = Branch.objects.create(name='B1')
        vd0 = d1 - timedelta(days=10)
        # this one will not be taken in account
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=vd0)
        self.assertEqual(0, Vente.objects.total_sellings(start_date=d1, end_date=d2))
        # this one will count
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=d1)
        self.assertEqual(20, Vente.objects.total_sellings(start_date=d1, end_date=d2))
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=d2)
        self.assertEqual(40, Vente.objects.total_sellings(start_date=d1, end_date=d2))
        vd1 = d1 + timedelta(days=3)
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=vd1)
        self.assertEqual(60, Vente.objects.total_sellings(start_date=d1, end_date=d2))

    def test_get_selling_from_date_alone(self):
        d1 = date(year=2018, month=3, day=1)
        vd0 = d1 + timedelta(days=1)
        b1 = Branch.objects.create(name='B1')
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=vd0)
        self.assertEqual(20, Vente.objects.total_sellings(start_date=d1))

    def test_get_selling_from_date_alone_selling_at_start_date(self):
        d1 = date(year=2018, month=3, day=1)
        b1 = Branch.objects.create(name='B1')
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=d1)
        vd0 = d1 + timedelta(days=1)
        vd_1 = d1 - timedelta(days=1)
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=vd0)
        # adding a selling older than d1: out of range
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=vd_1)
        self.assertEqual(40, Vente.objects.total_sellings(start_date=d1))

    def test_get_selling_end_date_alone(self):
        d = date(year=2018, month=3, day=1)
        b1 = Branch.objects.create(name='B1')
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=d)
        v_add_1 = d + timedelta(days=1)
        v_sub_1 = d - timedelta(days=1)
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=v_add_1)
        # adding a selling older than d1: out of range
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1, date=v_sub_1)
        self.assertEqual(60, Vente.objects.total_sellings(end_date=v_add_1))







