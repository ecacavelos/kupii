from django.conf.urls import patterns, url

urlpatterns = patterns('movimientos.views',    
    url(r'^$', 'movimientos'),
    #url(r'^datos/$', 'movimientos_datos'),
    url(r'^ventas_lotes/$', 'ventas_de_lotes'),
    url(r'^ventas_lotes/calcular_cuotas/$', 'ventas_de_lotes_calcular_cuotas'),
    url(r'^pago_cuotas/$', 'pago_de_cuotas'),
    url(r'^reservas_lotes/$', 'reservas_de_lotes'),
    url(r'^transferencias_lotes/$', 'transferencias_de_lotes'),
    url(r'^cambio_lotes/$', 'cambio_de_lotes'),
    url(r'^recuperacion_lotes/$', 'recuperacion_de_lotes'),
    url(r'^listado_ventas/$', 'listar_ventas'),
    url(r'^listado_pagos/$', 'listar_pagos'),
    url(r'^listado_cambios/$', 'listar_cambios'),
    url(r'^listado_recuperacion/$', 'listar_rec'),
    url(r'^listado_reservas/$', 'listar_res'),
    url(r'^listado_transferencias/$', 'listar_transf'),
)