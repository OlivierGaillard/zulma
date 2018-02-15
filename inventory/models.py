from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Enterprise(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Employee(models.Model):
    """
    Every user is an employee of one enterprise.

    The articles tables (derived from Product: Accessory, Clothes and Shoe)
     are bound to one enterprise with the help of the foreign key 'Product.product_owner'

    One user may work only with the articles belonging to his/her enterprise.

    The belonging of this user to the enterprise is expressed with the
    foreign key 'Employee.enterprise'.

    Conclusion: the employee has access permission only to the articles of her enterprise.

    Process to create one employee:

    a) create one user
    b) create one enterprise
    c) create one Employee with foreign keys to user and enterprise
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enterprise = models.ForeignKey(Enterprise, related_name="employees")

    def get_enterprise_of_current_user(user):
        """
        A class helper method used by the abstract products.forms.ProductCreateForm.
        :param user: the request.user used to retrieve one Employee instance.
        :return: the Enterprise instance of the Employee instance.
        """
        if Employee.objects.filter(user=user).exists():
            employee = Employee.objects.get(user=user)
            return employee.enterprise

    def is_current_user_employee(user):
        if Employee.objects.filter(user=user).exists():
            employee = Employee.objects.get(user=user)
            return employee.enterprise != None
        else:
            return False


    def __str__(self):
        if self.enterprise is not None:
            return self.user.username + ': ' + str(self.enterprise)
        else:
            return self.user.username


class Arrivage(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    date_arrivee = models.DateField()
    proprietaire = models.ForeignKey(Enterprise, null=True)

    def __str__(self):
        return self.nom


class Frais(models.Model):
    montant = models.DecimalField(max_digits=20, decimal_places=2)
    objet = models.TextField()
    date = models.DateField()
    entreprise = models.ForeignKey(Enterprise, null=True)
    arrivage = models.ForeignKey(Arrivage, null=True)

    def __str__(self):
        return self.objet + ': ' + str(self.montant)

    class Meta:
        verbose_name_plural = 'Frais'

class Category(models.Model):
    name = models.CharField(_('Category'), max_length=100, unique=True)


class Article(models.Model):
    """Base for an article containing the only required fields: photo."""

    solde_choices = (
        ('N', _('-')),
        ('S', _('en solde')),
    )

    photo = models.ImageField(upload_to='articles', null=True, blank=True)
    purchasing_price = models.DecimalField(_('Purchasing price'), max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price    = models.DecimalField(_('Selling price'), max_digits=10, decimal_places=2, null=True, blank=True)
    name  = models.CharField(_('Name'), max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, verbose_name=_('Category'))
    description = models.TextField(_('Description'), null=True, blank=True)
    quantity = models.IntegerField(_('Quantity'), default=1)
    solde = models.CharField(_("en solde"), max_length=1, choices=solde_choices, default='N')

    class Meta:
        verbose_name = _('Article with minimal data')



class Marque(models.Model):
    nom = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


# class ClothesArticle(Article):
#     """Cela ne résout pas le problème. Si les articles de bases sont créés encore faut-il générer les articles
#     spécifiques. Impossible de le faire automatiquement, sauf à prévoir un tri des photos.
#     Une autre solution: indexer les articles de base (fixer une catégorie), puis générer des instances
#     des classes dérivées. """
#     clients_choices = (
#         ('H', _('Homme')),
#         ('F', _('Femme')),
#         ('M', _('Mixte')),
#         ('E', _('Enfant')),
#     )
#     type_client = models.CharField(_("Type de client"), max_length=1, choices=clients_choices, default='F', )
#     marque = models.ForeignKey(Marque, null=True, blank=True)

class ArticleClothes(models.Model):
    clients_choices = (
        ('H', _('Homme')),
        ('F', _('Femme')),
        ('M', _('Mixte')),
        ('E', _('Enfant')),
    )
    genre_choices = (
        ('A', 'Accessoire'),
        ('V', 'Vêtement'),
        ('C', 'Chaussure'),
        ('S', 'Sous-vêtement'),
    )

    tailles_choices = (
        ('1', 'S'),
        ('2', 'M'),
        ('3', 'L'),
        ('4', 'XL'),
        ('5', 'XXL'),
        ('6', 'XXXL'),
        ('7', 'XXXXL'),
        ('8', '5XL'),
        ('9', '6XL'),
        ('10', '7XL'),
        ('11', '8XL'),
    )
    solde_choices = (
        ('N', _('-')),
        ('S', _('en solde')),
    )
    type_taille = (
        ('1', 'EUR'),
        ('2', 'US'),
        ('3', 'UK')
    )
    photo_no = models.PositiveSmallIntegerField(null=True, blank=True, help_text="no de la prise de vue", unique=True)
    type_client = models.CharField(_("Type de client"), max_length=1, choices=clients_choices, default='F', )
    genre_article = models.CharField(_("Genre d'article"), max_length=1, choices=genre_choices, default='S')
    nom = models.CharField(_('Nom'), max_length=100, default="ensemble")
    marque = models.ForeignKey(Marque)
    entreprise = models.ForeignKey(Enterprise, default=2)
    quantite   = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_total    = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    remise     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.0)
    date_ajout = models.DateField(auto_now_add=True)
    arrivage   = models.ForeignKey(Arrivage, null=True, blank=True, default=3, verbose_name=_('Arrivage'))
    couleurs_quantites = models.CharField(max_length=200, null=True, blank=True)
    motifs = models.CharField(max_length=200, null=True, blank=True)
    notes  = models.CharField(max_length=200, null=True, blank=True)
    type_taille = models.CharField(max_length=1, choices=type_taille, default='1', null=True, blank=True)
    taille = models.CharField(max_length=2, choices=tailles_choices, null=True, blank=True)
    taille_nombre = models.PositiveSmallIntegerField(null=True, blank=True)
    local = models.CharField(max_length=20, default='bas')
    solde = models.CharField(_("en solde"), max_length=1, choices=solde_choices, default='N')
    ventes = models.CharField(max_length=200, null=True, blank=True, help_text="25000, 35000")
    tailles_vendues = models.CharField(max_length=200, null=True, blank=True, help_text="(XL, 1), (M, 2)")

    def __str__(self):
        return self.nom + ' ID ' + str(self.pk)

    class Meta:
        ordering = ['pk',]

    def get_absolute_url(self):
        return reverse('inventory:article_detail', kwargs={'pk' : self.pk})



