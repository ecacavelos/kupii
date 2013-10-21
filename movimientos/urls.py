from django.conf.urls import patterns, url

urlpatterns = patterns('movimientos.views',    
    url(r'^$', 'movimientos'),
    #url(r'^datos/$', 'movimientos_datos'),
    url(r'^ventas_lotes/$', 'ventas_de_lotes'),
    url(r'^ventas_lotes/calcular_cuotas/$', 'ventas_de_lotes_calcular_cuotas'),
    url(r'^reservas_lotes/$', 'reservas_de_lotes'),
)
