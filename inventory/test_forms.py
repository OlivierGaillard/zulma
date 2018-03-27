from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article
from .forms import ArticleUpdateForm, ArticleLossesForm
#from .views import ArticleDeleteView

class TestInventoryForms(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10, losses=0, photo='a1')

    def test_quantity_of_losses(self):
        data = {'losses' : 1, 'amount_losses' : 200}
        form = ArticleLossesForm(instance=self.a1, data=data)
        self.assertTrue(form.is_valid())

    def test_losses_exceed_quantity(self):
        """The losses cannot be greater than the quantity"""
        data = {'losses': 200,}
        form = ArticleLossesForm(instance=self.a1, data=data)
        self.assertFalse(form.is_valid(), form.errors.as_data())


    def test_addone_but_stock_empty(self):
        a = Article.objects.create(name='yero', quantity=0, losses=0, photo='yero')
        data = {'losses': 1, }
        form = ArticleLossesForm(instance=a, data=data)
        self.assertFalse(form.is_valid(), form.errors.as_data())










