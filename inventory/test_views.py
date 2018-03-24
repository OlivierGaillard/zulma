from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article
from costs.models import Costs
#from .views import ArticleDeleteView

class TestInventoryViews(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10, photo='a1')
        self.a2 = Article.objects.create(name='a2', quantity=5, photo='a2')
        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_delete_view(self):
        self.assertEqual(2, Article.objects.count())
        c = Client()
        response = c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.post(reverse('inventory:article_delete', args=[self.a1.pk]), follow=False)
        c.logout()
        self.assertEqual(1, Article.objects.count())

    def btest_articles_list_filter(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.get('/inventory/articles/', {'name__icontains' : 'a1'})
        response_str = response.content.decode()
        self.assertInHTML('a1', response_str, count=1)

    def test_article_losses_view(self):
        self.assertEqual(0, self.a1.losses)
        c = Client()
        response = c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses' : 1, 'amount_losses' : 20}
        response = c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        c.logout()
        a1_upated = Article.objects.get(pk=self.a1.pk)
        self.assertEqual(9, a1_upated.quantity)
        self.assertEqual(1, a1_upated.losses)
        self.assertTrue(Costs.objects.count() == 1)
        cost = Costs.objects.all()[0]
        self.assertEqual(cost.amount, 20)

    def test_error_msg(self):
        c = Client()
        response = c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses': 12, 'amount_losses': 20} # article a1 quantity = 10
        response = c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        msg = "Losses (12) cannot exceed quantity (1)."
        self.assertInHTML(msg, response.content.decode())

    def test_losses_form_display_previous_losses_info(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.get(reverse('inventory:article_losses', args=[self.a1.pk]))
        self.assertInHTML('Previous losses:', response.content.decode())










