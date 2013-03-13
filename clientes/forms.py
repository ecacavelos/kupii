from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from datos.models import Cliente

# Create the form class.
class ClienteForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Cliente
        exclude = ('deuda_contraida')

class SearchForm(Form):
    buscar = forms.CharField(max_length=100)
    SEARCH_CHOICES = (
        ("N", "Nombre"),
        ("A", "Apellido"),
        ("C", "Cedula"),
        ("I", "ID"),
    )
    filtro = forms.ChoiceField(choices=SEARCH_CHOICES)
    
ClienteFormSet = modelformset_factory(Cliente, extra=0, can_order=True)
