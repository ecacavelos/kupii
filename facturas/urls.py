from django.conf.urls import patterns, url

urlpatterns = patterns('facturas.views',
    url(r'^$', 'facturacion'),        
    url(r'^facturar/$', 'facturar'),
    url(r'^facturar_operacion/(?P<tipo_operacion>\d+)/(?P<operacion_id>\d+)/$', 'facturar_operacion', name="frontend_facturar_operacion"),
    url(r'^facturar_pagos/$', 'facturar_pagos', name="frontend_facturar_operacion"),
    url(r'^listado/$', 'consultar_facturas', name='frontend_listado_facturas'),
    url(r'^listado/(?P<factura_id>\d+)/$', 'detalle_factura', name='frontend_detalle_factura'),
)
