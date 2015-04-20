from django.contrib import admin
from principal.models import Lote

class LoteAdmin(admin.ModelAdmin):    
    search_fields = ['codigo_paralot']
    list_display = ('codigo_paralot',)
    readonly_fields=('id',)
    pass
admin.site.register(Lote, LoteAdmin)