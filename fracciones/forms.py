from django.forms import ModelForm
from django.forms.models import modelformset_factory
from datos.models import Fraccion

# Create the form class.
class FraccionForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Fraccion
        
FraccionFormSet = modelformset_factory(Fraccion, extra=0, can_order=True)
