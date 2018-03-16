from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article
#from .views import ArticleDeleteView

class TestInventoryViews(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10, photo='a1')
        self.a2 = Article.objects.create(name='a2', quantity=5, photo='a2')
        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def btest_delete_view(self):
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
        data = {'losses' : 1}
        response = c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=False)
        c.logout()
        self.assertEqual(9, self.a1.quantity)
        self.assertEqual(1, self.a1.losses)







