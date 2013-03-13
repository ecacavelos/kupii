from django.contrib import admin
from datos.models import Cliente, Fraccion, Lote, Vendedor, Cobrador, Propietario, PlanDePagos, PlanDeVendedores, Venta

class ClienteAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'cedula']
    search_fields = ['nombres', 'apellidos']
admin.site.register(Cliente, ClienteAdmin)

class LoteAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'estado']
    ordering = ['fraccion', 'manzana', 'nro_lote']
admin.site.register(Lote, LoteAdmin)

admin.site.register(Fraccion)
admin.site.register(Vendedor)
admin.site.register(Cobrador)
admin.site.register(Propietario)
admin.site.register(PlanDePagos)
admin.site.register(PlanDeVendedores)
admin.site.register(Venta)
