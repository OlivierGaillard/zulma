from behave import given, when, then
from cart.models import Vente, CartItem
from costs.models import Category as CostsCategory
from costs.models import Costs
from inventory.models import Article, Losses
from django.contrib.auth.models import User
from django.shortcuts import reverse
from hamcrest import *

@when(u'one loss of quantity "{quantity}" with amount "{amount}" is added')
def step_impl(context, quantity, amount):
    Losses.objects.create(losses=quantity, amount_losses=amount)

@then(u'the total of losses is "{amount_losses:f}"')
def step_impl(context, amount_losses):
    assert_that(amount_losses, equal_to(Losses.objects.total_costs()))


