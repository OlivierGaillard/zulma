from django.db import models
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from inventory.models import Article, Branch
from cart.models import Vente

# Create your models here.

class Enterprise(models.Model):
    """Or a better name could be 'Provider'."""
    name = models.CharField(_('name'), max_length=80, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        reverse('costs:enterprise_details', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['name']


class Category(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)

    def get_absolute_url(self):
        reverse('costs:category_details', kwargs={'pk': self.pk})


    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _('Categories')
        ordering = ['name']


class CostsManager(models.Manager):

    def total_costs(self, branch=None):
        total = 0
        costs = None
        if branch:
            costs = self.model.objects.all().filter(branch=branch)
        else:
            costs = self.model.objects.all()
        for c in costs:
            total += c.amount
        return total

    def grand_total(self, branch=None):
        """Sum of costs + sum of Articles' purchasing price."""
        purchasing_price = Article.objects.total_purchasing_price(branch=branch)
        return purchasing_price + self.total_costs(branch)

    def get_balance(self, branch=None):
        """
        Ventes - - (purchases + costs)
        Purchases are taken from Article.objects.total_purchasing_price method.
        :return: Ventes - (purchases + costs)
        """
        return Vente.objects.total_sellings(branch=branch) - self.grand_total(branch=branch)



class Costs(models.Model):
    branch = models.ForeignKey(Branch, null=True, blank=True)
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    category = models.ForeignKey(Category)
    amount = models.DecimalField(_('Amount'), max_digits=20, decimal_places=2)
    name   = models.CharField(_('Name'), max_length=200, help_text=_('short description'), blank=True, null=True)
    note   = models.TextField(_('Note'), blank=True, null=True)
    enterprise = models.ForeignKey(Enterprise, blank=True, null=True)
    billing_date = models.DateField(blank=True, null=True, help_text=_('when the bill was created'))
    billing_number = models.CharField(blank=True, null=True, max_length=200, help_text=_('the bill reference number'))
    article_link = models.URLField(_('Article link'), null=True, blank=True)
    article_id   = models.ForeignKey(Article, null=True, on_delete=models.SET_NULL)
    objects = CostsManager()

    def __str__(self):
        return "Amount: %s / Category: %s / Date: %s " % (self.amount, self.category, self.creation_date)

    class Meta:
        verbose_name_plural = _('Costs')
        ordering = ['-billing_date']

    def delete(self):
        if self.article_id:
            article = Article.objects.get(pk=self.article_id.pk)
            if self.amount > 0:
                article.losses -= 1
                article.amount_losses -= self.amount
                article.quantity += 1
                article.save()
        super(Costs, self).delete()




