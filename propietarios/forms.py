from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from principal.models import Propietario
from django.forms.widgets import TextInput

# Create the form class.
class PropietarioForm(ModelForm):
    required_css_class = 'required'
    #fecha_nacimiento = forms.DateField(input_formats=('%Y-%m-%d', '%d/%m/%Y',))
    #fecha_ingreso = forms.DateField(input_formats=('%Y-%m-%d', '%d/%m/%Y',))
    class Meta:
        model = Propietario
        widgets = {
            'fecha_nacimiento': TextInput (attrs={'class': 'date'}),            
        }
        

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
