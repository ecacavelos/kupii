from django.contrib import admin
from principal.models import Cliente, Fraccion, Manzana, Lote, Vendedor, Cobrador, Propietario, PlanDePago, Venta

class ClienteAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'cedula']
    search_fields = ['nombres', 'apellidos']
admin.site.register(Cliente, ClienteAdmin)

# class LoteAdmin(admin.ModelAdmin):
#     list_display = ['__unicode__', 'estado']
#     ordering = ['fraccion', 'manzana', 'nro_lote']
# admin.site.register(Lote, LoteAdmin)
admin.site.register(Fraccion)
admin.site.register(Manzana)
admin.site.register(Lote)
admin.site.register(Vendedor)
admin.site.register(Cobrador)
admin.site.register(Propietario)
admin.site.register(PlanDePago)
admin.site.register(Venta)
