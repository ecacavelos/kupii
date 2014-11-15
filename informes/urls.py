from django.conf.urls import patterns, url

urlpatterns = patterns('informes.views',    
    url(r'^$', 'informes'),
    url(r'^lotes_libres/$', 'lotes_libres'),
    url(r'^listado_busqueda_lotes/$', 'listar_busqueda_lotes'),
    url(r'^clientes_atrasados/$', 'clientes_atrasados'),
    url(r'^detalle_pagos_clientes/$', 'listar_clientes_atrasados'),
    url(r'^informe_general/$', 'informe_general'),
    url(r'^informe_movimientos/$', 'informe_movimientos'),
    url(r'^liquidacion_propietarios/$', 'liquidacion_propietarios'),
    url(r'^liquidacion_vendedores/$', 'liquidacion_vendedores'),
    url(r'^liquidacion_gerentes/$', 'liquidacion_gerentes'),
    url(r'^lotes_libres_reporte_excel/$', 'lotes_libres_reporte_excel'),
    url(r'^clientes_atrasados_reporte_excel/$', 'clientes_atrasados_reporte_excel'),
    url(r'^informe_general_reporte_excel/$', 'informe_general_reporte_excel'),
)
