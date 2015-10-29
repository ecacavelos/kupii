from django.conf.urls import patterns, url

urlpatterns = patterns('parametros.views',
    url(r'^$', 'parametros'),
    url(r'^plan_pago/$', 'plan_de_pago'),
    url(r'^plan_pago/listado/$', 'consultar_plan_de_pago'),
    url(r'^plan_pago/listado/(?P<plandepago_id>\d+)/$', 'detalle_plan_de_pago'),
    url(r'^plan_pago/listado_busqueda_ppagos/$', 'listar_busqueda_ppagos'),
    
    url(r'^plan_pago/listado_busqueda_ppagos/(?P<plandepago_id>\d+)', 'detalle_plan_de_pago'),
    
    url(r'^plan_pago/agregar/$', 'agregar_plan_de_pago'),
    url(r'^plan_pago_vendedores/$', 'plan_de_pago_vendedores'),
    url(r'^plan_pago_vendedores/listado/$', 'consultar_plan_de_pago_vendedores'),
    url(r'^plan_pago/listado_busqueda_ppagos_vendedores/$', 'listar_busqueda_ppagos_vendedores'),
    url(r'^plan_pago_vendedores/listado/(?P<plandepago_vendedor_id>\d+)/$', 'detalle_plan_de_pago_vendedores'),
    url(r'^plan_pago_vendedores/agregar/$', 'agregar_plan_de_pago_vendedores'),  
    url(r'^generales/$', 'parametros_generales'),
    
    url(r'^log_usuario/$', 'log_usuario'),
    url(r'^log_usuario/listado/$', 'consultar_log_usuario'),
    url(r'^log_usuario/listado_busqueda_log_usuario/$', 'listar_busqueda_log_usuario'),
    
    url(r'^timbrado/$', 'timbrado'),
    url(r'^timbrado/listado/$', 'consultar_timbrado'),
    url(r'^timbrado/listado/(?P<timbrado_id>\d+)/$', 'detalle_timbrado'),
    url(r'^timbrado/listado_busqueda_timbrado/$', 'listar_busqueda_timbrado'),
    url(r'^timbrado/agregar/$', 'agregar_timbrado'),
    
    url(r'^concepto_factura/$', 'concepto_factura'),
    url(r'^concepto_factura/listado/$', 'consultar_concepto_factura'),
    url(r'^concepto_factura/listado/(?P<concepto_factura_id>\d+)/$', 'detalle_concepto_factura'),
    url(r'^concepto_factura/listado_busqueda_concepto_factura/$', 'listar_busqueda_concepto_factura'),
    url(r'^concepto_factura/agregar/$', 'agregar_concepto_factura'),
    
    url(r'^coordenadas_factura/$', 'coordenadas_factura'),
    url(r'^coordenadas_factura/listado/$', 'consultar_coordenadas_factura'),
    url(r'^coordenadas_factura/listado/(?P<coordenadas_factura_id>\d+)/$', 'detalle_coordenadas_factura'),
    url(r'^coordenadas_factura/listado_busqueda_coordendas_factura/$', 'listar_busqueda_coordenadas_factura'),
    url(r'^coordenadas_factura/agregar/$', 'agregar_coordenadas_factura'),
    
    url(r'^timbrado/listado/(?P<timbrado_id>\d+)/rango_factura/$', 'rango_factura'),
    url(r'^timbrado/listado/(?P<timbrado_id>\d+)/rango_factura/listado/$', 'consultar_rango_factura'),
    url(r'^timbrado/listado/(?P<timbrado_id>\d+)/rango_factura/listado/(?P<rango_factura_id>\d+)/$', 'detalle_rango_factura'),
    url(r'^timbrado/listado/(?P<timbrado_id>\d+)/rango_factura/listado_busqueda_rango_factura/$', 'listar_busqueda_rango_factura'),
    url(r'^timbrado/listado/(?P<timbrado_id>\d+)/rango_factura/agregar/$', 'agregar_rango_factura'),
)