from django.conf.urls import patterns, url

urlpatterns = patterns('informes.views',    
    url(r'^$', 'informes'),
    url(r'^lotes_libres/$', 'lotes_libres'),
    url(r'^listado_busqueda_lotes/$', 'listar_busqueda_lotes'),
    url(r'^clientes_atrasados/$', 'clientes_atrasados', name='frontend_clientes_atrasados'),
    url(r'^detalle_pagos_clientes/$', 'listar_clientes_atrasados'),
    url(r'^informe_general/$', 'informe_general'),
    url(r'^informe_cuotas_por_cobrar/$', 'informe_cuotas_por_cobrar'),
    url(r'^informe_facturacion/$', 'informe_facturacion'),
    url(r'^informe_facturacion_reporte_excel/$', 'informe_facturacion_reporte_excel'),
    url(r'^informe_movimientos/$', 'informe_movimientos'),
    url(r'^liquidacion_propietarios/$', 'liquidacion_propietarios'),
    url(r'^liquidacion_vendedores/$', 'liquidacion_vendedores'),
    url(r'^liquidacion_general_vendedores/$', 'liquidacion_general_vendedores'),
    url(r'^liquidacion_gerentes/$', 'liquidacion_gerentes'),
    # url(r'^lotes_libres_reporte_excel/$', 'lotes_libres_reporte_excel'),
    url(r'^clientes_atrasados_reporte_excel/$', 'clientes_atrasados_reporte_excel'),
    url(r'^informe_general_reporte_excel/$', 'informe_general_reporte_excel'),
    url(r'^liquidacion_propietarios_reporte_excel/$', 'liquidacion_propietarios_reporte_excel'),
    url(r'^liquidacion_vendedores_reporte_excel/$', 'liquidacion_vendedores_reporte_excel'),
    url(r'^liquidacion_general_vendedores_reporte_excel/$', 'liquidacion_general_vendedores_reporte_excel'),
    url(r'^liquidacion_gerentes_reporte_excel/$', 'liquidacion_gerentes_reporte_excel'),
    url(r'^informe_movimientos_reporte_excel/$', 'informe_movimientos_reporte_excel'),
    url(r'^informe_ventas/$', 'informe_ventas', name='frontend_informe_ventas'),
    url(r'^informe_ventas_reporte_excel/$', 'informe_ventas_reporte_excel'),
    url(r'^informe_pagos_practipago/$', 'informe_pagos_practipago', name='frontend_informe_ventas'),
    url(r'^informe_pagos_practipago_reporte_excel/$', 'informe_pagos_practipago_reporte_excel'),
    url(r'^informe_cuotas_devengadas/$', 'informe_cuotas_devengadas'),
)
