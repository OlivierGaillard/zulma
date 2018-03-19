from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Costs, Category, Enterprise
from datetime import date


class TestCostsViews(TestCase):

    def setUp(self):
        User.objects.create_user(username='golivier', password='mikacherie')

    def test_create_one_category(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c.post(reverse('costs:category_create'), data={'name' : 'salary'})
        c.logout()
        self.assertEqual(1, Category.objects.count())

    def test_list_categories(self):
        c1 = Category.objects.create(name='cat1')
        c2 = Category.objects.create(name='cat2')
        self.assertEqual(2, Category.objects.count())
        c = Client()
        url = reverse('costs:categories')
        response = c.get(url)


    def test_category_details(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c.post(reverse('costs:category_create'), data={'name': 'salary'})
        category = Category.objects.all()[0]
        url = reverse('costs:category_details', args=[category.pk])
        response = c.get(url)
        self.assertInHTML('salary', response.content.decode())

    def test_category_update(self):
        c1 = Category.objects.create(name='cat1')
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.post(reverse('costs:category_update', args=[c1.pk]), data={'name': 'salary'}, follow=True)
        # Without follow=True the changes are not saved.
        self.assertInHTML('salary', response.content.decode())
        url = reverse('costs:category_details', args=[c1.pk])
        response = c.get(url)
        self.assertInHTML('salary', response.content.decode())
        c1 = Category.objects.get(pk=c1.pk)
        self.assertEqual('salary', c1.name)

    def test_category_delete(self):
        c1 = Category.objects.create(name='cat1')
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.post(reverse('costs:category_delete', args=[c1.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, Category.objects.count())

    def test_create_one_enterprise(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c.post(reverse('costs:enterprise_create'), data={'name': 'Clean Work'}, follow=False)
        c.logout()
        self.assertEqual(1, Enterprise.objects.count())

    def test_enterprise_details(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c.post(reverse('costs:enterprise_create'), data={'name': 'Clean Work'}, follow=False)
        e = Enterprise.objects.all()[0]
        url = reverse('costs:enterprise_details', args=[e.pk])
        response = c.get(url)
        self.assertInHTML('Clean Work', response.content.decode())

    def test_enterprise_update(self):
        c1 = Enterprise.objects.create(name='Cosas de Casa')
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.post(reverse('costs:enterprise_update', args=[c1.pk]), data={'name': 'Prestige'}, follow=True)
        # Without follow=True the changes are not saved.
        self.assertInHTML('Prestige', response.content.decode())
        url = reverse('costs:enterprise_details', args=[c1.pk])
        response = c.get(url)
        self.assertInHTML('Prestige', response.content.decode())
        c1 = Enterprise.objects.get(pk=c1.pk)
        self.assertEqual('Prestige', c1.name)

    def test_enterprise_delete(self):
        c1 = Enterprise.objects.create(name='Cosas de Casa')
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.post(reverse('costs:enterprise_delete', args=[c1.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, Enterprise.objects.count())


    def test_costs_create(self):
        c = Client()
        c.post('/login/', {'username' : 'golivier', 'password' : 'mikacherie'})
        c1 = Category.objects.create(name='canalisations')
        data = {'amount' : 2000, 'name' : 'fosse septique', 'category' : c1.pk }
        c.post(reverse('costs:costs_create'), data=data, follow=True)
        response = c.get(reverse('costs:costs'))
        self.assertInHTML('fosse septique', response.content.decode())

    def test_costs_details(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c1 = Category.objects.create(name='canalisations')
        e1 = Enterprise.objects.create(name='Clown')
        cost = Costs.objects.create(amount=2000, category=c1, name='fosse', enterprise=e1)
        response = c.get(reverse('costs:costs_details', args=[cost.pk]))
        self.assertEqual(200, response.status_code)
        self.assertInHTML('fosse', response.content.decode())
        self.assertInHTML('Clown', response.content.decode())

    def test_costs_details_enterpriseField_undefined(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c1 = Category.objects.create(name='canalisations')
        cost = Costs.objects.create(amount=2000, category=c1, name='fosse')
        response = c.get(reverse('costs:costs_details', args=[cost.pk]))
        self.assertEqual(200, response.status_code)
        self.assertInHTML('fosse', response.content.decode())



    def test_costs_update(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c1 = Category.objects.create(name='canalisations')
        cost = Costs.objects.create(amount = 2000, category = c1)
        data = {'name' : 'fosse'}
        response = c.post(reverse('costs:costs_update', args=[cost.pk]), data=data, follow=True )
        self.assertEqual(200, response.status_code)

    def test_costs_delete(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c1 = Category.objects.create(name='canalisations')
        cost = Costs.objects.create(amount = 2000, category = c1)
        response = c.post(reverse('costs:costs_delete', args=[cost.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, Costs.objects.count())

    def test_costs_billing_date_in_main_costs_list(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c1 = Category.objects.create(name='canalisations')
        billing_date = date(year=2018, month=3, day=16)
        cost = Costs.objects.create(amount=2000, category=c1, name='fosse', billing_date=billing_date)
        response = c.get(reverse('costs:costs'))
        self.assertEqual(200, response.status_code)
        self.assertInHTML('Billing Date', response.content.decode())





