from django.db import models
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Enterprise(models.Model):
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


class Costs(models.Model):
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    category = models.ForeignKey(Category)
    amount = models.DecimalField(_('Amount'), max_digits=20, decimal_places=2)
    name   = models.CharField(_('Name'), max_length=200, help_text=_('short description'), blank=True, null=True)
    note   = models.TextField(_('Note'), blank=True, null=True)
    enterprise = models.ForeignKey(Enterprise, blank=True, null=True)
    billing_date = models.DateField(blank=True, null=True, help_text=_('when the bill was created'))
    billing_number = models.CharField(blank=True, null=True, max_length=200, help_text=_('the bill reference number'))

    def __str__(self):
        return "Amount: %s / Category: %s / Date: %s " % (self.amount, self.category, self.creation_date)

    class Meta:
        verbose_name_plural = _('Costs')

