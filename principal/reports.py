'''
Created on Nov 6, 2014

@author: J. Danilo
'''

import xlwt
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError

def reporte_general_pagos(object_list):
    cuotas=object_list
    wb=xlwt.Workbook(encoding='utf-8')
    sheet=wb.add_sheet('test',cell_overwrite_ok=True)
    style=xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2=xlwt.easyxf('font: name Arial, bold True;')
    #cabeceras
    sheet.write(0,0,"Fraccion",style)
    sheet.write(0,1,"Lote Nro.",style)
    sheet.write(0,2,"Cliente",style)
    sheet.write(0,3,"Cuota Nro.",style)
    sheet.write(0,4,"Plan de Pago",style)
    sheet.write(0,5,"Fecha de Pago",style)
    sheet.write(0,6,"Total de Cuotas",style)
    sheet.write(0,7,"Total de Mora",style)
    sheet.write(0,8,"Total de Pago",style)
    
    #wb.save('informe_general.xls')
    #guardamos la primera fraccion para comparar
    fraccion_actual = cuotas[0]['fraccion_id']
    
    total_cuotas = 0
    total_mora = 0
    total_pagos = 0
    total_general_cuotas = 0
    total_general_mora = 0
    total_general_pagos = 0
    
    #i=0
    #contador de filas
    c=1
    for i in range(len(cuotas)):
    #for i,cuota in enumerate(cuotas,start=1):
        #se suman los totales por fracion
        if (cuotas[i]['fraccion_id'] == fraccion_actual):
            total_cuotas += cuotas[i]['total_de_cuotas']
            total_mora += cuotas[i]['total_de_mora']
            total_pagos += cuotas[i]['total_de_pago']
            
            sheet.write(c,0,str(cuotas[i]['fraccion']))
            sheet.write(c,1,str(cuotas[i]['lote']))
            sheet.write(c,2,str(cuotas[i]['cliente']))
            sheet.write(c,3,str(cuotas[i]['cuota_nro']))
            sheet.write(c,4,str(cuotas[i]['plan_de_pago']))
            sheet.write(c,5,str(cuotas[i]['fecha_pago']))
            sheet.write(c,6,str(cuotas[i]['total_de_cuotas']))
            sheet.write(c,7,str(cuotas[i]['total_de_mora']))
            sheet.write(c,8,str(cuotas[i]['total_de_pago']))
            c+=1
            #... y acumulamos para los totales generales
            total_general_cuotas += cuotas[i]['total_de_cuotas']
            total_general_mora += cuotas[i]['total_de_mora'] 
            total_general_pagos += cuotas[i]['total_de_pago'] 
            #si es la ultima fila

        else: 
            
            sheet.write(c,0,"Totales de Fraccion",style2)
            sheet.write(c,6,total_cuotas)
            sheet.write(c,7,total_mora)
            sheet.write(c,8,total_pagos)
            c+=1
            
            sheet.write(c,0,str(cuotas[i]['fraccion']))
            sheet.write(c,1,str(cuotas[i]['lote']))
            sheet.write(c,2,str(cuotas[i]['cliente']))
            sheet.write(c,3,str(cuotas[i]['cuota_nro']))
            sheet.write(c,4,str(cuotas[i]['plan_de_pago']))
            sheet.write(c,5,str(cuotas[i]['fecha_pago']))
            sheet.write(c,6,str(cuotas[i]['total_de_cuotas']))
            sheet.write(c,7,str(cuotas[i]['total_de_mora']))
            sheet.write(c,8,str(cuotas[i]['total_de_pago']))
            
            fraccion_actual = cuotas[i]['fraccion_id']
            total_cuotas = 0;
            total_mora = 0;
            total_pagos = 0;
            total_cuotas += cuotas[i]['total_de_cuotas'];
            total_mora += cuotas[i]['total_de_mora'];
            total_pagos += cuotas[i]['total_de_pago'];
            
        if (i == len(cuotas)-1):             
            sheet.write(c,0,"Totales de Fraccion", style2)
            sheet.write(c,6,total_cuotas,style2)
            sheet.write(c,7,total_mora,style2)
            sheet.write(c,8,total_pagos,style2)
            
            
    sheet.write(c+1,0,"Totales Generales",style2)
    sheet.write(c+1,6,total_general_cuotas,style2)
    sheet.write(c+1,7,total_general_mora,style2)
    sheet.write(c+1,8,total_general_pagos,style2)
    
    wb.save('informe_general.xls')
#     response = HttpResponse(mimetype="application/ms-excel")
#     response['Content-Disposition'] = 'attachment; filename=%s' % fname
#     wb.save(response)
#     return response
#         
        

    
def reporte_liquidacion_propietarios(object_list,totales): 
    
    wb=xlwt.Workbook(encoding='utf-8')
    sheet=wb.add_sheet('test',cell_overwrite_ok=True)
    style=xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2=xlwt.easyxf('font: name Arial, bold True;')
    
    sheet.write(0,0,"Fecha de Venta",style)
    sheet.write(0,1,"Lote Nro.",style)
    sheet.write(0,2,"Cliente",style)
    sheet.write(0,3,"Cuota Nro.",style)
    sheet.write(0,4,"Monto Pagado",style)
    sheet.write(0,5,"Monto Inmobiliaria",style)
    sheet.write(0,6,"Monto Propietario",style)
    
    c=1
    total_monto_pagado=0
    total_monto_inm=0
    total_monto_propietario=0
    for i in range(len(object_list)):              
        sheet.write(c,0,str(object_list[i][0]))
        sheet.write(c,1,str(object_list[i][1]))
        sheet.write(c,2,str(object_list[i][2]))
        sheet.write(c,3,str(object_list[i][3]))
        sheet.write(c,4,str(object_list[i][4]))
        sheet.write(c,5,str(object_list[i][5]))
        sheet.write(c,6,str(object_list[i][6]))
        
        c+=1
    if (i == len(object_list)-1):             
        sheet.write(c,0,"Liquidacion", style2)
        sheet.write(c,4,totales[0])
        sheet.write(c,5,totales[1])
        sheet.write(c,6,totales[2])
    wb.save('liquidacion_propietarios.xls')
#     response = HttpResponse(mimetype="application/ms-excel")
#     response['Content-Disposition'] = 'attachment; filename=%s' % fname
#     wb.save(response)
#     return response


def reporte_liquidacion_vendedores(object_list):
    cuotas=object_list
    wb=xlwt.Workbook(encoding='utf-8')
    sheet=wb.add_sheet('test',cell_overwrite_ok=True)
    style=xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2=xlwt.easyxf('font: name Arial, bold True;')
    #cabeceras
    sheet.write(0,0,"Cliente",style)
    sheet.write(0,1,"Lote Nro.",style)    
    sheet.write(0,2,"Cuota Nro.",style)
    sheet.write(0,3,"Fecha de Pago",style)
    sheet.write(0,4,"Importe",style)
    sheet.write(0,5,"Comision",style)
    sheet.write(0,6,"Fraccion",style)
    #wb.save('informe_general.xls')
    #guardamos la primera fraccion para comparar
    fraccion_actual = cuotas[0]['fraccion_id']
    
    total_importe = 0
    total_comision = 0
    total_general_importe = 0
    total_general_comision = 0
    
    #i=0
    #contador de filas
    c=1
    for i in range(len(cuotas)):
    #for i,cuota in enumerate(cuotas,start=1):
        #se suman los totales por fracion
        if (cuotas[i]['fraccion_id'] == fraccion_actual):
            c+=1
            total_importe += cuotas[i]['importe']
            total_comision += cuotas[i]['comision']
            
            sheet.write(c,0,str(cuotas[i]['cliente']))
            sheet.write(c,1,str(cuotas[i]['lote']))
            sheet.write(c,2,str(cuotas[i]['cuota_nro']))
            sheet.write(c,3,str(cuotas[i]['fecha_pago']))
            sheet.write(c,4,str(cuotas[i]['importe']))
            sheet.write(c,5,str(cuotas[i]['comision']))
            sheet.write(c,6,str(cuotas[i]['fraccion']))
            #print str(cuotas[i]['importe'])
            
            
            #... y acumulamos para los totales generales
            total_general_importe += cuotas[i]['importe']
            total_general_comision += cuotas[i]['comision'] 
             
           

        else: 
            c+=1
            sheet.write(c,0,"Totales de Fraccion",style2)
            sheet.write(c,4,total_importe)
            sheet.write(c,5,total_comision)
            
            c+=1
            sheet.write(c,0,str(cuotas[i]['cliente']))
            sheet.write(c,1,str(cuotas[i]['lote']))
            sheet.write(c,2,str(cuotas[i]['cuota_nro']))
            sheet.write(c,3,str(cuotas[i]['fecha_pago']))
            sheet.write(c,4,str(cuotas[i]['importe']))
            sheet.write(c,5,str(cuotas[i]['comision']))
            sheet.write(c,6,str(cuotas[i]['fraccion']))
            
            total_general_importe += cuotas[i]['importe']
            total_general_comision += cuotas[i]['comision'] 
            fraccion_actual = cuotas[i]['fraccion_id']
            total_importe = 0
            total_comision = 0
            
            total_importe += cuotas[i]['importe']
            total_comision += cuotas[i]['comision']
        #si es la ultima fila    
        if (i == len(cuotas)-1):   
            c+=1           
            sheet.write(c,0,"Totales de Fraccion", style2)
            sheet.write(c,4,total_importe,style2)
            sheet.write(c,5,total_comision,style2)
            
    c+=1
    sheet.write(c,0,"Totales del Vendedor",style2)
    sheet.write(c,4,total_general_importe,style2)
    sheet.write(c,5,total_general_comision,style2)
    
    
    wb.save('liquidacion_vendedores.xls')
#     response = HttpResponse(mimetype="application/ms-excel")
#     response['Content-Disposition'] = 'attachment; filename=%s' % fname
#     wb.save(response)
#     return response
#         
    
    
def reporte_liquidacion_gerentes(object_list):
    cuotas=object_list
    wb=xlwt.Workbook(encoding='utf-8')
    sheet=wb.add_sheet('test',cell_overwrite_ok=True)
    style=xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2=xlwt.easyxf('font: name Arial, bold True;')
    #cabeceras
    sheet.write(0,0,"Cliente",style)
    sheet.write(0,1,"Lote Nro.",style)    
    sheet.write(0,2,"Cuota Nro.",style)
    sheet.write(0,3,"Fecha de Pago",style)
    sheet.write(0,4,"Importe",style)
    sheet.write(0,5,"Comision",style)
    sheet.write(0,6,"Fraccion",style)
    #wb.save('informe_general.xls')
    #guardamos la primera fraccion para comparar
    fraccion_actual = cuotas[0]['fraccion_id']
    
    total_monto_pagado = 0
    total_monto_gerente = 0
    total_general_pagado = 0
    total_general_gerente = 0
    
    #i=0
    #contador de filas
    c=1
    for i in range(len(cuotas)):
    #for i,cuota in enumerate(cuotas,start=1):
        #se suman los totales por fracion
        if (cuotas[i]['fraccion_id'] == fraccion_actual):
            c+=1
            total_monto_pagado += cuotas[i]['monto_pagado']
            total_monto_gerente += cuotas[i]['monto_gerente']
                    
            
            sheet.write(c,0,str(cuotas[i]['fecha_pago']))
            sheet.write(c,1,str(cuotas[i]['lote']))
            sheet.write(c,2,str(cuotas[i]['cliente']))
            sheet.write(c,3,str(cuotas[i]['monto_pagado']))
            sheet.write(c,4,str(cuotas[i]['monto_gerente']))
            sheet.write(c,6,str(cuotas[i]['fraccion']))
            
            
            #... y acumulamos para los totales generales
            total_general_pagado += cuotas[i]['monto_pagado']
            total_general_gerente += cuotas[i]['monto_gerente'] 
             
           

        else: 
            c+=1
            sheet.write(c,0,"Totales de Fraccion",style2)
            sheet.write(c,4,total_monto_pagado)
            sheet.write(c,5,total_monto_gerente)
            
            c+=1
#             
            sheet.write(c,0,str(cuotas[i]['fecha_pago']))
            sheet.write(c,1,str(cuotas[i]['lote']))
            sheet.write(c,2,str(cuotas[i]['cliente']))
            sheet.write(c,3,str(cuotas[i]['monto_pagado']))
            sheet.write(c,4,str(cuotas[i]['monto_gerente']))
            sheet.write(c,6,str(cuotas[i]['fraccion']))
            
            total_general_pagado += cuotas[i]['monto_pagado']
            total_general_gerente += cuotas[i]['monto_gerente'] 
            fraccion_actual = cuotas[i]['fraccion_id']
            total_importe = 0
            total_comision = 0
            
            total_monto_pagado += cuotas[i]['monto_pagado']
            total_monto_gerente += cuotas[i]['monto_gerente']
        #si es la ultima fila    
        if (i == len(cuotas)-1):   
            c+=1           
            sheet.write(c,0,"Totales de Fraccion", style2)
            sheet.write(c,4,total_monto_pagado,style2)
            sheet.write(c,5,total_monto_gerente,style2)
            
    c+=1
    sheet.write(c,0,"Totales Generales",style2)
    sheet.write(c,4,total_general_pagado,style2)
    sheet.write(c,5,total_general_gerente,style2)
    
    
    wb.save('liquidacion_gerentes.xls')
#     response = HttpResponse(mimetype="application/ms-excel")
#     response['Content-Disposition'] = 'attachment; filename=%s' % fname
#     wb.save(response)
#     return response
#         
    
    
    
    
    