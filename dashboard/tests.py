from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from cart.models import Vente
from costs.models import Costs, Category
from inventory.models import Article, Arrivage, Branch
from .models import Dashboard
import datetime

class TestDashboard(TestCase):

    def setUp(self):
        self.arrival = Arrivage.objects.create(nom="test", date_arrivee=datetime.date.today())
        # a1 = Article.objects.create(name='a1', quantity=10, photo='a1', arrival=self.arrival, purchasing_price=100)
        # a2 = Article.objects.create(name='a2', quantity=5, photo='a2', arrival=self.arrival,  purchasing_price=100)

        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_balance_view(self):
        Vente.objects.create(montant=20, reglement_termine=True)
        cost_catego = Category.objects.create(name='Divers')
        Costs.objects.create(category=cost_catego, amount=10)
        self.assertEqual(10, Costs.objects.total_costs())
        a1 = Article.objects.create(name='a1', quantity=10, photo='a1', arrival=self.arrival, purchasing_price=100)
        a2 = Article.objects.create(name='a2', quantity=5, photo='a2', arrival=self.arrival,  purchasing_price=100)
        self.assertEqual(200, Article.objects.total_purchasing_price())
        self.assertEqual(20-210, Costs.objects.get_balance())
        self.assertEqual(20, Vente.objects.total_sellings())
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.get(reverse('dashboard:main'))
        self.assertEqual(200, response.status_code)
        html = response.content.decode()
        self.assertInHTML('210.00', html)
        self.assertInHTML('-190.00', html)
        self.assertInHTML('20.00', html)
        self.assertInHTML('200.00', html)
        c.logout()

    def test_sellings_with_branches(self):
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1)
        Vente.objects.create(montant=10, reglement_termine=True, branch=b2)
        self.assertEqual(20, Vente.objects.total_sellings(branch=b1))
        self.assertEqual(10, Vente.objects.total_sellings(branch=b2))
        self.assertEqual(30, Vente.objects.total_sellings())

    def test_costs_with_branch(self):
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1)
        Vente.objects.create(montant=20, reglement_termine=True, branch=b2)
        cost_catego = Category.objects.create(name='Divers')
        Costs.objects.create(category=cost_catego, amount=10, branch=b1)
        Costs.objects.create(category=cost_catego, amount=15, branch=b2)
        self.assertEqual(10, Costs.objects.total_costs(branch=b1))
        self.assertEqual(15, Costs.objects.total_costs(branch=b2))
        self.assertEqual(25, Costs.objects.total_costs())

    def test_purchasing_price_branch_None(self):
        # without branch
        a3 = Article.objects.create(name='a3', quantity=1, photo='a3', arrival=self.arrival, purchasing_price=600)
        # Article without branch
        self.assertEqual(600.00, Article.objects.total_purchasing_price())

    def test_purchasing_price_per_branch(self):
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        a1b1 = Article.objects.create(name='a1b1', quantity=1, photo='a1b1', arrival=self.arrival, purchasing_price=200,
                                     branch=b1)
        a2b1 = Article.objects.create(name='a2b1', quantity=1, photo='a2b1', arrival=self.arrival, purchasing_price=200,
                                      branch=b1)
        a1b2 = Article.objects.create(name='a1b2', quantity=1, photo='a1b2', arrival=self.arrival, purchasing_price=400,
                                     branch=b2)
        # without branch
        a3 = Article.objects.create(name='a3', quantity=1, photo='a3', arrival=self.arrival, purchasing_price=600)
        # Article without branch
        self.assertEqual(1400.00, Article.objects.total_purchasing_price())
        self.assertEqual(400.00, Article.objects.total_purchasing_price(branch=b1))
        self.assertEqual(400.00, Article.objects.total_purchasing_price(branch=b2))

    def test_balance_with_branches(self):
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        a1b1 = Article.objects.create(name='a1b1', quantity=1, photo='a1b1', arrival=self.arrival, purchasing_price=200,
                                     branch=b1)
        a2b1 = Article.objects.create(name='a2b1', quantity=1, photo='a2b1', arrival=self.arrival, purchasing_price=200,
                                      branch=b1)
        a1b2 = Article.objects.create(name='a1b2', quantity=1, photo='a1b2', arrival=self.arrival, purchasing_price=400,
                                     branch=b2)
        # without branch
        a3 = Article.objects.create(name='a3', quantity=1, photo='a3', arrival=self.arrival, purchasing_price=600)


        cost_catego = Category.objects.create(name='Divers')
        Costs.objects.create(category=cost_catego, amount=10, branch=b1)
        Costs.objects.create(category=cost_catego, amount=15, branch=b2)

        Vente.objects.create(montant=20, reglement_termine=True, branch=b1)
        Vente.objects.create(montant=10, reglement_termine=True, branch=b2)

        self.assertEqual(30.00-1400-25.00, Costs.objects.get_balance())
        self.assertEqual(20.00-400-10, Costs.objects.get_balance(branch=b1))


    def test_dashoboard_utility_class(self):
        """The Branch model can retries it."""
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        a1b1 = Article.objects.create(name='a1b1', quantity=1, photo='a1b1', arrival=self.arrival, purchasing_price=200,
                                      branch=b1)
        a2b1 = Article.objects.create(name='a2b1', quantity=1, photo='a2b1', arrival=self.arrival, purchasing_price=200,
                                      branch=b1)
        a1b2 = Article.objects.create(name='a1b2', quantity=1, photo='a1b2', arrival=self.arrival, purchasing_price=400,
                                      branch=b2)
        # without branch
        a3 = Article.objects.create(name='a3', quantity=1, photo='a3', arrival=self.arrival, purchasing_price=600)

        cost_catego = Category.objects.create(name='Divers')
        Costs.objects.create(category=cost_catego, amount=10, branch=b1)
        Costs.objects.create(category=cost_catego, amount=15, branch=b2)

        Vente.objects.create(montant=20, reglement_termine=True, branch=b1)
        Vente.objects.create(montant=10, reglement_termine=True, branch=b2)


        self.assertEqual(400, Dashboard.total_purchasing_prices(branch=b1))
        self.assertEqual(1400, Dashboard.total_purchasing_prices())
        self.assertEqual(25, Dashboard.total_costs())
        self.assertEqual(10, Dashboard.total_costs(branch=b1))
        self.assertEqual(1425, Dashboard.costs_grand_total())
        self.assertEqual(410, Dashboard.costs_grand_total(branch=b1))

        self.assertEqual(20-400-10, Dashboard.get_balance(b1))













