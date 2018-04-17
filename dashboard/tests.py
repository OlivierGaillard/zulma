from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from cart.models import Vente
from costs.models import Costs, Category
from inventory.models import Article, Arrivage, Branch
from .models import Dashboard
from datetime import date, timedelta
from django.utils import timezone
#from django.utils.timezone import datetime, timedelta, localdate
from inventory.views import articleDeleteView

class TestDashboard(TestCase):

    def setUp(self):
        dnow = timezone.localdate().today()
        self.arrival = Arrivage.objects.create(nom="test", date_arrivee=dnow)
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


    def test_balance_view_bad_dates_order(self):
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
        data = {'start_date': '2018-02-01', 'end_date': '2018-01-31'}
        response = c.get(reverse('dashboard:main'), data=data)
        self.assertEqual(200, response.status_code)
        self.assertInHTML('<li>start and end dates order mismatch</li>', response.content.decode())

    def test_main_balance_view_start_end_dates(self):
        d1mars = date(year=2018, month=3, day=1)
        d28mars = date(year=2018, month=3, day=28)
        d31mars = date(year=2018, month=3, day=31)
        d3mars = d1mars + timedelta(days=2)
        Vente.objects.create(montant=20, reglement_termine=True, date=d28mars)
        cost_catego = Category.objects.create(name='Divers')
        Costs.objects.create(category=cost_catego, amount=10, billing_date=d1mars)
        self.assertEqual(10, Costs.objects.total_costs())
        a1 = Article.objects.create(name='a1', quantity=10, photo='a1', arrival=self.arrival, purchasing_price=100,
                                    date_added=d3mars)
        a2 = Article.objects.create(name='a2', quantity=5, photo='a2', arrival=self.arrival, purchasing_price=100,
                                    date_added=d3mars)
        self.assertEqual(200, Article.objects.total_purchasing_price(start_date=d1mars, end_date=d31mars))
        self.assertEqual(20 - 210, Costs.objects.get_balance())
        self.assertEqual(20, Vente.objects.total_sellings())
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'start_date': '2018-02-01', 'end_date': '2018-03-31'}
        response = c.get(reverse('dashboard:main'), data=data)
        self.assertEqual(200, response.status_code)
        self.assertInHTML('-190.00', response.content.decode())

    def test_branch_balance_view(self):
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        Vente.objects.create(montant=20, reglement_termine=True, branch=b1)
        cost_catego = Category.objects.create(name='Divers')
        Costs.objects.create(category=cost_catego, amount=10, branch=b1)
        a1 = Article.objects.create(name='a1', branch=b1, quantity=10, photo='a1', arrival=self.arrival, purchasing_price=100)
        a2 = Article.objects.create(name='a2', branch=b2, quantity=5, photo='a2', arrival=self.arrival, purchasing_price=100)
        balance = 20-10-100
        self.assertEqual(balance, Costs.objects.get_balance(branch=b1))
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.get(reverse('dashboard:branch', args=[b1.pk]))
        self.assertEqual(200, response.status_code)
        html = response.content.decode()
        self.assertInHTML('-90.00', html)
        c.logout()


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

    def test_costs_date_interval(self):
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        d1mars  = date(year=2018, month=3, day=1)
        d31mars = date(year=2018, month=3, day=31)
        dfevrier = d1mars - timedelta(days=20)
        d3mars = d1mars + timedelta(days=2)
        # Out of range: in february
        Article.objects.create(name='alast', photo='alast', arrival=self.arrival, purchasing_price=200,
                               date_added=dfevrier, branch=b1)
        self.assertEqual(0, Article.objects.total_purchasing_price(start_date=d1mars))
        self.assertEqual(0, Costs.objects.get_balance(start_date=d1mars, end_date=d31mars))
        # In mars (1)
        Article.objects.create(name='alast1', photo='alast1', arrival=self.arrival, purchasing_price=200,
                       date_added=d1mars, branch=b2)
        self.assertEqual(200, Article.objects.total_purchasing_price(start_date=d1mars))
        self.assertEqual(-200, Costs.objects.get_balance(start_date=d1mars, end_date=d31mars))

        # Testing with branch
        self.assertEqual(0, Costs.objects.get_balance(branch=b1, start_date=d1mars, end_date=d31mars))
        self.assertEqual(0, Costs.objects.get_balance(branch=b1, start_date=d1mars, end_date=d31mars))
        self.assertEqual(-200, Costs.objects.get_balance(branch=b2, start_date=dfevrier, end_date=d31mars))

    def test_costs_last_year(self):
        cost_catego = Category.objects.create(name='Divers')
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        dnow = timezone.localdate().today()
        lastyear = dnow - timedelta(days=365)
        # Costs for this year
        Costs.objects.create(category=cost_catego, amount=10, branch=b1)
        Costs.objects.create(category=cost_catego, amount=15, branch=b2)
        # Testing still zero costs amount for last year
        self.assertEqual(0, Costs.objects.total_costs(year=lastyear.year))
        # Testing costs amount for this year
        self.assertEqual(25, Costs.objects.total_costs(year=dnow.year))
        # Creating costs for last year
        Costs.objects.create(category=cost_catego, amount=10, branch=b1, billing_date=lastyear)
        Costs.objects.create(category=cost_catego, amount=15, branch=b2, billing_date=lastyear)
        self.assertEqual(25, Costs.objects.total_costs(year=lastyear.year))


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


    def test_delete_article_check_costs_purchases_are_ok(self):
        """If one article has a purchasing price it could be deleted from
        the inventory but its purchasing price does need to be added
        to the costs. When to add the purchase cost to costs?
        Right after the price is saved? Bad idea because the total costs
        should then be updated to not include the request for articles.

        Then the price could be added during the deletion of the article.
        I will include a message on the form that the purchasing price
        will be included. If the article was a doublon the user has to
        reset the purchasing price to zero. The delete form will include
        a field to assert that it is or not a doublon. If doublon.
        """
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


        self.assertEqual(400, Dashboard.total_purchasing_prices(branch=b1))
        self.assertEqual(1400, Dashboard.total_purchasing_prices())

        # total purchasing prices = 1400
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'delete_purchasing_costs': 'False'}
        c.post(reverse('inventory:article_delete', args=[a1b1.pk]), data)

        # costs_grand_total: costs with purchasing prices.
        # if article is deleted a new cost is created with the purchasing price.
        self.assertEqual(400, Dashboard.costs_grand_total(branch=b1))



















