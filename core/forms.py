from django import forms
from .models import Associacio, Activitat

class AssociacioForm(forms.ModelForm):
    class Meta:
        model = Associacio
        fields = ['nom', 'descripcio', 'any_fundacio', 'zona_geografica', 'latitud', 'longitud']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;'}),
            'descripcio': forms.Textarea(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'rows': 5}),
            'any_fundacio': forms.NumberInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;'}),
            'zona_geografica': forms.TextInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;'}),
            'latitud': forms.NumberInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'step': 'any'}),
            'longitud': forms.NumberInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'step': 'any'}),
        }

class ActivitatForm(forms.ModelForm):
    class Meta:
        model = Activitat
        fields = ['titol', 'descripcio', 'data', 'hora', 'adreça', 'latitud', 'longitud']
        widgets = {
            'titol': forms.TextInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;'}),
            'descripcio': forms.Textarea(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'rows': 4}),
            'data': forms.DateInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'type': 'time'}),
            'adreça': forms.TextInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;'}),
            'latitud': forms.NumberInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'step': 'any'}),
            'longitud': forms.NumberInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'step': 'any'}),
        }
