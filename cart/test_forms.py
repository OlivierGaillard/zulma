from django.test import TestCase
from .forms import PaiementCreateForm, PaiementUpdateForm
from .models import Vente
from datetime import date

class TestForm(TestCase):


    def test_paymentCreate(self):
        v = Vente.objects.create(montant=100)
        data = {'montant' : 100, 'vente' : v.pk, 'date' : date.today()}
        f = PaiementCreateForm(data=data)
        self.assertTrue(f.is_valid(), f.errors.as_data())


