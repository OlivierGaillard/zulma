from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import TabHolder, Tab, FormActions
from crispy_forms.layout import Submit, Layout, Fieldset, Field
from django import forms
from .models import Costs, Category, Enterprise


class CostsCreateForm(forms.ModelForm):
    class Meta:
        model = Costs
        fields = ('branch', 'name', 'amount', 'category', 'note', 'enterprise', 'billing_date', 'billing_number' )
        widgets = {
            'billing_date': forms.DateInput(
                attrs={'id': 'datetimepicker_es'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(CostsCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )

class CostsUpdateForm(forms.ModelForm):
    class Meta:
        model = Costs
        fields = ('branch', 'name', 'amount', 'category', 'note', 'enterprise', 'billing_date', 'billing_number' )
        widgets = {
            'billing_date': forms.DateInput(
                attrs={'id': 'datetimepicker_es'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(CostsUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )



class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(CategoryCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )

class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(CategoryUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )



class EnterpriseCreateForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(EnterpriseCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )


class EnterpriseUpdateForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(EnterpriseUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )
