from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .models import Article
#from .views import ArticleDeleteView
class TestInventoryViews(TestCase):

    def setUp(self):
        self.a1 = Article.objects.create(name='a1', quantity=10)
        #self.user_oga = User.objects.create_user(username='golivier', password='mikacherie')

    def test_article_date_added(self):
        d = self.a1.date_added
        self.assertIsNotNone(d)

    def test_article_initial_quantity(self):
        self.assertEqual(self.a1.initial_quantity, 1)

    def test_get_losses(self):
        self.assertEqual(0, self.a1.losses)
        self.a1.losses = 1
        self.a1.save()
        self.assertEqual(1, self.a1.losses)

    def test_quantity_updated_after_losses_was_set(self):
        """Goal: not updating the quantity if the previous losses was already
        set. But how to know it?  Within the form there will be a read-only field
        'losses'? """
        self.assertEqual(0, self.a1.losses)
        self.a1.losses = 1
        self.a1.clean() # to call the validation and trigger the update as would form.is_valid()
        # which triggers: Model.clean_fields(), Model.clean() and Model.validate_unique().
        # See: https://docs.djangoproject.com/fr/2.0/ref/models/instances/#validating-objects
        self.a1.quantity = self.a1.quantity - self.a1.losses # should be achieved by the view or the form.
        self.a1.save()
        self.assertEqual(9, self.a1.quantity)
        self.a1.name = 'Ballon'
        self.a1.clean()
        self.a1.save()
        self.assertEqual(9, self.a1.quantity)










