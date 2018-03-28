from django.db import models
from django.utils import timezone
from django.shortcuts import reverse
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from inventory.models import Article


class Client(models.Model):
    name = models.CharField(_('Name'), max_length=80)
    first_name = models.CharField(_('First name'), max_length=80)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,20}$',
                                 message="Format: '+999999999'. Maximum 20 chiffres.")
    tel = models.CharField(_('Tél.'), max_length=20, validators=[phone_regex], help_text=_("pas d'espaces entre les chiffres svp"),
                           null=True, blank=True)

    class Meta:
        unique_together = ['name', 'first_name']
        ordering = ['name']

    def __str__(self):
        return self.first_name + ' ' + self.name

    def get_absolute_url(self):
        return reverse('cart:client', kwargs={'pk': self.pk})

class VenteManager(models.Manager):

    def total_sellings(self):
        total = 0
        for v in self.model.objects.all():
            if v.reglement_termine:
                total += v.montant
        return total


class Vente(models.Model):
    """Simplistic. Further adds are:
    - le statut: terminé ou pas
    - un lien sur les avances
    - un lien sur une cliente
    """
    date = models.DateTimeField(default=timezone.now)
    montant = models.DecimalField(_('montant'), max_digits=20, decimal_places=2, default=0)
    client  = models.ForeignKey(Client, null=True, blank=True, verbose_name=_('Client'), help_text=_("Laisser le champ vide (---) si le client n'est pas enregistré."))
    reglement_termine = models.BooleanField(_('Règlement terminé'), default=False)
    objects = VenteManager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        titre = "ID: %s / %s / %s" % (self.pk, self.date, self.montant)
        return titre

    def get_absolute_url(self):
        return reverse('cart:vente', kwargs={'pk': self.pk})

    def total_paiements(self):
        total = 0
        for p in self.paiement_set.all():
            total += p.montant
        return total

    def solde_paiements(self):
        return self.montant - self.total_paiements()



class Paiement(models.Model):
    PAYMENT_MODE = (
        ('C' , 'Cash'),
        ('B' , 'Bank'),
    )

    date    = models.DateTimeField(default=timezone.now)
    montant = models.DecimalField(_('Montant'), max_digits=20, decimal_places=0, default=0)
    vente   = models.ForeignKey(Vente, verbose_name=_('Vente'))
    payment_mode = models.CharField(max_length=1, choices=PAYMENT_MODE, null=True, blank=True)

    def __str__(self):
        return "Montant: %s / Vente-ID: %s" % (self.montant, self.vente.pk)

    def get_absolute_url(self):
        return reverse('cart:paiement', kwargs={'pk': self.pk})


class CartItem(models.Model):
    cart_id    = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity   = models.IntegerField(default=1)
    article    = models.ForeignKey(Article, unique=False)
    prix       = models.DecimalField(_('Prix'), max_digits=20, decimal_places=0, default=25000)
    vente      = models.ForeignKey(Vente, null=True, verbose_name=_('Vente')) # par défaut si une vente est effacée, ses cart_item aussi
    # Si le panier est validé pour une vente, ce dernier est vidé. (session_id effacé)
    # Pour retrouver les éléments il faut utiliser Vente-ID
    cart_complete = models.BooleanField(default=False, verbose_name=_('Panier validé'))

    class Meta:
        db_table = 'cart_items'
        ordering = ['date_added']

    def total(self):
        return self.quantity * self.prix

    def update_article_quantity(self):
        self.article.quantity = self.article.quantity - self.quantity
        self.article.save()

    @property
    def nom(self):
        return self.article.name


    def get_absolute_url(self):
        return self.article.get_absolute_url()


    def augment_quantity(self, quantity):
        # check if this is possible given 1) the stock available and 2) the actual quantity
        if self.quantity < self.article.quantity:
            self.quantity = self.quantity + int(quantity)
            self.save()

    def set_quantity(self, quantity):
        if quantity <= self.article.quantity and quantity > 0:
            self.quantity = quantity
            self.save()
        else:
            #print('quantity exceed stock total.')
            self.quantity = self.article.quantity
            msg = "Warning: quantity set to max stock available."
            #print('quantity set to maximum available stock')
            return msg

    def get_total_of_cart(session_id):
        """
        Select the cart_items for this session_id and sum the total
        of each item.
        :return: the total of cart content
        """
        cart_items = CartItem.objects.filter(cart_id=session_id)
        cart_total_list = [cart_item.total() for cart_item in cart_items]
        return sum(cart_total_list)

    # def get_vente_id(session_id):
    #     cart_items = CartItem.objects.filter(cart_id=session_id)
    #     if cart_items:
    #         return cart_items[0].vente.pk
    #     else:
    #         return None



