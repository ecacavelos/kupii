from django.forms import ModelForm
from django.forms.models import modelformset_factory
from principal.models import Vendedor
from django.forms.widgets import TextInput

# Create the form class.
class VendedorForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Vendedor
        widgets = {
                 'porcentaje_cuota_inicial': TextInput,
                 'cantidad_cuotas': TextInput,
                 'cuota_inicial': TextInput,
                 'intervalos': TextInput,
                 'porcentaje_de_cuotas': TextInput,               
         }
        
FraccionFormSet = modelformset_factory(Vendedor, extra=0, can_order=True)
