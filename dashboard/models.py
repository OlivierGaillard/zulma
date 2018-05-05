from django.db import models
from inventory.models import Article, Branch, Losses
from cart.models import Vente
from costs.models import Costs, Category

# Create your models here.
class Dashboard:
    """Utility class to get costs, sellings and balances of branches.
    If the branch is set to 'MAIN' the instances with branch == None are used.
    """

    def total_purchasing_prices(branch=None, year=None, start_date=None, end_date=None):
        return Article.objects.total_purchasing_price(branch=branch, start_date=start_date, end_date=end_date)

    def total_costs(branch=None, year=None, start_date=None, end_date=None):
        return Costs.objects.total_costs(branch=branch, start_date=start_date, end_date=end_date)

    def costs_grand_total(branch=None, year=None, start_date=None, end_date=None):
        """Purchases and Costs"""
        return Costs.objects.grand_total(branch=branch, start_date=start_date, end_date=end_date)

    def total_losses(branch=None, year=None, start_date=None, end_date=None):
        """
        If branch is empty all losses are returned, MAIN included.
        :return: the total amount currency
        """
        return Losses.objects.total_costs(branch=branch, start_date=start_date, end_date=end_date)

    def total_quantity_losses(branch=None, year=None, start_date=None, end_date=None):
        """
        Return not a currency amount.
        :return: number of losses
        """
        return Losses.objects.total_quantity(branch=branch, start_date=start_date, end_date=end_date)

    def get_balance(branch=None, year=None, start_date=None, end_date=None):
        return Costs.objects.get_balance(branch=branch, start_date=start_date, end_date=end_date)
