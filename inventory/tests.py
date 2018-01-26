from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.test.utils import isolate_apps
from .forms import ArticleCreateForm
from .models import Article, Enterprise, Arrivage, Marque, Employee



# Create your tests here.
class TestInventory(TestCase):

    def setUp(self):

        self.enterprise = Enterprise.objects.create(name='Gogol')
        self.arrivage   = Arrivage.objects.create(nom='Sebastopol', date_arrivee="2017-12-12",
                                             proprietaire=self.enterprise)
        self.marque_Supra = Marque.objects.create(nom='Supra')
        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')
        self.employe = Employee.objects.create(user=self.user_oga, enterprise=self.enterprise)

        self.article1 = Article.objects.create(nom='Article-1', marque=self.marque_Supra,
                                          entreprise=self.enterprise, quantite=5,
                                          arrivage=self.arrivage, prix_total=2000)


    #@isolate_apps('inventory')
    def test_createForm(self):
        data = {'type_client': 'F',
                'genre_article' : 'V',
                'nom': 'Test-1', 'marque': 'Babar',
                'marque' : self.marque_Supra.pk,
                'entreprise' : self.enterprise.pk,
                'quantite': 5,
                'arrivage': self.arrivage.pk,
                'prix_unitaire' : '2500',
                'prix_total' : '2500',
                'remise' : 5.0,
                }
        form = ArticleCreateForm(data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_get_article1(self):
        article = Article.objects.get(pk=self.article1.pk)
        self.assertIsNotNone(article)

    def test_user_can_access_article_create(self):
        c = Client()
        response = c.post('/accounts/login/', {'username' : 'golivier', 'password' : 'mikacherie'})

        data = {'type_client': 'F',
                'genre_article': 'V',
                'nom': 'Test-1', 'marque': 'Babar',
                'marque': self.marque_Supra.pk,
                'entreprise': self.enterprise.pk,
                'quantite': 5,
                'arrivage': self.arrivage.pk,
                'prix_unitaire': '2500',
                'prix_total': '2500',
                'remise': 5.0,
                }

        response = c.post(reverse('inventory:article_create'), data=data, follow=False)
        print(response.templates)
        c.logout()

        self.assertEqual(2, Article.objects.count())
