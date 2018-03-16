from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article
from .forms import ArticleUpdateForm, ArticleLossesForm
#from .views import ArticleDeleteView

class TestInventoryForms(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10)

    def test_quantity_of_losses(self):
        data = {'losses' : 1}
        form = ArticleLossesForm(instance=self.a1, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        form.save()
        self.assertEqual(1, self.a1.losses)

    def test_article_quantity_is_updated_after_losses(self):
        data = {'losses': 1}
        form = ArticleLossesForm(instance=self.a1, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        form.save()
        self.assertEqual(9, self.a1.quantity)

    def test_losses_exceed_quantity(self):
        """The losses cannot be greater than the quantity"""
        data = {'losses': 200}
        form = ArticleLossesForm(instance=self.a1, data=data)
        self.assertFalse(form.is_valid(), form.errors.as_data())





