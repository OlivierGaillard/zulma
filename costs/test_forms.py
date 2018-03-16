from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Costs, Category, Enterprise
from .forms import CostsCreateForm, CostsUpdateForm, CategoryCreateForm, EnterpriseCreateForm
#from .views import ArticleDeleteView

class TestInventoryForms(TestCase):

    def setUp(self):
        pass

    def test_enterprise_create_form(self):
        data = {'name' : 'Wonderland'}
        form = EnterpriseCreateForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        form.save()
        self.assertEqual(1, Enterprise.objects.count())

    def test_category_create_form(self):
        data = {'name' : 'canalisations'}
        form = CategoryCreateForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        form.save()
        self.assertEqual(1, Category.objects.count())

    def test_cost_create_form(self):
        category_renovation = Category.objects.create(name='rénovations')
        data = {'name': 'créer fosse septique',
                'amount' : 2000,
                'category' : category_renovation.pk}
        form = CostsCreateForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        form.save()
        self.assertEqual(1, Costs.objects.count())
        self.assertEqual(2000, form.instance.amount)

    def test_cost_update_form(self):
        category_renovation = Category.objects.create(name='rénovations')
        cost = Costs.objects.create(amount=2000, category=category_renovation)
        data = {'name': 'nouvelle fosse', 'amount': 2000, 'category': category_renovation.pk}
        form = CostsUpdateForm(data= data, instance=cost)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        form.save()
        cost_update = Costs.objects.all()[0]
        self.assertEqual('nouvelle fosse', cost_update.name)






