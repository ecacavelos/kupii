from django.forms import ModelForm
from django.forms.models import modelformset_factory
from principal.models import Fraccion
from django.forms.widgets import TextInput
from django.forms.widgets import HiddenInput


# Create the form class.
class FraccionForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Fraccion
        widgets = {
            'propietario': HiddenInput,            
        }
     
class FraccionFormAdd(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Fraccion
        widgets = {
            'propietario': HiddenInput,            
        }        
        
                
FraccionFormSet = modelformset_factory(Fraccion, extra=0, can_order=True)
