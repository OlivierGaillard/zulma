from django import forms
from datetime import date

class DateForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={ 'type' : 'date' }))
    end_date =   forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))

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

