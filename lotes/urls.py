from django.conf.urls import patterns, url

urlpatterns = patterns('lotes.views',    
    url(r'^$', 'lotes',name='frontend_lotes_index'),
    url(r'^listado/$', 'consultar_lotes', name='frontend_listado_lote'),
    url(r'^consultar/$', 'consultar_proximo_pago_lote', name='frontend_listado_lote'),
    url(r'^listado/(?P<lote_id>\d+)/$', 'detalle_lote', name='frontend_detalle_lote'),
    url(r'^listado/ventas/(?P<venta_id>\d+)/$', 'detalle_ventas_lote'),
    url(r'^agregar/$', 'agregar_lotes'),
    url(r'^listado_busqueda_lotes/$', 'listar_busqueda_lotes'),
    url(r'^listado_busqueda_lotes/(?P<lote_id>\d+)/$', 'detalle_lote'),
    #url(r'^prueba/$', 'prueba'),
)
