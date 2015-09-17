from django.conf.urls import patterns, url

urlpatterns = patterns('facturas.views',        
    url(r'^facturar/$', 'facturar'),
    url(r'^facturar_pagos/(?P<pago_id>\d+)/$', 'facturar_pagos'),
    url(r'^listado/$', 'consultar_facturas'),
    url(r'^listado/(?P<factura_id>\d+)/$', 'detalle_factura'),
)
