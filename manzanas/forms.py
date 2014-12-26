from django.forms import ModelForm
from django.forms.models import modelformset_factory
from principal.models import Manzana

# Create the form class.
class ManzanaForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Manzana
        
ManzanaFormSet = modelformset_factory(Manzana, extra=0, can_order=True)
