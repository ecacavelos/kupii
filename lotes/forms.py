from django.forms import ModelForm
from django.forms.models import modelformset_factory
from datos.models import Lote

# Create the form class.
class LoteForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Lote
        
FraccionFormSet = modelformset_factory(Lote, extra=0, can_order=True)
