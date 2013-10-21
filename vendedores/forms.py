from django.forms import ModelForm
from django.forms.models import modelformset_factory
from principal.models import Vendedor

# Create the form class.
class VendedorForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Vendedor
        
FraccionFormSet = modelformset_factory(Vendedor, extra=0, can_order=True)
