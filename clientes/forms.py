from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from datos.models import Cliente

# Create the form class.
class ClienteForm(ModelForm):
    class Meta:
        model = Cliente

class SearchForm(Form):
    search_string = forms.CharField(max_length=100)
    
ClienteFormSet = modelformset_factory(Cliente)

