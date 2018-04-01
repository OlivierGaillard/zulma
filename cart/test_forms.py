from django.test import TestCase
from django import forms
from .forms import PaiementCreateForm, PaiementUpdateForm
from .models import Vente
from datetime import datetime

class TestForm(TestCase):


    def test_paymentCreate(self):
        data = {'montant' : 100, 'date' : datetime.now(), 'payment_mode' : 'C'} # Cash
        f = PaiementCreateForm(data=data)
        self.assertTrue(f.is_valid(), f.errors.as_data())

    def test_paymentCreate_initial(self):
        initial_data = {'montant': 40, 'date': '2018-04-01 9:45:00', 'payment_mode': 'C'}  # Cash
        new_data = {'montant': 40, 'payment_mode': 'B', 'date': '2018-04-01 9:45:00'}  # Bank
        f = PaiementCreateForm(data=new_data, initial=initial_data)
        self.assertTrue(f.has_changed())
        self.assertTrue(f.is_valid(), f.errors.as_data())






