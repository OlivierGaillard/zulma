from crispy_forms.helper import FormHelper
from django.utils.translation import ugettext_lazy as _
from crispy_forms.bootstrap import TabHolder, Tab, FormActions
from crispy_forms.layout import Submit, Layout, Fieldset, Field, HTML
from django import forms
from django.conf import settings
import os
from .models import Article, Arrivage, Category

class CategoryFormCreate(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(CategoryFormCreate, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )

class CategoryFormUpdate(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(CategoryFormUpdate, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )


class CategoryFormDelete(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(CategoryFormDelete, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )


class UploadPicturesZipForm(forms.Form):
    pictures_zip = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(UploadPicturesZipForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'

        pictures_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        li = os.listdir(pictures_dir)
        if len(li) > 0:
            self.helper.layout = Layout(
                HTML("<div class='alert alert-warning'>They are already uploaded pictures. Please generate the articles before uploading new ones.</div>")
            )
        else:
            self.helper.layout.append(
                FormActions(
                    Submit('save', 'Upload'),
                )
            )


    def clean(self):
        cleaned_data = super(UploadPicturesZipForm, self).clean()
        zip_file = cleaned_data['pictures_zip']
        if not zip_file.name.split('.')[1] == 'zip':
            self.add_error('pictures_zip', _("File ends not with extension '.zip'."))
        # print('clean zip file:', zip_file)
        # print('clean', zip_file.temporary_file_path())
        # print('clean', zip_file.name)
        # print('clean', zip_file.size)
        # if zip_file.multiple_chunks():
        #     print('multiple chunks required.')
        # else:
        #     print('no multiple chunks required')
        return cleaned_data



class HandlePicturesForm(forms.Form):

    arrival  = forms.ModelChoiceField(label=_('Arrival'), queryset=Arrivage.objects.all())
    category = forms.ModelChoiceField(label=_('Category'), required=False, queryset=Category.objects.all())

    def __init__(self, *args, **kwargs):
        super(HandlePicturesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Generate'),
            )
        )


class ArticleUpdateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('name', 'category', 'purchasing_price', 'selling_price', 'solde', 'initial_quantity', 'quantity', 'notes', 'description', 'arrival')

    def __init__(self, *args, **kwargs):
        super(ArticleUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )

class ArrivalUpdateForm(forms.ModelForm):
    class Meta:
        model = Arrivage
        fields = ('nom', _('date_arrivee'))
        widgets = {
            'date_arrivee': forms.DateInput(format='%Y-%m-%d',
                attrs={'id': 'datetimepicker_arrival'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ArrivalUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )


class ArrivalCreateForm(forms.ModelForm):
    class Meta:
        model = Arrivage
        fields = ('nom', _('date_arrivee'))
        widgets = {
            'date_arrivee': forms.DateInput(format=settings.DATE_INPUT_FORMATS,
                                            attrs={'id': 'datetimepicker_arrival'}
                                            ),
        }

    def __init__(self, *args, **kwargs):
        super(ArrivalCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )




                # class ArticleCreateForm(forms.ModelForm):
#     #quantite = forms.IntegerField(min_value=1, required=True, label="Quantité", initial=0,
#     #                              help_text="Quantité en stock (peut différer de la quantité achetée)")
#     new_marque = forms.CharField(max_length=100, required=False, help_text='Pour entrer une nouvelle marque')
#
#     class Meta:
#         model = Article
#         fields = ('type_client', 'genre_article', 'nom', 'marque', 'quantite', 'prix_unitaire', 'prix_total',
#                   'arrivage', 'entreprise')
#
#         widgets = {
#             'type_client': forms.RadioSelect,
#         }
#
#
#     def __init__(self, *args, **kwargs):
#         super(ArticleCreateForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper(self)
#         self.helper.form_method = "POST"
#         self.helper.form_action = reverse('inventory:article_create')
#         self.helper.form_class = 'form-horizontal'
#         self.helper.label_class = 'col-lg-2'
#         self.helper.field_class = 'col-lg-4'
#         self.helper.layout = Layout(
#             TabHolder(
#                 Tab('Fiche article',
#                     'nom', 'arrivage', 'entreprise',
#                     'quantite', 'prix_unitaire', 'prix_total',),
#
#                 Tab('Classification',
#                     'type_client', 'marque', 'new_marque',
#                     ),
#             ),
#             #Submit('submit', u'Submit', css_class='btn btn-success'),
#         )
#         self.helper.layout.append(
#             FormActions(
#                 Submit('save', 'Submit'),
#             )
#         )
#
#        self.helper.add_input(Submit('Submit', 'submit'))

        # if self.user:
        #     user_enterprise = Employee.get_enterprise_of_current_user(self.user)
        #     self.fields['arrivage'].queryset = Arrivage.objects.filter(enterprise=user_enterprise)
        #     self.fields['product_owner'].queryset = Enterprise.objects.filter(pk=user_enterprise.pk)

    # def clean(self):
    #     cleaned_data = super(ArticleCreateForm, self).clean()
    #     print("in clean")
    #     # marque_ref = cleaned_data.get('marque_ref', '')
    #     # if marque_ref is None:
    #     #     marque = cleaned_data.get('marque', '')
    #     #     if len(marque) == 0:
    #     #         msg = "Vous devez choisir une marque ou en créer une en renseignant le champ 'marque'. "
    #     #         raise forms.ValidationError(msg)
    #     return cleaned_data
    #
class AddPhotoForm(forms.Form):
    image   = forms.ImageField()
