from django.db import models
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from inventory.models import Article, Branch
from cart.models import Vente
from dashboard.utils import TimeSliceHelper
from datetime import date

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

    def total_costs(self, year=None, branch=None, start_date = None, end_date=None):
        helper = TimeSliceHelper(self.model)
        costs = helper.get_objects(year=year, branch=branch, start_date=start_date, end_date=end_date)
        total = sum(c.amount for c in costs)
        return total

    def grand_total(self, branch=None, year=None, start_date = None, end_date=None):
        """Sum of costs + sum of Articles' purchasing price."""
        helper = TimeSliceHelper(Article)
        articles = helper.get_objects(year=year, branch=branch, start_date=start_date, end_date=end_date)
        purchasing_price = sum(a.purchasing_price for a in articles)
        return purchasing_price + self.total_costs(branch=branch, year=year, start_date=start_date, end_date=end_date)

    def get_balance(self, branch=None, year=None, start_date = None, end_date=None):
        """
        Ventes minus (purchases + costs)
        Purchases are taken from Article.objects.total_purchasing_price method.
        :return: Ventes - (purchases + costs)
        """
        return Vente.objects.total_sellings(branch=branch, year=year, start_date = start_date, end_date=end_date) - \
               self.grand_total(branch=branch, year=year, start_date = start_date, end_date=end_date)



class Costs(models.Model):
    branch = models.ForeignKey(Branch, null=True, blank=True)
    creation_date = models.DateField(_('Creation date'), default=date.today)
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




