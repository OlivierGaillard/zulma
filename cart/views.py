from django.shortcuts import render, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from crispy_forms.bootstrap import PrependedText
from crispy_forms.bootstrap import TabHolder, Tab, FormActions
from crispy_forms.layout import Submit, Layout, Fieldset, Field
from .models import CartItem, Vente, Client, Paiement
from .forms import VenteCreateForm, ClientCreateForm, PaiementCreateForm, VenteDeleteForm, VenteUpdateForm, ClientUpdateForm
from .forms import PaiementUpdateForm
from django.forms import formset_factory, modelformset_factory, BaseModelFormSet
from inventory.models import Article
from .cartutils import is_cart_id_session_set, _set_or_get_session_id, get_cart_items, get_cart_id_session
from .cartutils import  get_cart_item_of_book, article_already_in_cart, get_cart_counter, _remove_cart_item, cart_not_complete
from .cartutils import remove_cart_id_from_session
import logging

logger = logging.getLogger('django')


def add_cart_counter_to_context(request, ctx):
    ctx['cart_counter'] = get_cart_counter(request)
    return ctx

def add_cart_item(request, pk):
    if request.method == 'POST':
        article = Article.objects.get(pk=pk)
        cart_items = get_cart_items(request)
        if article_already_in_cart(cart_items, article):
            cart_item = get_cart_item_of_book(cart_items, article)
            cart_item.augment_quantity(1)
            cart_item.save()
            logger.info('add_cart_item: another one item of article {0}'.format(article))
        else:
            if article.quantity > 0:
                cart_item = CartItem()
                cart_item.cart_id = _set_or_get_session_id(request)
                msg = 'add_cart_item: Session-ID: {0}'.format(cart_item.cart_id)
                logger.info(msg)
                cart_item.article = article
                cart_item.quantity = 1
                cart_item.prix = article.selling_price
                cart_item.save()
                logger.info('add_cart_item: Article {0} added to the cart.'.format(article))
            else:
                logger.warning('add_cart_item: out of stock for article {0}'.format(article))
                return HttpResponse("Quantite en stock insuffisante!")
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        logger.warning('add_cart_item called with method GET. Not normal!')
        print('not a POST?')
        pass

def remove_cart_item(request, pk):
    if request.method == 'POST':
        cart_items = get_cart_items(request)
        vente = cart_items[0].vente
        article = Article.objects.get(pk=pk)
        _remove_cart_item(request, article)
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        raise ValueError('Should not be called with GET')


def remove_article_from_vente_and_update_article_quantity(request, pk):
    """pk is the one of cart_item, its ID."""
    if request.method == 'GET':
        logger.info('remove_article_from_vente_and_update_article_quantity:...')
        cart_item = CartItem.objects.get(pk=pk)
        vente = cart_item.vente
        article = Article.objects.get(pk=cart_item.article.pk)
        logger.debug('Article: {0}'.format(article))
        article.quantity += cart_item.quantity
        article.save()
        logger.debug('Article quantity: {0}'.format(article.quantity))
        logger.debug('Quantity of article will be added by {0}. END of remove...'.format(cart_item.quantity))
        cart_item.delete()
#        url_redirect = reverse('cart:vente_update', kwargs={'pk':vente.pk})
        return HttpResponseRedirect("/cart/vente_update/%s" % vente.pk)

def save_cart_item(request, pk):
    if request.method == 'POST':
        cart_item = CartItem.objects.get(pk=pk)
        new_quantity = request.POST.get('new_quantity', '')
        new_quantity = int(new_quantity)
        logger.debug('save_cart_item: new quantity: %s' % str(new_quantity))
        msg = cart_item.set_quantity(new_quantity)
        if msg:
            logger.warning('msg: %s' % msg)
        price = request.POST.get('new_price', '')
        logger.debug('save_cart_item: new_price: %s' % price)
        if len(price) == 0:
            # assuming zero
            price = "0"
        cart_item.prix = float(price)

        if cart_item.prix == 0:
            logger.warning("save_cart_item: The amount of article is zero!")
            return render(request, 'cart/cart_content.html',
                          {'error_message': "The amount of article is zero!",
                           'cart': get_cart_items(request), 'new_price': price,
                           })
        cart_item.save()
        logger.debug('save_cart_item: Item saved.')
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        raise ValueError('cart:views:edit_price: should not be called with GET')


def edit_price(request, pk):
    if request.method == 'POST':
        cart_item = CartItem.objects.get(pk=pk)
        price = request.POST.get('new_price', '')
        logger.debug('new_price: %s' % price)
        if len(price) == 0:
            # assuming zero
            price = "0"
        logger.debug('converting in float..')
        cart_item.prix = float(price)
        logger.debug('DONE.')
        cart_item.save()
        if cart_item.prix == 0:
            return render(request, 'cart/cart_content.html',
                          {'error_message' : "The amount is zero!",
                           'cart' : get_cart_items(request), 'new_price' : price,
                           })
        cart_item.save()
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        raise ValueError('cart:views:edit_price: should not be called with GET')

def edit_quantity(request, pk):
    logger.debug('in edit_quantity view of app "cart"')
    if request.method == "POST":
        cart_item = CartItem.objects.get(pk=pk)
        quantity = cart_item.quantity
        logger.debug('original quantity: %s' % str(quantity) )
        new_quantity = request.POST.get('new_quantity', '')
        new_quantity = int(new_quantity)
        logger.debug('new quantity: %s' % str(new_quantity))
        msg = cart_item.set_quantity(new_quantity)
        logger.warning('msg: %s' % msg)
        cart_item.save()
        logger.debug('new quantity set and saved')
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect, {'warning' : msg })
    else:
        raise ValueError('cart:views:edit_quantity: should not be called with GET')


# This import must be defined here, after the functions definition and not before,
# otherwise it fails.

class BaseCartItemFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseCartItemFormSet, self).__init__(*args, **kwargs)
        self.queryset = get_cart_items(self.request)

class CartView(ListView):
    """When the cart is validated the cart_items have the status
    'cart_complete' = True. It is better to remove the 'session_id'
    from the request?
    """
    model = CartItem
    template_name = 'cart/cart_content.html'
    context_object_name = 'cart'

    def get_queryset(self):
        if is_cart_id_session_set(self.request):
            qs = CartItem.objects.filter(cart_id = get_cart_id_session(self.request))
            qs = qs.exclude(cart_complete=True)
            return qs #CartItem.objects.filter(cart_id = get_cart_id_session(self.request))
        else:
            return []

    def get_context_data(self, **kwargs):
        ctx = super(CartView, self).get_context_data(**kwargs)
        if  is_cart_id_session_set(self.request):
            cart_id = get_cart_id_session(self.request)
            ctx['cart_total'] = CartItem.get_total_of_cart(cart_id)
            ctx['cart'] = get_cart_items(self.request)
            return ctx
        else:
            cart_items_formset = modelformset_factory(CartItem, fields=('article', 'prix', 'quantity', ),
                                                      formset=BaseCartItemFormSet)

            return ctx


class CheckoutView(CreateView):
    """Crée le formulaire de la vente avec la liste des articles mis dans le panier.
    Le montant est pré-renseigné. """
    model = Vente
    template_name = 'cart/checkout.html'
    context_object_name = 'cart'
    form_class = VenteCreateForm

    def get_context_data(self, **kwargs):
        logger.debug('CheckoutView: get_context_data')
        ctx = super(CheckoutView, self).get_context_data(**kwargs)

        if is_cart_id_session_set(self.request):
            cart_id = get_cart_id_session(self.request)
            ctx['cart_total'] = CartItem.get_total_of_cart(cart_id)
            ctx['cart'] = get_cart_items(self.request)
            return ctx
        else:
            return ctx

    def get_initial(self):
        logger.debug('CheckoutView: get_initial')
        initial = super(CheckoutView, self).get_initial()
        session_id = get_cart_id_session(self.request)
        logger.info('get_initial: Session-ID: {0}'.format(session_id))
        initial['montant'] = CartItem.get_total_of_cart(session_id)
        # trying to get branch from article, if any
        try:
            items = get_cart_items(self.request)
            cart_item  = items[0]
            logger.debug('CheckoutView: Article Name: %s / Branch: [%s]' % (cart_item.article.name, cart_item.article.branch))
            initial['branch'] = cart_item.article.branch
        except IndexError:
            logger.info("CheckoutView: No branch defined for article in cart.")
        return  initial

    def form_valid(self, form):
        logger.debug('In CheckoutView: form_valid')
        self.object = form.save()
        cart_items = get_cart_items(request=self.request)
        for cart in cart_items:
            cart.cart_complete = True
            cart.vente = self.object
            cart.save()
            cart.update_article_quantity()
        remove_cart_id_from_session(self.request)
        logger.info('cart_id removed from session. End of form_valid of CheckoutView.')
        return super(CheckoutView, self).form_valid(form)

@method_decorator(login_required, name='dispatch')
class VenteDetail(DetailView):
    model = Vente
    template_name = 'cart/vente.html'
    context_object_name = 'vente'


@method_decorator(login_required, name='dispatch')
class VenteUpdateView(UpdateView):
    model = Vente
    template_name = 'cart/vente_update.html'
    context_object_name = 'vente'
    form_class = VenteUpdateForm

@method_decorator(login_required, name='dispatch')
class VenteListView(ListView):
    model = Vente
    template_name = 'cart/ventes.html'
    context_object_name = 'ventes'

    def get_context_data(self, **kwargs):
        ctx = super(VenteListView, self).get_context_data(**kwargs)
        li = Vente.objects.all()
        total = 0
        for v in li:
            total += v.montant
        ctx['total'] = total
        return ctx


# class VenteDeleteView(DeleteView):
#     model = Vente
#     template_name = 'cart/vente_delete.html'
#     form_class = VenteDeleteForm

def vente_delete(request, pk):
    if request.method == "GET":
        vente = Vente.objects.get(pk=pk)
        vente.delete()
        return HttpResponseRedirect("/cart/ventes/")
    else:
        print('POST? strange')


@method_decorator(login_required, name='dispatch')
class ClientListView(ListView):
    model = Client
    template_name = 'cart/clients.html'
    context_object_name = 'clients'

@method_decorator(login_required, name='dispatch')
class ClientDetailView(DetailView):
    model = Client
    template_name = 'cart/client.html'
    context_object_name = 'client'

@method_decorator(login_required, name='dispatch')
class ClientCreateView(CreateView):
    model = Client
    template_name = 'cart/client_create.html'
    form_class = ClientCreateForm


@method_decorator(login_required, name='dispatch')
class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'cart/client_delete.html'
    #form_class = ClientDeleteForm
    success_url = '/cart/clients'


@method_decorator(login_required, name='dispatch')
class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'cart/client_update.html'
    form_class = ClientUpdateForm


@method_decorator(login_required, name='dispatch')
class PaiementListView(ListView):
    model = Paiement
    template_name = 'cart/paiements.html'
    context_object_name = 'paiements'


@method_decorator(login_required, name='dispatch')
class PaiementCreateView(CreateView):
    model = Paiement
    template_name = 'cart/paiement_create.html'
    form_class = PaiementCreateForm

login_required()
def add_paiement(request, vente_pk):
    """Add a paiement to a vente.
    return render(request, 'polls/detail.html', {'question': question})

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

    """
    # TODO: add validation for selling balance: montant paiement pas superieur au montant de la vente
    logger.debug('In add_paiement')
    template_name = 'cart/paiement_add.html'
    vente = get_object_or_404(Vente, pk=vente_pk)
    logger.debug('Vente instance retrieved.')
    logger.debug('Amount of this "Vente": ', vente.montant)

    if request.method == 'POST':
        logger.debug('in POST')
        form = PaiementCreateForm(request.POST)
        logger.debug('before calling form.is_valid()')
        if form.is_valid():
            logger.debug('IS valid.')
            logger.debug('Setting the "Vente" instance to the payment...')
            montant = form.cleaned_data['montant']
            p = Paiement.objects.create(montant=montant, date=form.cleaned_data['date'], vente=vente,
                                        payment_mode=form.cleaned_data['payment_mode'])
            logger.debug('Payment-ID [%s] created.' % p.pk)
            logger.debug('Payment amount: [%s]' % p.montant)
            logger.debug('Saved. Will update selling.')
            if vente.solde_paiements() == 0:
                vente.reglement_termine = True
            else:
                vente.reglement_termine = False
            vente.save()
            logger.debug('Vente: %s' % vente)
            url_redirect = reverse('cart:vente', args=[vente.pk])
            return HttpResponseRedirect(url_redirect)
        else:
            logger.debug('IS NOT valid.')
            logger.debug(form.errors.as_data())
            return render(request=request, template_name=template_name, context={'form': form,
                                                                             'solde': vente.solde_paiements()})
    else:
        logger.debug('in GET.')
        logger.debug('Vente ID: %s' % vente.pk)
        vente_solde = vente.solde_paiements()
        logger.debug('Solde: [%s}' % vente_solde)
        date_vente = datetime.datetime(year=vente.date.year, month=vente.date.month, day=vente.date.day,
                                       hour=vente.date.hour, minute=vente.date.minute)
        form = PaiementCreateForm(initial={'date' : date_vente, 'montant' : vente_solde, 'payment_mode' : 'C'})
        # form = PaiementCreateForm(
        #     initial={'vente': vente, 'date': date_vente, 'payment_mode': 'C'})
        # add prepended text here
        #form.helper.layout.append(PrependedText('montant', 'Max: ' + str(vente_solde)))

        # form.helper.layout.append(
        #     FormActions(
        #         Submit('save', 'Submit'),
        #     )
        # )

        return render(request=request, template_name=template_name, context={'form': form,
                                                                             'solde': vente_solde})


@method_decorator(login_required, name='dispatch')
class PaiementDetailView(DetailView):
    model = Paiement
    template_name = 'cart/paiement.html'
    context_object_name = 'paiement'

@method_decorator(login_required, name='dispatch')
class PaiementUpdateView(UpdateView):
    model = Paiement
    template_name = 'cart/paiement_update.html'
    context_object_name = 'paiement'
    form_class = PaiementUpdateForm




