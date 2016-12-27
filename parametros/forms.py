from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from principal.models import PlanDePago, PlanDePagoVendedor, Timbrado, RangoFactura, ConceptoFactura, CoordenadasFactura
from django.forms.widgets import TextInput, Textarea, CheckboxInput
from django.contrib.auth.models import User


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
            'cuotas_de_refuerzo': TextInput,
            'intervalo_cuota_refuerzo': TextInput
        }


class TimbradoForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Timbrado
        exclude = ['deuda_contraida']

        widgets = {
            'numero': TextInput,
            'desde': TextInput,
            'hasta': TextInput,

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


TimbradoFormSet = modelformset_factory(Timbrado, extra=0, can_order=True)


class ConceptoFacturaForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = ConceptoFactura
        exclude = ['deuda_contraida']

        widgets = {
            'descripcion': TextInput,
            'precio_unitario': TextInput,
            'exentas': CheckboxInput,
            'iva10': CheckboxInput,
            'iva5': CheckboxInput,

        }


class CoordenadasFacturaForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = CoordenadasFactura

        widgets = {

        }

ConceptoFacturaFormSet = modelformset_factory(ConceptoFactura, extra=0, can_order=True)


class RangoFacturaForm(ModelForm):
    required_css_class = 'required'
    usuario = forms.ChoiceField(required=False)

    class Meta:
        model = RangoFactura
        exclude = ['deuda_contraida']

        widgets = {
            'nro_sucursal': TextInput,
            'nro_boca': TextInput,
            'nro_desde': TextInput,
            'nro_hasta': TextInput,

        }

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session', None)
        super(RangoFacturaForm, self).__init__(*args, **kwargs)
        self.fields['usuario'] = forms.ChoiceField(
            choices=opciones_usuarios('-- Seleccione --'),
            widget=forms.Select(
                attrs={'style': 'width: auto; margin-left:3%;margin: 1.5% 1.5%'}
            )
        )

RangoFacturaFormSet = modelformset_factory(RangoFactura, extra=0, can_order=True)


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


def opciones_usuarios(first_option=None):
    usuarios = User.objects.all().order_by('id')
    lista_usuarios_tupla = []
    usuarios_list = usuarios
    if first_option is not None:
        tupla_zero = ('', first_option)
        lista_usuarios_tupla.append(tupla_zero)

    for idx, usuario in enumerate(usuarios_list):
        tupla = (usuario.id, usuario.username)
        lista_usuarios_tupla.append(tupla)
    usuarios = tuple(lista_usuarios_tupla)
    return usuarios
