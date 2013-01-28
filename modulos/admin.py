from django.contrib import admin
from modulos.models import Cliente, Fraccion, Lote, Vendedor, Cobrador, Propietario

class ClienteAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'cedula']
    search_fields = ['nombres', 'apellidos']
admin.site.register(Cliente, ClienteAdmin)

admin.site.register(Fraccion)
admin.site.register(Lote)
admin.site.register(Vendedor)
admin.site.register(Cobrador)
admin.site.register(Propietario)
