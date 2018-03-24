from crispy_forms.helper import FormHelper
from django.core.validators import MinValueValidator
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

class ArticleLossesForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ('losses', 'amount_losses',)

    def __init__(self, *args, **kwargs):
        super(ArticleLossesForm, self).__init__(*args, **kwargs)
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

    def clean(self):
        if self.cleaned_data['losses'] > self.instance.quantity:
            self.add_error('losses', _('Losses (%s) cannot exceed quantity (%s).' % (
                str(self.cleaned_data['losses']),
                str(self.instance.quantity))
            ))
        elif self.cleaned_data['losses'] == 0:
            self.add_error('losses', _('Losses should be greater than zero.'))
        return self.cleaned_data



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





class AddPhotoForm(forms.Form):
    image   = forms.ImageField()
