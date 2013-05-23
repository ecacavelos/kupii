from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from principal.models import Propietario

# Create the form class.
class PropietarioForm(ModelForm):
    required_css_class = 'required'
    fecha_nacimiento = forms.DateField(input_formats=('%Y-%m-%d', '%d/%m/%Y',))
    class Meta:
        model = Propietario

class SearchForm(Form):
    buscar = forms.CharField(max_length=100)
    SEARCH_CHOICES = (
        ("N", "Nombre"),
        ("A", "Apellido"),
        ("C", "Cedula"),
        ("I", "ID"),
    )
    filtro = forms.ChoiceField(choices=SEARCH_CHOICES)
    
PropietarioFormSet = modelformset_factory(Propietario, extra=0, can_order=True)
