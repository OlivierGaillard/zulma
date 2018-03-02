from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article
#from .views import ArticleDeleteView
class TestInventoryViews(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10)
        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_article_date_added(self):
        d = self.a1.date_added
        self.assertIsNotNone(d)

    def test_article_initial_quantity(self):
        self.assertEqual(self.a1.initial_quantity, 1)






