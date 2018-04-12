from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import TabHolder, Tab, FormActions
from crispy_forms.layout import Submit, Layout, Fieldset, Field
from datetime import date

class DateForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={ 'type' : 'date' }))
    end_date =   forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super(DateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "GET"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Submit'),
            )
        )


    def clean(self):
        cleaned_data = super().clean()
        d1 = cleaned_data.get('start_date')
        d2 = cleaned_data.get('end_date')
        if d1 and d2:
            if d1 > d2:
                raise forms.ValidationError("start and end dates order mismatch")
        if not d1 and not d2:
            raise forms.ValidationError('At least one date is required')
        return cleaned_data

