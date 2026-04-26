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
