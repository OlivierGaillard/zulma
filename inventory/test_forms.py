from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article, Arrivage, Branch, Category
from .forms import ArticleUpdateForm, ArticleLossesForm, BranchCreateForm, HandlePicturesForm, ArticleDeleteForm
from datetime import date

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

    def test_edit_branch_of_article(self):
        arrival = Arrivage.objects.create(nom="test", date_arrivee=date.today())
        a1 = Article.objects.create(name='a1', quantity=10, photo='a1', arrival=arrival)
        branch = Branch.objects.create(name='b1')
        data = {'branch' : branch.pk, 'solde': 'N', 'initial_quantity': 1, 'quantity': 1, 'arrival': arrival.pk}
        form = ArticleUpdateForm(data=data, instance=a1)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_create_branch(self):
        data = {'name' : 'Boutique'}
        form = BranchCreateForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_handlepictures(self):
        bra = Branch.objects.create(name='Boutique')
        cat = Category.objects.create(name='Chaussures')
        arr = Arrivage.objects.create(nom="test", date_arrivee=date.today())
        data = {'branch' : bra.pk, 'arrival' : arr.pk, 'category' : cat.pk}
        form = HandlePicturesForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_handlepictures_no_branch(self):
        cat = Category.objects.create(name='Chaussures')
        arr = Arrivage.objects.create(nom="test", date_arrivee=date.today())
        data = {'arrival' : arr.pk, 'category' : cat.pk}
        form = HandlePicturesForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        self.assertIsNone(form.cleaned_data['branch'])
        art = Article.objects.create(name='a1', quantity=10, photo='a1', arrival=form.cleaned_data['arrival'],
                                     category=form.cleaned_data['category'],
                                     branch=form.cleaned_data['branch'])
        self.assertIsNotNone(art)


    def test_delete_article_form_with_doublon_checkbox_checked(self):
        f = ArticleDeleteForm(data={'delete_purchasing_costs' : True})
        self.assertTrue(f.is_valid())

    def test_delete_article_form_with_doublon_checkbox_unchecked(self):
        f = ArticleDeleteForm(data={'delete_purchasing_costs': False})
        self.assertTrue(f.is_valid())

