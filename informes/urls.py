from django.conf.urls import patterns, url

urlpatterns = patterns('informes.views',    
    url(r'^$', 'informes'),
    url(r'^lotes_libres/$', 'lotes_libres'),
    url(r'^listado_busqueda_lotes/$', 'listar_busqueda_lotes'),
    url(r'^clientes_atrasados/$', 'clientes_atrasados'),
    url(r'^detalle_pagos_clientes/$', 'listar_clientes_atrasados'),
    url(r'^informe_general/$', 'informe_general'),
)
