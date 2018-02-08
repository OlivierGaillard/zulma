from django.shortcuts import render, reverse
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from crispy_forms.bootstrap import PrependedText
from crispy_forms.bootstrap import TabHolder, Tab, FormActions
from crispy_forms.layout import Submit, Layout, Fieldset, Field
from .models import CartItem, Vente, Client, Paiement
from .forms import VenteCreateForm, ClientCreateForm, PaiementCreateForm, VenteDeleteForm, VenteUpdateForm, ClientUpdateForm
from inventory.models import Article
from .cartutils import is_cart_id_session_set, _set_or_get_session_id, get_cart_items, get_cart_id_session
from .cartutils import  get_cart_item_of_book, article_already_in_cart, get_cart_counter, _remove_cart_item, cart_not_complete
from .cartutils import remove_cart_id_from_session


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
        else:
            if article.quantite > 0:
                cart_item = CartItem()
                cart_item.cart_id = _set_or_get_session_id(request)
                cart_item.article = article
                cart_item.quantity = 1
                cart_item.save()
                # if cart_items.count() == 0:
                #     # Pourquoi créer une vente maintenant et pas lors de la commande?
                #     vente = Vente.objects.create()
                #     cart_item.vente = vente
                # else:
                #     cart_item.vente = cart_items[0].vente
                # cart_item.save()
            else:
                return HttpResponse("Quantite en stock insuffisante!")
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        print('not a POST?')
        pass

def remove_cart_item(request, pk):
    if request.method == 'POST':
        cart_items = get_cart_items(request)
        vente = cart_items[0].vente
        article = Article.objects.get(pk=pk)
        _remove_cart_item(request, article)
        # If the cart is empty then the Vente is deleted. Because
        # a new instance of "Vente" is created.
        if len(cart_items) == 0:
            vente = Vente.objects.get(pk=vente.pk)
            vente.delete()

        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        raise ValueError('Should not be called with GET')


def remove_article_from_vente_and_update_article_quantity(request, pk):
    """pk is the one of cart_item, its ID."""
    if request.method == 'GET':
        cart_item = CartItem.objects.get(pk=pk)
        vente = cart_item.vente
        article = Article.objects.get(pk=cart_item.article.pk)
        article.quantite += cart_item.quantity
        article.save()
        cart_item.delete()
#        url_redirect = reverse('cart:vente_update', kwargs={'pk':vente.pk})
        return HttpResponseRedirect("/cart/vente_update/%s" % vente.pk)


def edit_price(request, pk):
    if request.method == 'POST':
        cart_item = CartItem.objects.get(pk=pk)
        price = request.POST.get('new_price', '')
        if len(price) == 0:
            # assuming zero
            price = "0"
        cart_item.prix = float(price)
        cart_item.save()
        if cart_item.prix == 0:
            return render(request, 'cart/cart_content.html',
                          {'error_message' : "Le montant de l'article est zéro!",
                           'cart' : get_cart_items(request), 'new_price' : price,
                           })
        cart_item.save()
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        raise ValueError('cart:views:edit_price: should not be called with GET')

# This import must be defined here, after the functions definition and not before,
# otherwise it fails.


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
        # ctx = add_categories_to_context(ctx)
        # ctx = add_cart_counter_to_context(self.request, ctx)
        # ctx = add_total_books(ctx)
        if  is_cart_id_session_set(self.request): # and not cart_not_complete(self.request):
            cart_id = get_cart_id_session(self.request)
            ctx['cart_total'] = CartItem.get_total_of_cart(cart_id)
            #ctx['vente_pk']   = CartItem.get_vente_id(cart_id)
            ctx['cart'] = get_cart_items(self.request)
            carts = get_cart_items(self.request)
            print(carts)
            print('cart')
            return ctx
        else:
            return ctx


class CheckoutView(CreateView):
    """Crée le formulaire de la vente avec la liste des articles mis dans le panier.
    Le montant est pré-renseigné. """
    model = Vente
    template_name = 'cart/checkout.html'
    context_object_name = 'cart'
    form_class = VenteCreateForm

    def get_context_data(self, **kwargs):
        ctx = super(CheckoutView, self).get_context_data(**kwargs)

        if is_cart_id_session_set(self.request):
            cart_id = get_cart_id_session(self.request)
            ctx['cart_total'] = CartItem.get_total_of_cart(cart_id)
            #ctx['vente_pk'] = CartItem.get_vente_id(cart_id)
            ctx['cart'] = get_cart_items(self.request)
            return ctx
        else:
            return ctx

    def get_initial(self):
        initial = super(CheckoutView, self).get_initial()
        session_id = get_cart_id_session(self.request)
        initial['montant'] = CartItem.get_total_of_cart(session_id)
        return  initial

    def form_valid(self, form):
        self.object = form.save()
        montant = form['montant'].value()
        print('self.object: ', self.object)
        if is_cart_id_session_set(self.request):
            cart_id = get_cart_id_session(self.request)
#            montant_paiement = self.object.montant # le formulaire permet d'entrer le 1er paiement (ou final)
            # facture total
            #self.object.montant = CartItem.get_total_of_cart(cart_id)

        #cart_items = CartItem.objects.filter(vente=self.object)
        cart_items = get_cart_items(request=self.request)
        for cart in cart_items:
            print(cart)
            cart.cart_complete = True
            cart.vente = self.object
            cart.save()
            cart.update_article_quantity()
        remove_cart_id_from_session(self.request)
        return super(CheckoutView, self).form_valid(form)




class VenteDetail(DetailView):
    model = Vente
    template_name = 'cart/vente.html'
    context_object_name = 'vente'

class VenteUpdateView(UpdateView):
    model = Vente
    template_name = 'cart/vente_update.html'
    context_object_name = 'vente'
    form_class = VenteUpdateForm


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



class ClientListView(ListView):
    model = Client
    template_name = 'cart/clients.html'
    context_object_name = 'clients'

class ClientDetailView(DetailView):
    model = Client
    template_name = 'cart/client.html'
    context_object_name = 'client'

class ClientCreateView(CreateView):
    model = Client
    template_name = 'cart/client_create.html'
    form_class = ClientCreateForm


class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'cart/client_update.html'
    form_class = ClientUpdateForm


class PaiementListView(ListView):
    model = Paiement
    template_name = 'cart/paiements.html'
    context_object_name = 'paiements'

class PaiementCreateView(CreateView):
    model = Paiement
    template_name = 'cart/paiement_create.html'
    form_class = PaiementCreateForm

def add_paiement(request, vente_pk):
    """Add a paiement to a vente.
    return render(request, 'polls/detail.html', {'question': question})

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    """
    template_name = 'cart/paiement_add.html'
    if request.method == 'POST':
        form = PaiementCreateForm(request.POST)
        montant = float(request.POST.get('montant', ''))
        vente = Vente.objects.get(pk=vente_pk)
        form.helper.layout.append(PrependedText('montant', 'Max: ' + str(vente.solde_paiements())))
        form.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )


        if form.is_valid():
            form.save()
            if vente.solde_paiements() == 0:
                vente.reglement_termine = True
            else:
                vente.reglement_termine = False
            vente.save()
            url_redirect = reverse('cart:vente', args=[vente.pk])
            return HttpResponseRedirect(url_redirect)
        else:
            return render(request=request, template_name=template_name, context={'form': form,
                                                                             'solde': vente.solde_paiements()})
    else:
        # initial data = vente.pk
        vente = Vente.objects.get(pk=vente_pk)
        vente_solde = vente.solde_paiements()

        date_vente = datetime.datetime(year=vente.date.year, month=vente.date.month, day=vente.date.day,
                                       hour=vente.date.hour, minute=vente.date.minute)
        form = PaiementCreateForm(initial={'vente': vente, 'date' : date_vente, 'montant' : vente_solde})
        # add prepended text here
        form.helper.layout.append(PrependedText('montant', 'Max: ' + str(vente_solde)))
        form.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )

        return render(request=request, template_name=template_name, context={'form': form,
                                                                             'solde': vente_solde})



class PaiementDetailView(DetailView):
    model = Paiement
    template_name = 'cart/paiement.html'
    context_object_name = 'paiement'



