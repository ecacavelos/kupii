from django.conf.urls import patterns, url

urlpatterns = patterns('facturas.views',
    url(r'^$', 'facturacion'),        
    url(r'^facturar/$', 'facturar'),
    url(r'^facturar_operacion/(?P<tipo_operacion>\d+)/(?P<operacion_id>\d+)/$', 'facturar_operacion'),
    url(r'^listado/$', 'consultar_facturas', name='frontend_listado_facturas'),
    url(r'^listado/(?P<factura_id>\d+)/$', 'detalle_factura'),
)
