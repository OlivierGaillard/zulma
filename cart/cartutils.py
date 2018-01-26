import random
from .models import CartItem
import pdb

CART_ID_SESSION_KEY = 'cart_id'


def is_cart_id_session_set(request):
    return len(request.session.get(CART_ID_SESSION_KEY, '')) > 0

def _generate_cart_id():
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
    cart_id_length = 50
    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id

def _set_or_get_session_id(request):
    if not is_cart_id_session_set(request):
        request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
    return request.session[CART_ID_SESSION_KEY]


def get_cart_id_session(request):
    return request.session.get(CART_ID_SESSION_KEY, '')


def remove_cart_id_from_session(request):
    if is_cart_id_session_set(request):
        del request.session[CART_ID_SESSION_KEY]


def get_cart_items(request):
    """return all items from the current user's cart."""
    return CartItem.objects.filter(cart_id = get_cart_id_session(request))

def cart_not_complete(request):
    cart_items = get_cart_items(request)
    if cart_items:
        one_cart_item = cart_items[0]
        return one_cart_item.cart_complete == False
    else:
        # not yet cart_item, then it is TRULY not complete!
        return True

def get_cart_item_of_book(cart_items, article):
    cart_items_li = [ cart_item for cart_item in cart_items if cart_item.article == article ]
    if len(cart_items_li) == 1:
        return cart_items_li[0]
    else:
        return None

def _remove_cart_item(request, article):
    """Remove the cart_item of the book."""
    cart_items = get_cart_items(request)
    if cart_items:
        cart_item_of_book = get_cart_item_of_book(cart_items, article)
        cart_item_of_book.delete()

def article_already_in_cart(cart_items, article):
    articles_pk_list = [ cart_item.article.pk for cart_item in cart_items ]
    return article.pk in articles_pk_list

def get_cart_counter(request):
    """Return the total of items in cart."""
    return len(get_cart_items(request))

