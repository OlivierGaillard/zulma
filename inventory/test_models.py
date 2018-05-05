from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article, Branch, Arrivage, Losses
from datetime import date, timedelta
from django.utils import timezone
#from .views import ArticleDeleteView
class TestInventoryViews(TestCase):

    def setUp(self):
        dnow = timezone.localdate().today()
        self.arrival = Arrivage.objects.create(nom="arrivage de test", date_arrivee=dnow)
        #self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_article_date_added(self):
        a1 = Article.objects.create(name='a1', quantity=10, purchasing_price=20, photo='a1')
        d = a1.date_added
        self.assertIsNotNone(d)


    def test_article_initial_quantity(self):
        a1 = Article.objects.create(name='a1', quantity=10, purchasing_price=20, photo='a1')
        self.assertEqual(a1.initial_quantity, 1)

    def test_get_losses(self):
        a1 = Article.objects.create(name='a1', quantity=10, purchasing_price=20, photo='a1')
        self.assertEqual(0, a1.losses)
        Losses.objects.create(article=a1, losses=1, amount_losses=20.50)
        a1.save()
        self.assertEqual(1, a1.losses)

    def test_quantity_updated_after_losses_was_set(self):
        """Goal: not updating the quantity if the previous losses was already
        set. But how to know it?  Within the form there will be a read-only field
        'losses'? """
        a1 = Article.objects.create(name='a1', quantity=10, purchasing_price=20, photo='a1')
        self.assertEqual(0, a1.losses)
        Losses.objects.create(article=a1, losses=1, amount_losses=20.50)
        a1.clean() # to call the validation and trigger the update as would form.is_valid()
        # which triggers: Model.clean_fields(), Model.clean() and Model.validate_unique().
        # See: https://docs.djangoproject.com/fr/2.0/ref/models/instances/#validating-objects
        a1.quantity = a1.quantity - a1.losses # should be achieved by the view or the form.
        a1.save()
        self.assertEqual(9, a1.quantity)
        a1.name = 'Ballon'
        a1.clean()
        a1.save()
        self.assertEqual(9, a1.quantity)

    def test_create_two_articles_with_same_name_but_two_branches(self):
        # test uniqueness too? One article could have the same name if it belongs to different branches.
        # todo: validate this business case with client

        boutique = Branch.objects.create(name="Boutique")
        atelier  = Branch.objects.create(name="Atelier")
        a1 = Article.objects.create(branch=atelier, name='aa1', quantity=10, purchasing_price=20, photo='aa')
        a2 = Article.objects.create(branch=boutique, name='aa1', quantity=10, purchasing_price=20, photo='aaa' )
        self.assertIsNotNone(a2)

    def test_delete_arrival_or_branch_does_not_delete_its_articles(self):
        arr = Arrivage.objects.create(nom='test', date_arrivee=date.today())
        atelier = Branch.objects.create(name="Atelier")
        a1 = Article.objects.create(branch=atelier, name='aa1', quantity=10, purchasing_price=20, photo='aaaa',
                                    arrival=arr)
        self.assertEqual(1, Article.objects.count())
        arr.delete()
        atelier.delete()
        self.assertEqual(1, Article.objects.count())

    def test_purchasing_price_branch_None(self):
        # without branch
        a3 = Article.objects.create(name='a3', quantity=1, photo='a3', arrival=self.arrival, purchasing_price=600)
        # Article without branch
        self.assertEqual(600.00, Article.objects.total_purchasing_price())

    def test_purchasing_price_per_branch(self):
        b1 = Branch.objects.create(name='B1')
        b2 = Branch.objects.create(name='B2')
        a1b1 = Article.objects.create(name='a1b1', quantity=1, photo='a1b1', arrival=self.arrival, purchasing_price=200,
                                      branch=b1)
        a2b1 = Article.objects.create(name='a2b1', quantity=1, photo='a2b1', arrival=self.arrival, purchasing_price=200,
                                      branch=b1)
        a1b2 = Article.objects.create(name='a1b2', quantity=1, photo='a1b2', arrival=self.arrival, purchasing_price=400,
                                      branch=b2)
        # without branch
        a3 = Article.objects.create(name='a3', quantity=1, photo='a3', arrival=self.arrival, purchasing_price=600)
        # Article without branch
        self.assertEqual(1400.00, Article.objects.total_purchasing_price())
        self.assertEqual(400.00, Article.objects.total_purchasing_price(branch=b1))
        self.assertEqual(400.00, Article.objects.total_purchasing_price(branch=b2))

    def test_purchasing_price_of_year(self):
        last_year = date.today() - timedelta(days=365)
        Article.objects.create(name='alast', photo='alast', arrival=self.arrival, purchasing_price=200,
                               date_added=last_year)
        self.assertEqual(200, Article.objects.total_purchasing_price(year=last_year.year))
        # Testing purchases of current year
        self.assertEqual(0, Article.objects.total_purchasing_price(year=date.today().year))
        # Testing all purchases
        self.assertEqual(200, Article.objects.total_purchasing_price())

    def test_purchasing_price_of__year_with_branch(self):
        last_year = date.today() - timedelta(days=365)
        b1 = Branch.objects.create(name='B1')

        Article.objects.create(name='alast', photo='alast', arrival=self.arrival, purchasing_price=200,
                               date_added=last_year, branch=b1)
        self.assertEqual(200, Article.objects.total_purchasing_price(year=last_year.year, branch=b1))
        self.assertEqual(200, Article.objects.total_purchasing_price(year=last_year.year))
        # testing zero if looking for last year with another branch name.
        b2 = Branch.objects.create(name='B2')
        self.assertEqual(0, Article.objects.total_purchasing_price(year=last_year.year, branch=b2))

    def test_purchasing_price_from_to_date(self):
        d1mars  = date(year=2018, month=3, day=1)
        d31mars = date(year=2018, month=3, day=31)
        b1 = Branch.objects.create(name='B1')
        dfevrier = d1mars - timedelta(days=20)
        d3mars = d1mars + timedelta(days=2)
        # Out of range: in february
        Article.objects.create(name='alast', photo='alast', arrival=self.arrival, purchasing_price=200,
                               date_added=dfevrier, branch=b1)
        self.assertEqual(200, Article.objects.total_purchasing_price(start_date=dfevrier))

        self.assertEqual(0, Article.objects.total_purchasing_price(start_date=d1mars))
        # In mars (1)
        Article.objects.create(name='alast1', photo='alast1', arrival=self.arrival, purchasing_price=200,
                       date_added=d1mars, branch=b1)
        self.assertEqual(200, Article.objects.total_purchasing_price(start_date=d1mars))
        # In mars (2)
        Article.objects.create(name='alast2', photo='alast2', arrival=self.arrival, purchasing_price=200,
                       date_added=d3mars, branch=b1)

        self.assertEqual(400, Article.objects.total_purchasing_price(start_date=d1mars))
        Article.objects.create(name='alast3', photo='alast3', arrival=self.arrival, purchasing_price=200,
                       date_added=d31mars, branch=b1)

        # test range 1-31 mars   range 1- 3 mars
        self.assertEqual(200, Article.objects.total_purchasing_price(start_date=date(year=2018, month=2, day=1),
                                                                     end_date=d1mars-timedelta(days=1)))

        self.assertEqual(600, Article.objects.total_purchasing_price(start_date=d1mars, end_date=d31mars))














