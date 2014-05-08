from django.conf.urls import patterns, url

urlpatterns = patterns('informes.views',    
    url(r'^$', 'informes'),
    url(r'^lotes_libres/$', 'lotes_libres'),
    url(r'^detalle_pagos_clientes/$', 'listar_clientes_atrasados'),
)
