from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from principal.models import PlanDePago

# Create the form class.
class PlanDePagoForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = PlanDePago
        exclude = ['deuda_contraida']

class SearchForm(Form):
    buscar = forms.CharField(max_length=100)
    SEARCH_CHOICES = (
        ("N", "Nombre del plan"),
        ("T", "Tipo del plan"),
        ("C", "Cantidad de cuotas"),
        ("I", "ID"),
    )
    filtro = forms.ChoiceField(choices=SEARCH_CHOICES)
    
PlanDePagoFormSet = modelformset_factory(PlanDePago, extra=0, can_order=True)
