from django.db import models
from inventory.models import Article, Branch
from cart.models import Vente
from costs.models import Costs, Category

# Create your models here.
class Dashboard:
    """Utility class to get costs, sellings and balances of branches."""

    def total_purchasing_prices(branch=None):
        return Article.objects.total_purchasing_price(branch=branch)

    def total_costs(branch=None):
        return Costs.objects.total_costs(branch=branch)

    def costs_grand_total(branch=None):
        """Purchases and Costs"""
        return Costs.objects.grand_total(branch=branch)

    def get_balance(branch=None):
        return Costs.objects.get_balance(branch=branch)
