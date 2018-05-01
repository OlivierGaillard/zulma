from behave import given, when, then
from cart.models import Vente, CartItem
from costs.models import Category as CostsCategory
from costs.models import Costs
from inventory.models import Article
from django.contrib.auth.models import User
from django.shortcuts import reverse
from hamcrest import *

@given(u'There exists one selling of "{amount}" which is "{selling_state}"')
def there_exists_one_selling_of_amount(context, amount, selling_state):
    if selling_state == 'closed':
        Vente.objects.create(montant=amount, reglement_termine=True)
    else:
        Vente.objects.create(montant=amount, reglement_termine=False)

@when(u'I make one selling of "{amount}"')
def one_selling_of(context, amount):
    Vente.objects.create(montant=amount, reglement_termine=True)

@then(u'the total of sellings must be "{total}"')
def total_must_be(context, total):
    total_found = Vente.objects.total_sellings()
    assert_that(total_found, equal_to(float(total)))

@then(u'the quantity of sellings must be "{quantity}"')
def quantity_of_selling_must_be(context, quantity):
    assert_that(int(quantity), equal_to(Vente.objects.count()))


@given(u'There is one article "{name}" with quantity "{quantity}"')
def step_impl(context, name, quantity):
    Article.objects.create(name=name, quantity=int(quantity))
    assert_that(1, equal_to(Article.objects.count()))

@when(u'I make one selling with quantity "{quantity}" of "{name}" for one amount of "{amount}" and payments are "{selling_state}"')
def step_impl(context, quantity, name, amount, selling_state):
    selling_status = False
    if selling_state == 'closed':
        selling_status = True
    Vente.objects.create(montant=amount, reglement_termine=selling_status)
    article = Article.objects.get(name=name)
    article.quantity = article.quantity - int(quantity)
    article.save()

@then(u'The stock quantity of "{name}" must be "{quantity}"')
def step_impl(context, name, quantity):
    article = Article.objects.get(name=name)
    assert_that(article.quantity, equal_to(int(quantity)))


@given(u'User "{username}" with password "{password}" exist')
def step_impl(context, username, password):
    user = User.objects.create_user(username=username, password=password)
    assert_that(1, equal_to(User.objects.count()))

@when(u'This user visit "{url}"')
def step_impl(context, url):
    context.response = context.test.client.get(url)

@then(u'It is logged')
def step_impl(context):
    assert_that(200, equal_to(context.response.status_code))

@when(u'This user adds the article to its cart by visiting "{url}" with quantity "{quantity}"')
def step_impl(context, url, quantity):
    article = Article.objects.get(name='plate')
    context.response = context.test.client.post(url + '/' + str(article.pk))
    assert_that(1, equal_to(CartItem.objects.count()))
    data = {'new_quantity': quantity, 'new_price': "50"}
    cart_item = CartItem.objects.all()[0]
    context.test.client.post(reverse('cart:save_cart_item', args=[cart_item.pk]), data=data)


@then(u'There exists one cart-item with quantity "{quantity}"')
def step_impl(context, quantity):
    cart_item = CartItem.objects.all()[0]
    assert_that(int(quantity), equal_to(cart_item.quantity))


@given(u'one category named "{catname}" exists')
def step_impl(context, catname):
    costs_category = CostsCategory.objects.create(name=catname)
    assert_that(costs_category, is_not(None))

@given(u'one new cost of this category "{catname}" with amount "{amount}" is added')
def step_impl(context, catname, amount):
    category = CostsCategory.objects.get(name=catname)
    Costs.objects.create(category=category, amount=float(amount))



@given(u'a set of articles')
def step_impl(context):
    photo_template = "photo_{0}"
    photo_nb = 0
    for row in context.table:
        photo_nb += 1
        photo = photo_template.format(photo_nb)
        Article.objects.create(name=row['name'], purchasing_price=float(row['purchasing_price']),
                               selling_price=float(row['selling_price']), quantity=int(row['quantity']),
                               photo=photo)
        Vente.objects.create(reglement_termine=True, montant=row['selling_amount'])
    assert_that(Article.objects.count(), equal_to(2))



@then(u'the total purchasing price is "{total:f}"')
def step_impl(context, total):
    assert_that(total, Article.objects.total_purchasing_price())


@then(u'the total of the sellings is "{total_selling:f}"')
def step_impl(context, total_selling):
    assert_that(total_selling, equal_to(Vente.objects.total_sellings()))




@then(u'The total of costs is "{total:f}"')
def step_impl(context, total):
    assert_that(total, equal_to(Costs.objects.total_costs()))


@then(u'The grand total with purchases is "{grand_total:f}"')
def step_impl(context, grand_total):
    assert_that(grand_total, equal_to(Costs.objects.grand_total()))

@then(u'The balance is "{balance:f}"')
def step_impl(context, balance):
    assert_that(balance, equal_to(Costs.objects.get_balance()))







