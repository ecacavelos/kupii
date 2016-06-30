import xlwt

style_titulos_columna = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                    'font: name Calibri; align: horiz center')

style_titulos_columna_resaltados_centrados = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                                         'font: name Calibri; align: horiz center')
style_titulos_columna_resaltados = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                               'font: name Calibri')

style_titulo_resumen = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                   'font: name Calibri, bold True, height 200;')

style_titulo_resumen_centrado = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                   'font: name Calibri, bold True, height 200; align: horiz center')

style_datos_montos = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
style_datos_montos_subrayado = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
style_datos_montos_importante = xlwt.easyxf('font: name Calibri, bold True, height 200 ; align: horiz right')
# style_datos = xlwt.easyxf('pattern: pattern solid, fore_colour white;''font: name Calibri, height 200 ; align: horiz right')

style_normal = xlwt.easyxf('font: name Calibri, height 200;')
style_normal_subrayado_palabra = xlwt.easyxf('font: name Calibri, height 200;')
style_subrayado_normal = xlwt.easyxf('font: name Calibri, height 200;')
style_subrayado_normal_titulo = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')
style_doble_subrayado = xlwt.easyxf('font: name Calibri, height 200;')
style_datos_texto_lote = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')
style_datos_texto = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')

style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                             'font: name Calibri; align: horiz center')

style_datos_montos_importante_doble_borde = xlwt.easyxf(
    'font: name Calibri, bold True, height 200 ; align: horiz right')

# BORDES PARA las columnas de titulos
borders = xlwt.Borders()
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.DOUBLE
style_titulos_columna_resaltados_centrados.borders = borders
style_datos_montos_importante_doble_borde.borders = borders
style_titulos_columna_resaltados.borders = borders

# Subrayado normal
border_subrayado = xlwt.Borders()
border_subrayado.bottom = xlwt.Borders.THIN
style_subrayado_normal.borders = border_subrayado
style_datos_montos_subrayado.borders = border_subrayado
style_subrayado_normal_titulo.borders = border_subrayado

# Doble Subrayado negritas
border_doble_subrayado = xlwt.Borders()
border_doble_subrayado.bottom = xlwt.Borders.THIN
style_doble_subrayado.borders = border_doble_subrayado

# font
font = xlwt.Font()
font.underline = True
style_normal_subrayado_palabra.font = font