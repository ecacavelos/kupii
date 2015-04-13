from django.contrib import admin
from principal.models import PagoDeCuotas

class PagoDeCuotasAdmin(admin.ModelAdmin):    
    search_fields = ['lote__id']
    list_display = ('fecha_de_pago',)
    pass
admin.site.register(PagoDeCuotas, PagoDeCuotasAdmin)