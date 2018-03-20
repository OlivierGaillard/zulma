from django.test import TestCase
from .models import Enterprise, Category, Costs
from datetime import date

class TestModels(TestCase):

    def setUp(self):
        self.e3 = Enterprise.objects.create(name='Zorro')
        self.e1 = Enterprise.objects.create(name='Cosas de Casa')
        self.e2 = Enterprise.objects.create(name='Métacohérence')

        self.c5 = Category.objects.create(name='zeta')
        self.c1 = Category.objects.create(name='entretien')
        self.c2 = Category.objects.create(name='salaires')
        self.c3 = Category.objects.create(name='location')
        self.c4 = Category.objects.create(name='électricité')


    def test_cost_one_can_be_created(self):
        cos1 = Costs.objects.create(category=self.c1, amount=100)
        self.assertIsNotNone(cos1)

    def test_cost_one_amount(self):
        cos1 = Costs.objects.create(category=self.c1, amount=100)
        self.assertEqual(100, cos1.amount)


    def test_cost_one_print(self):
        cos1 = Costs.objects.create(category=self.c1, amount=100)
        s = "Amount: % s / Category: % s / Date: % s " % (cos1.amount, cos1.category, cos1.creation_date)
        self.assertEqual(s, str(cos1))

    def test_enterprise_ordered(self):
        li = Enterprise.objects.all()
        self.assertEqual('Cosas de Casa', li[0].name)

    def test_categories_ordered(self):
        li = Category.objects.all()
        self.assertEqual('électricité', li[0].name)

    def test_cost_dates(self):
        billing_date = date(year=2018, month=3, day=16)
        cost1 = Costs.objects.create(category=self.c1, amount=100, billing_date=billing_date)
        self.assertEqual(billing_date, cost1.billing_date)

    def test_total_costs_for_no_costs(self):
        self.assertEqual(0, Costs.objects.total_costs())

    def test_total_costs_for_one_cost(self):
        c = Costs.objects.create(category=self.c1, amount=100)
        self.assertEqual(100, Costs.objects.total_costs())

    def test_total_costs_for_two_costs(self):
        c = Costs.objects.create(category=self.c1, amount=100)
        Costs.objects.create(category=self.c1, amount=100.50)
        self.assertEqual(200.5, Costs.objects.total_costs())


