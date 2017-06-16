# -*- encoding: utf-8 -*-
from django.forms import ModelForm, ModelChoiceField, CharField, DateTimeField
from django.forms.widgets import TextInput, Textarea, HiddenInput, DateTimeInput
from contactos.contactos_models import Contacto
from tipo_contacto.models import TipoContacto
from motivo_contacto.models import MotivoContacto


class ContactoAddForm(ModelForm):
    required_css_class = 'required'
    tipo_contacto = ModelChoiceField(TipoContacto.objects.all(), empty_label=None)
    motivo_contacto = ModelChoiceField(MotivoContacto.objects.all(), empty_label=None)

    comentarios_gerencia = CharField(required=False, widget=Textarea(
                attrs={
                    'placeholder': 'Escribir aquí los comentarios (si son necesarios) de la gerencia respecto al contacto',
                    'rows': 8,
                    'cols': 100,
                    'required': 'false'
                }))
    fecha_respuesta = DateTimeField(required=False, widget=DateTimeInput(
        attrs={'placeholder': 'Ej: dd/mm/aaaaa',
               'size': 25,
               'maxlength': 10,
               'required': 'false'
               }))
    mensaje_respuesta = CharField(required=False, widget=Textarea(
        attrs={'placeholder': 'Escribir aquí el contenido de la respuesta obtenida o tema acordado en reunión o llamada',
               'rows': 8,
               'cols': 100,
               'required': 'false'
               }))
    recipiente = CharField(required=False, widget=TextInput(
        attrs={'placeholder': 'Nombre del cliente, o la persona que respondió el mensaje, mail, llamada, reunión',
               'size': 100,
               'maxlength': 100,
               'required': 'false'
               }))
    tipo_respuesta = ModelChoiceField(TipoContacto.objects.all(), required=False)
    proximo_contacto = DateTimeField(required=False, widget=DateTimeInput(
        attrs={'placeholder': 'Ej: dd/mm/aaaaa',
               'size': 25,
               'maxlength': 10,
               'required': 'false'
               }))

    class Meta:
        model = Contacto

        widgets = {
            'lote': HiddenInput(),
            'cliente': HiddenInput(),
            'numero_direccion_contactado': TextInput(attrs={'placeholder': 'Numero de Telefono, Mail, o Dirección de reunión', 'size': 100, 'maxlength': 100}),
            'fecha_contacto': DateTimeInput(attrs={'placeholder': 'Ej: dd/mm/aaaaa', 'size': 25, 'maxlength': 10}),
            'mensaje_enviado' : Textarea(attrs={'placeholder': 'Escribir aquí el contenido del mensaje enviado o tema tratado en reunión o llamada', 'rows': 8, 'cols': 100}),

        }


class ContactoEditForm(ModelForm):
    required_css_class = 'required'
    tipo_contacto = ModelChoiceField(TipoContacto.objects.all(), empty_label=None)
    motivo_contacto = ModelChoiceField(MotivoContacto.objects.all(), empty_label=None)

    comentarios_gerencia = CharField(required=False, widget=Textarea(
                attrs={
                    'placeholder': 'Escribir aquí los comentarios (si son necesarios) de la gerencia respecto al contacto',
                    'rows': 8,
                    'cols': 100,
                    'required': 'false'
                }))
    fecha_respuesta = DateTimeField(widget=DateTimeInput(
        attrs={'placeholder': 'Ej: dd/mm/aaaaa',
               'size': 25,
               'maxlength': 10,
               }))
    mensaje_respuesta = CharField(widget=Textarea(
        attrs={'placeholder': 'Escribir aquí el contenido de la respuesta obtenida o tema acordado en reunión o llamada',
               'rows': 8,
               'cols': 100,
               }))
    recipiente = CharField(widget=TextInput(
        attrs={'placeholder': 'Nombre del cliente, o la persona que respondió el mensaje, mail, llamada, reunión',
               'size': 100,
               'maxlength': 100,
               }))
    tipo_respuesta = ModelChoiceField(TipoContacto.objects.all(), empty_label=None)
    proximo_contacto = DateTimeField(required=False, widget=DateTimeInput(
        attrs={'placeholder': 'Ej: dd/mm/aaaaa',
               'size': 25,
               'maxlength': 10,
               'required': 'false'
               }))

    class Meta:
        model = Contacto

        widgets = {
            'lote': HiddenInput(),
            'cliente': HiddenInput(),
            'numero_direccion_contactado': TextInput(attrs={'placeholder': 'Numero de Telefono, Mail, o Dirección de reunión', 'size': 100, 'maxlength': 100}),
            'fecha_contacto': DateTimeInput(attrs={'placeholder': 'Ej: dd/mm/aaaaa', 'size': 25, 'maxlength': 10}),
            'mensaje_enviado' : Textarea(attrs={'placeholder': 'Escribir aquí el contenido del mensaje enviado o tema tratado en reunión o llamada', 'rows': 8, 'cols': 100}),

        }
