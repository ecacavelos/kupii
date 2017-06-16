from django.conf.urls import patterns, include, url

urlpatterns = patterns('ajax.views',        
    # Fracciones
    url(r'^get_fracciones_by_name/$', 'get_fracciones_by_name', name='get_fracciones_by_name'),
    url(r'^get_fracciones_by_sucursal/$', 'get_fracciones_by_sucursal', name='get_fracciones_by_sucursal'),
    url(r'^get_fracciones_by_id/$', 'get_fracciones_by_id', name='get_fracciones_by_id'),

    url(r'^get_manzanas_by_fraccion/$', 'get_manzanas_by_fraccion', name='get_manzanas_by_fraccion'),
    url(r'^get_ventas_by_lote/$', 'get_ventas_by_lote', name='get_ventas_by_lote'),
    url(r'^get_ventas_by_cliente/$', 'get_ventas_by_cliente', name='get_ventas_by_cliente'),

    url(r'^get_pagos_by_venta/$', 'get_pagos_by_venta', name='get_pagos_by_venta'),

    url(r'^get_propietario_id_by_name/$', 'get_propietario_id_by_name', name='get_propietario_id_by_name'),
    url(r'^get_propietario_lastId/$', 'get_propietario_lastId', name='get_propietario_lastId'),
    url(r'^get_propietario_name_by_id/$', 'get_propietario_name_by_id', name='get_propietario_name_by_id'),    
    url(r'^get_propietario_name_id_by_cedula/$', 'get_propietario_name_id_by_cedula', name='get_propietario_name_id_by_cedula'),
    
    url(r'^get_concepto_factura_by_name/$', 'get_concepto_factura_by_name', name='get_concepto_factura_by_name'),
    
#     url(r'^create_form_by_number/$', 'create_form_by_number', name='create_form_by_number'),
    url(r'^get_lotes_a_cargar_by_manzana/$', 'get_lotes_a_cargar_by_manzana', name='get_lotes_a_cargar_by_manzana'),
    url(r'^get_lotes_by_manzana/$', 'get_lotes_by_manzana', name='get_lotes_by_manzana'),
    url(r'^get_cliente_id_by_name/$', 'get_cliente_id_by_name', name='get_cliente_id_by_name'),
    url(r'^get_cliente_id_by_name_or_ruc/$', 'get_cliente_id_by_name_or_ruc', name='get_cliente_id_by_name_or_ruc'), 
    url(r'^get_cliente_name_id_by_cedula/$', 'get_cliente_name_id_by_cedula', name='get_cliente_name_id_by_cedula'),
    url(r'^get_vendedor_id_by_name/$', 'get_vendedor_id_by_name', name='get_vendedor_id_by_name'),
    url(r'^get_vendedor_name_id_by_cedula/$', 'get_vendedor_name_id_by_cedula', name='get_vendedor_name_id_by_cedula'),
    url(r'^get_plan_pago/$', 'get_plan_pago', name='get_plan_pago'),
    url(r'^get_plan_pago_vendedor/$', 'get_plan_pago_vendedor', name='get_plan_pago_vendedor'),
    url(r'^get_timbrado_by_numero/$', 'get_timbrado_by_numero', name='get_timbrado_by_numero'),
    url(r'^get_mes_pagado_by_id_lote/$', 'get_mes_pagado_by_id_lote', name='get_mes_pagado_by_id_lote'),
    url(r'^get_pago_cuotas_by_lote_cliente/$', 'get_pago_cuotas_by_lote_cliente', name='get_pago_cuotas_by_lote_cliente'),
    url(r'^get_detalles_factura/$', 'get_detalles_factura', name='get_detalles_factura'),
    url(r'^get_pagos_by_ventas/$', 'get_pagos_by_ventas', name='get_pagos_by_ventas'),
    
    url(r'^facturar/$', 'facturar', name='facturar'),
    
    url(r'^get_usuario_by_username/$', 'get_usuario_by_username', name='get_usuario_by_username'), 
    
    url(r'^get_lote_by_codigo_paralot/$', 'get_lote_by_codigo_paralot', name='get_lote_by_codigo_paralot'),

    url(r'^get_lotes_by_estado/$', 'get_lotes_by_estado', name='get_lotes_by_estado'),

    url(r'^get_factura_by_numero/$', 'get_factura_by_numero', name='get_factura_by_numero'),
    
    url(r'^marcar_impresa/$', 'marcar_impresa', name='marcar_impresa'),
    
    url(r'^imprimir_factura/$', 'imprimir_factura', name='imprimir_factura'),
    url(r'^get_plan_vendedor/$', 'get_plan_vendedor', name='get_plan_vendedor'),
    url(r'^get_plan_pago_fraccion/$', 'get_plan_pago_fraccion', name='get_plan_pago_fraccion'),

    url(r'^get_sucursales_by_name/$', 'get_sucursales_by_name', name='get_sucursales_by_name'),

    url(r'^get_usuario_by_name/$', 'get_usuario_by_name', name='get_usuario_by_name'),
#     url(r'^get_lista_pagos/$', 'get_lista_pagos', name='get_lista_pagos'),
#     url(r'^get_lista_pagos_gerentes/$', 'get_lista_pagos_gerentes', name='get_lista_pagos_gerentes'), 
#     url(r'^get_informe_general/$', 'get_informe_general', name='get_informe_general'),
#     url(r'^get_reporte_lotes_libres/$', 'get_reporte_lotes_libres', name='get_reporte_lotes_libres'),
#     url(r'^get_lotes_libres/$', 'get_lotes_libres', name='get_lotes_libres'),         
#     url(r'^get_reporte_lotes_libres/$', 'get_reporte_lotes_libres', name='get_reporte_lotes_libres'),         
)
