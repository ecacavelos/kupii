from django.contrib.auth.models import Permission
from django.contrib import admin
from contactos_models import Contacto
admin.site.register(Permission)
admin.site.register(Contacto)
