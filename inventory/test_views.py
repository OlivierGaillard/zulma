from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article
#from .views import ArticleDeleteView

class TestInventoryViews(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10)
        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_delete_view(self):
        self.assertEqual(1, Article.objects.count())
        c = Client()
        response = c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.post(reverse('inventory:article_delete', args=[self.a1.pk]), follow=False)
        c.logout()
        self.assertEqual(0, Article.objects.count())




