from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from .models import Article, Arrivage, Branch
from .models import Category as ArticleCategory
from .forms import ArticleUpdateForm
from .views import get_extension, get_extension_error, image_extension_fails
from costs.models import Costs, Category


#from .views import ArticleDeleteView

class TestInventoryViews(TestCase):

    def setUp(self):
        self.arrival = Arrivage.objects.create(nom="test", date_arrivee=date.today())
        self.a1 = Article.objects.create(name='a1', quantity=10, photo='a1', arrival=self.arrival)
        self.a2 = Article.objects.create(name='a2', quantity=5, photo='a2', arrival=self.arrival)
        self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_delete_view(self):
        self.assertEqual(2, Article.objects.count())
        c = Client()
        response = c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.post(reverse('inventory:article_delete', args=[self.a1.pk]), {'delete_purchasing_costs' : False}, follow=False)
        c.logout()
        self.assertEqual(1, Article.objects.count())

    def test_articles_list_filter(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.get('/inventory/articles/', {'name__icontains' : 'a1'})
        response_str = response.content.decode()
        self.assertInHTML('a1', response_str, count=1)

    def test_add_loss_quantity_one(self):
        self.assertEqual(0, self.a1.losses)
        self.assertEqual(10, self.a1.quantity)
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses' : 1, 'amount_losses' : 20}
        response = c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        self.assertEqual(200, response.status_code)
        c.logout()
        a1_upated = Article.objects.get(pk=self.a1.pk)
        self.assertEqual(9, a1_upated.quantity)
        self.assertEqual(1, a1_upated.losses)
        self.assertEqual(20, a1_upated.amount_losses)
        self.assertTrue(Costs.objects.count() == 1)
        self.assertEqual(Costs.objects.total_costs(), 20)

    def test_add_loss_quantity_two(self):
        self.assertEqual(0, self.a1.losses)
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses' : 2, 'amount_losses' : 40}
        c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        c.logout()
        a1_upated = Article.objects.get(pk=self.a1.pk)
        self.assertEqual(8, a1_upated.quantity)
        self.assertEqual(2, a1_upated.losses)
        self.assertEqual(40, a1_upated.amount_losses)
        self.assertTrue(Costs.objects.count() == 1)
        self.assertEqual(Costs.objects.total_costs(), 40)

    def test_add_two_losses_and_check_total_costs(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses': 2, 'amount_losses': 40}
        c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        data = {'losses': 1, 'amount_losses': 20}
        c.post(reverse('inventory:article_losses', args=[self.a2.pk]), data=data, follow=True)
        c.logout()
        self.assertEqual(60, Costs.objects.total_costs())


    def test_add_two_losses_for_same_article_and_check_article_update(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses': 1, 'amount_losses': 20.50}
        c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        data = {'losses': 1, 'amount_losses': 20.50}
        c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        article = Article.objects.get(pk=self.a1.pk)
        self.assertEqual(41.0, article.amount_losses)
        self.assertEqual(2, article.losses)
        self.assertEqual(41, Costs.objects.total_costs())



    def test_add_one_cost_then_two_losses_and_check_total_costs(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        c1 = Category.objects.create(name='canalisations')
        data = {'amount': 2000, 'name': 'fosse septique', 'category': c1.pk}
        c.post(reverse('costs:costs_create'), data=data, follow=True)
        data = {'losses': 2, 'amount_losses': 40}
        c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        data = {'losses': 1, 'amount_losses': 20}
        c.post(reverse('inventory:article_losses', args=[self.a2.pk]), data=data, follow=True)
        c.logout()
        self.assertEqual(2060, Costs.objects.total_costs())



    def test_error_msg_when_losses_greater_than_stock_quantity(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses': 12, 'amount_losses': 20} # article a1 quantity = 10
        response = c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        msg = "Losses (12) cannot exceed quantity (10)."
        self.assertInHTML(msg, response.content.decode())

    def test_losses_form_display_previous_losses_info(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        response = c.get(reverse('inventory:article_losses', args=[self.a1.pk]))
        self.assertInHTML('Previous losses:', response.content.decode())

    def test_delete_loss_update_article_loss_fields(self):
        self.assertEqual(0, self.a1.losses)
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses': 1, 'amount_losses': 20}
        c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        a1_updated = Article.objects.get(pk=self.a1.pk)
        self.assertEqual(9, a1_updated.quantity)
        self.assertEqual(1, a1_updated.losses)
        self.assertEqual(20, a1_updated.amount_losses)
        self.assertEqual(1, Costs.objects.count())
        self.assertEqual(20, Costs.objects.total_costs())
        # Now deleting this cost of category 'Losses'

        cost = Costs.objects.all()[0]
        c.post(reverse('costs:costs_delete', args=[cost.pk]))
        self.assertEqual(0, Costs.objects.total_costs())
        a1_updated = Article.objects.get(pk=self.a1.pk)
        self.assertIsNotNone(a1_updated)
        self.assertEqual(a1_updated.losses, 0)
        # update stock available too
        self.assertEqual(10, a1_updated.quantity)
        self.assertEqual(0, a1_updated.amount_losses)


    def test_delete_article_does_NOT_imply_delete_losses_too(self):
        """The Costs model has a foreign key with on_delete SET_TO_NULL.
        Deleting the article will generate a new cost if the purchasing
        price must be saved.
        """
        self.assertEqual(2, Article.objects.count())
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses': 1, 'amount_losses': 20}
        c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data=data, follow=True)
        self.assertEqual(1, Costs.objects.count())
        # Deleting article with costs
        c.post(reverse('inventory:article_delete', args=[self.a1.pk]), {'delete_purchasing_costs' : True}, follow=False)
        c.logout()
        self.assertEqual(1, Costs.objects.count())


    def test_add_oneLoss_on_article_where_stock_is_zero(self):
        a = Article.objects.create(name='zero', quantity=0, photo='zero')
        self.assertEqual(a.quantity, 0)
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses': 1, 'amount_losses': 0}
        c.post(reverse('inventory:article_losses', args=[a.pk]), data=data, follow=True)
        a_updated = Article.objects.get(pk=a.pk)
        self.assertEqual(0, a_updated.quantity)


    def test_add_zero_loss_should_not_generate_one_cost(self):
        a = Article.objects.create(name='one', quantity=1, photo='zero')
        self.assertEqual(a.quantity, 1)
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        data = {'losses': 0, 'amount_losses': 0}
        c.post(reverse('inventory:article_losses', args=[a.pk]), data=data, follow=True)
        a_updated = Article.objects.get(pk=a.pk)
        self.assertEqual(1, a_updated.quantity)
        self.assertEqual(0, Costs.objects.count())


    def test_that_updating_article_does_not_touch_losses(self):
        c = Client()
        c.post('/login/', {'username' : 'golivier', 'password' : 'mikacherie'})
        self.assertEqual(self.a1.quantity, 10)
        c.post(reverse('inventory:article_losses', args=[self.a1.pk]), data={'losses' : 3,
                                                                       'amount_losses' : 30},
               follow=True)
        a_updated = Article.objects.get(pk=self.a1.pk)
        self.assertEqual(3, a_updated.losses)
        self.assertEqual(7, a_updated.quantity)
        new_data = {'name' : 'a1prime', 'solde' : 'N', 'initial_quantity' : 1, 'quantity' : a_updated.quantity,
                    'arrival' : self.arrival.pk}
        form = ArticleUpdateForm(instance=a_updated, data=new_data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        c.post(reverse('inventory:article_update', args=[self.a1.pk]), data=new_data, follow=True)
        a_updated = Article.objects.get(pk=self.a1.pk)
        self.assertEqual('a1prime', a_updated.name)
        # Now the crucial test
        self.assertEqual(3, a_updated.losses)


    def test_grand_total_costs(self):
        """The grand total is the sum of all costs and the total of purchasing prices."""
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        a1 = Article.objects.create(name='a1', quantity=3, photo='a1a', purchasing_price=10)
        Article.objects.create(name='a2', quantity=1, photo='a2a', purchasing_price=10.5)
        data = {'losses': 3, 'amount_losses': 10.5}
        c.post(reverse('inventory:article_losses', args=[a1.pk]), data=data)
        self.assertEqual(31.0, Costs.objects.grand_total())

    def test_balance(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        a1 = Article.objects.create(name='a1', quantity=3, photo='a1a', purchasing_price=10)
        Article.objects.create(name='a2', quantity=1, photo='a2a', purchasing_price=10.5)
        data = {'losses': 3, 'amount_losses': 10.5}
        c.post(reverse('inventory:article_losses', args=[a1.pk]), data=data)

    def test_branch_list_view(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        r = c.get(reverse('inventory:branches'))
        self.assertEqual(200, r.status_code)

    def test_create_branch(self):
        c = Client()
        c.post('/login/', {'username' : 'golivier', 'password' : 'mikacherie'})
        data = {'name' : 'Boutique'}
        r = c.post(reverse('inventory:branch_create'), data=data, follow=True)
        self.assertEqual(200, r.status_code)
        self.assertEqual(1, Branch.objects.count())
        self.assertInHTML('Boutique', r.content.decode())

    def test_delete_branch(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        b = Branch.objects.create(name='Boutique')
        c.post(reverse('inventory:branch_delete', args=[b.pk]), follow=True)
        self.assertEqual(0, Branch.objects.count())

    def test_edit_branch(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        b = Branch.objects.create(name='Boutique')
        data = {'name' : 'Chance'}
        r = c.post(reverse('inventory:branch_update', args=[b.pk]), data=data, follow=True)
        b2 = Branch.objects.get(pk=b.pk)
        self.assertEqual('Chance', b2.name)
        self.assertInHTML('Chance', r.content.decode())

    def test_get_extension(self):
        img_path = "/temp/truc/pic.jpg"
        self.assertEqual('.JPG', get_extension(img_path))
        img_path = "/temp/truc/pic.JPG"
        self.assertEqual('.JPG', get_extension(img_path))

    def test_get_extension_error(self):
        img_path = "/temp/truc/pic2.jpg"
        msg = "Image extension is not .JPG (.jpg) or .JPEG (.jpeg): [{0}".format(img_path)
        self.assertEqual(msg, get_extension_error(img_path))

    def test_img_extension_fail(self):
        img_path = "/temp/truc/pic2.png"
        self.assertTrue((image_extension_fails(img_path), img_path))

    def test_img_extension_valid(self):
        self.assertFalse(image_extension_fails("/temp/truc/pic2.jpg"), "/temp/truc/pic2.jpg" )
        self.assertFalse(image_extension_fails("/temp/truc/pic2.jpeg"))
        self.assertFalse(image_extension_fails("/temp/truc/pic2.JPG"))
        self.assertFalse(image_extension_fails("/temp/truc/pic2.JPEG"))
        self.assertFalse(image_extension_fails("pic2.jpg"))
        self.assertFalse(image_extension_fails("pic2.jpeg"))
        self.assertTrue(image_extension_fails("/temp/turc.png"), "turc.png")

    def test_arrival_delete(self):
        arr = Arrivage.objects.create(nom='Torture', date_arrivee=date.today())
        self.assertIsNotNone(arr)
        self.assertEqual(Arrivage.objects.count(), 2)
        c = Client()
        c.post('/login/', {'username' : 'golivier', 'password' : 'mikacherie'})
        c.post(reverse('inventory:arrival_delete', args=[arr.pk]))
        self.assertEqual(1, Arrivage.objects.count())

    def test_article_delete_without_deleting_PurchasingPrice(self):
        bra = Branch.objects.create(name='Boutique')
        cat = ArticleCategory.objects.create(name='Chaussures')
        arr = Arrivage.objects.create(nom="testd", date_arrivee=date.today())
        art = Article.objects.create(name='a11234', quantity=10, photo='a1asdf', arrival=arr, category=cat, branch=bra)
        self.assertEqual(Costs.objects.count(), 0)
        c = Client()
        c.post('/login/', {'username' : 'golivier', 'password' : 'mikacherie'})
        data = {'delete_purchasing_costs' : 'False'}
        c.post(reverse('inventory:article_delete', args=[art.pk]), data)
        self.assertEqual(Costs.objects.count(), 1)

    def test_article_delete_without_deleting_PurchasingPrice_noBranch(self):
        cat = ArticleCategory.objects.create(name='Chaussures')
        arr = Arrivage.objects.create(nom="testd", date_arrivee=date.today())
        art = Article.objects.create(name='a11234', quantity=10, photo='a1asdf', arrival=arr, category=cat)
        self.assertEqual(Costs.objects.count(), 0)
        c = Client()
        c.post('/login/', {'username' : 'golivier', 'password' : 'mikacherie'})
        data = {'delete_purchasing_costs' : 'False'}
        c.post(reverse('inventory:article_delete', args=[art.pk]), data)
        self.assertEqual(Costs.objects.count(), 1)

    def test_get_articles_by_pictures(self):
        c = Client()
        c.post('/login/', {'username': 'golivier', 'password': 'mikacherie'})
        r = c.get(reverse('inventory:articles_by_pictures'))
        self.assertEqual(200, r.status_code)
