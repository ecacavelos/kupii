from django.conf.urls import patterns, url

urlpatterns = patterns('facturas.views',        
    url(r'^facturar/$', 'facturar'),
    url(r'^listado/(?P<factura_id>\d+)/$', 'detalle_factura'),
    url(r'^listado/$', 'consultar_facturas'),
)
