from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article
from .forms import ArticleUpdateForm, ArticleLossesForm
#from .views import ArticleDeleteView

class TestInventoryForms(TestCase):

    def setUp(self):
        pass

    def test_quantity_of_losses(self):
        data = {'losses' : 1, 'amount_losses' : 200}
        form = ArticleLossesForm(data=data)
        self.assertTrue(form.is_valid())

    def test_add_loss_quantity_zero(self):
        data = {'losses': 0, 'amount_losses': 0}
        form = ArticleLossesForm(data=data)
        self.assertFalse(form.is_valid())


    def test_add_loss_but_with_amount_zero(self):
        data = {'losses': 1, 'amount_losses': 0}
        form = ArticleLossesForm(data=data)
        self.assertFalse(form.is_valid())

    def test_add_loss_but_with_minimum_amount(self):
        data = {'losses': 1, 'amount_losses': 0.1}
        form = ArticleLossesForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())












