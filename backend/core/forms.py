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
    pdf_activitat = forms.FileField(
        required=False,
        help_text="PDF explicatiu de l'activitat (màx 2MB)",
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
    )

    class Meta:
        model = Activitat
        fields = ['titol', 'descripcio', 'data', 'hora', 'adreça', 'latitud', 'longitud', 'pdf_activitat']
        widgets = {
            'titol': forms.TextInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;'}),
            'descripcio': forms.Textarea(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'rows': 4}),
            'data': forms.DateInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'type': 'time'}),
            'adreça': forms.TextInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;'}),
            'latitud': forms.NumberInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'step': 'any'}),
            'longitud': forms.NumberInput(attrs={'class': 'wpforms-field-large', 'style': 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px;', 'step': 'any'}),
        }

    def clean_pdf_activitat(self):
        pdf = self.cleaned_data.get('pdf_activitat', False)
        if pdf:
            if pdf.size > 2 * 1024 * 1024:
                raise forms.ValidationError("El PDF no pot pesar més de 2MB.")
            if not pdf.name.endswith('.pdf'):
                raise forms.ValidationError("Només es permeten arxius PDF.")
        return pdf

from django.contrib.auth.models import User

FIELD_STYLE = 'padding:10px; border:1px solid #ccc; width:100%; border-radius:4px; box-sizing:border-box;'

class GestorUserForm(forms.Form):
    username = forms.CharField(
        label="Nom d'usuari",
        max_length=150,
        widget=forms.TextInput(attrs={'style': FIELD_STYLE})
    )
    email = forms.EmailField(
        label="Correu electrònic",
        widget=forms.EmailInput(attrs={'style': FIELD_STYLE})
    )
    first_name = forms.CharField(
        label="Nom",
        max_length=150,
        widget=forms.TextInput(attrs={'style': FIELD_STYLE})
    )
    last_name = forms.CharField(
        label="Cognoms",
        max_length=150,
        widget=forms.TextInput(attrs={'style': FIELD_STYLE})
    )
    password = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput(attrs={'style': FIELD_STYLE})
    )
    password2 = forms.CharField(
        label="Confirma la contrasenya",
        widget=forms.PasswordInput(attrs={'style': FIELD_STYLE})
    )
    is_admin = forms.BooleanField(
        label="És administrador d'una associació (gerent)?",
        required=False,
        widget=forms.CheckboxInput(attrs={'style': 'transform: scale(1.5); margin-left:10px;'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les contrasenyes no coincideixen.")
        return cleaned_data

class GestorAssociacioForm(forms.ModelForm):
    class Meta:
        model = Associacio
        fields = [
            'nom', 'descripcio_curta', 'descripcio',
            'any_fundacio', 'zona_geografica', 'adreça',
            'latitud', 'longitud', 'web', 'correu', 'foto', 'gerent'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'style': FIELD_STYLE}),
            'descripcio_curta': forms.TextInput(attrs={'style': FIELD_STYLE, 'placeholder': 'Màxim 10 paraules'}),
            'descripcio': forms.Textarea(attrs={'style': FIELD_STYLE, 'rows': 4}),
            'any_fundacio': forms.NumberInput(attrs={'style': FIELD_STYLE}),
            'zona_geografica': forms.TextInput(attrs={'style': FIELD_STYLE}),
            'adreça': forms.TextInput(attrs={'style': FIELD_STYLE}),
            'latitud': forms.NumberInput(attrs={'style': FIELD_STYLE, 'step': 'any', 'placeholder': 'Ex: 41.3879'}),
            'longitud': forms.NumberInput(attrs={'style': FIELD_STYLE, 'step': 'any', 'placeholder': 'Ex: 2.1699'}),
            'web': forms.URLInput(attrs={'style': FIELD_STYLE, 'placeholder': 'https://...'}),
            'correu': forms.EmailInput(attrs={'style': FIELD_STYLE}),
            'foto': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'gerent': forms.Select(attrs={'style': FIELD_STYLE}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar el select de gerents per a mostrar només administradors
        self.fields['gerent'].queryset = User.objects.filter(is_staff=True)
        self.fields['gerent'].empty_label = "Selecciona un administrador..."

        # Forcem com a obligatoris els camps que el model declara com a opcionals
        # però que nosaltres exigim sempre en aquest formulari del gestor
        camps_obligatoris = [
            'gerent', 'foto', 'web', 'correu', 'adreça',
            'zona_geografica', 'any_fundacio', 'latitud', 'longitud',
            'descripcio_curta',
        ]
        for camp in camps_obligatoris:
            if camp in self.fields:
                self.fields[camp].required = True
