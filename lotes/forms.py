from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from django.forms.widgets import TextInput
from principal.models import Lote

# Create the form class.
class LoteForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Lote
        exclude = ('vendido', 'fecha_de_venta'),        
        widgets = {
                 'nro_lote': TextInput,
                 'precio_contado': TextInput,
                 'precio_credito': TextInput,
                 'superficie': TextInput,
                 'boleto_nro': TextInput,                 
         }
        
#class LoteIdentifierForm(Form):
    #buscar = forms.CharField(max_length=100)
        
LoteFormSet = modelformset_factory(Lote, extra=0, can_order=True)

class FraccionManzana(Form):
    fraccion = forms.CharField(max_length=50)
#     manzana = forms.ChoiceField(widget=forms.Select)