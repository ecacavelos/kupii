from django import forms
from django.forms import Form, ModelForm
from django.forms.models import modelformset_factory
from principal.models import Factura

# Create the form class.
# class FacturaForm(ModelForm):
#     class Meta:
#         model = Factura
#         fields = ['fecha', 'headline', 'content', 'reporter']
