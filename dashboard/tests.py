from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from cart.models import Vente
from costs.models import Costs, Category
from inventory.models import Article, Arrivage
import datetime

class TestDashboard(TestCase):

    def setUp(self):
        arrival = Arrivage.objects.create(nom="test", date_arrivee=datetime.date.today())
        a1 = Article.objects.create(name='a1', quantity=10, photo='a1', arrival=arrival, purchasing_price=100)
        a2 = Article.objects.create(name='a2', quantity=5, photo='a2', arrival=arrival,  purchasing_price=100)

        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_balance_view(self):
        Vente.objects.create(montant=20, reglement_termine=True)
        cost_catego = Category.objects.create(name='Divers')
        Costs.objects.create(category=cost_catego, amount=10)
        self.assertEqual(10, Costs.objects.total_costs())
        self.assertEqual(200, Article.objects.total_purchasing_price())
        self.assertEqual(20-210, Costs.objects.get_balance())
        self.assertEqual(20, Vente.objects.total_sellings())
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.get(reverse('dashboard:main'))
        self.assertEqual(200, response.status_code)
        html = response.content.decode()
        self.assertInHTML('210,00', html)
        self.assertInHTML('-190,00', html)
        self.assertInHTML('20,00', html)
        self.assertInHTML('200,00', html)
        c.logout()





