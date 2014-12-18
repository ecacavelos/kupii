from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from principal.models import PlanDePago, PlanDePagoVendedor
from django.forms.widgets import TextInput, Textarea

# Create the form class.
class PlanDePagoForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = PlanDePago
        exclude = ['deuda_contraida']
        
        widgets = {
                 'cantidad_de_cuotas': TextInput,
                 'porcentaje_inicial_inmobiliaria': TextInput,
                 'cantidad_cuotas_inmobiliaria': TextInput,
                 'inicio_cuotas_inmobiliaria': TextInput,
                 'intervalos_cuotas_inmobiliaria': TextInput,               
                 'porcentaje_cuotas_inmobiliaria': TextInput,
                 'porcentaje_cuotas_administracion': TextInput,
                 'porcentaje_inicial_gerente': TextInput,
                 'cantidad_cuotas_gerente': TextInput,
                 'inicio_cuotas_gerente': TextInput,                 
                 'intervalos_cuotas_gerente': TextInput,
                 'porcentaje_cuotas_gerente': TextInput,
                 'monto_fijo_cuotas_gerente': TextInput,
         }
        
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

# Create the form class.
class PlanDePagoVendedorForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = PlanDePagoVendedor
        widgets = {
                 'porcentaje_cuota_inicial': TextInput,
                 'cantidad_cuotas': TextInput,
                 'cuota_inicial': TextInput,
                 'intervalos': TextInput,
                 'porcentaje_de_cuotas': TextInput,
                 'observacion': Textarea,               
         }
        
FraccionFormSet = modelformset_factory(PlanDePagoVendedor, extra=0, can_order=True)
