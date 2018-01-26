from django.contrib import admin
from .models import Frais, Enterprise, Employee, Arrivage, Article, Marque, Photo

class FraisAdmin(admin.ModelAdmin):
    list_display = ['date', 'montant', 'objet', 'entreprise']

admin.site.register(Frais, FraisAdmin)

class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
admin.site.register(Enterprise, EnterpriseAdmin)

admin.site.register(Employee)
class ArrivageAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom', 'proprietaire']
admin.site.register(Arrivage, ArrivageAdmin)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'entreprise', 'type_client', 'nom', 'marque', 'local', 'quantite', 'type_taille', 'taille', 'taille_nombre', 'solde',
                    'couleurs_quantites', 'motifs', 'photo_no', 'notes', 'ventes', 'tailles_vendues']

admin.site.register(Article, ArticleAdmin)
#admin.site.register(Photo)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom']
admin.site.register(Marque, MarqueAdmin)

class PhotoAdmin(admin.ModelAdmin):
    list_display = ['article', 'article_ID']
admin.site.register(Photo, PhotoAdmin)

