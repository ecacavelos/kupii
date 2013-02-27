from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from datos.models import Cobrador

# Create the form class.
class CobradorForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Cobrador
    
ClienteFormSet = modelformset_factory(Cobrador, extra=0, can_order=True)
