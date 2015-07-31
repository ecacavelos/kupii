from django.conf.urls import patterns, url

urlpatterns = patterns('parametros.views',
    url(r'^$', 'parametros'),
    url(r'^plan_pago/$', 'plan_de_pago'),
    url(r'^plan_pago/listado/$', 'consultar_plan_de_pago'),
    url(r'^plan_pago/listado/(?P<plandepago_id>\d+)/$', 'detalle_plan_de_pago'),
    url(r'^plan_pago/listado_busqueda_ppagos/$', 'listar_busqueda_ppagos'),
    url(r'^plan_pago/agregar/$', 'agregar_plan_de_pago'),
    url(r'^plan_pago_vendedores/$', 'plan_de_pago_vendedores'),
    url(r'^plan_pago_vendedores/listado/$', 'consultar_plan_de_pago_vendedores'),
    url(r'^plan_pago/listado_busqueda_ppagos_vendedores/$', 'listar_busqueda_ppagos_vendedores'),
    url(r'^plan_pago_vendedores/listado/(?P<plandepago_vendedor_id>\d+)/$', 'detalle_plan_de_pago_vendedores'),
    url(r'^plan_pago_vendedores/agregar/$', 'agregar_plan_de_pago_vendedores'),  
    url(r'^generales/$', 'parametros_generales'),
)