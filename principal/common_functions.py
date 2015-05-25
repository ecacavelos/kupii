from django.db.models import Count, Min, Sum, Avg
from principal.models import Lote, Cliente, Vendedor, PlanDePago, Fraccion, Manzana, Venta, Propietario, \
    PlanDePagoVendedor, PagoDeCuotas, RecuperacionDeLotes
from principal.monthdelta import MonthDelta
from calendar import monthrange
from datetime import datetime, timedelta
from django.core import serializers
import json
import math


def get_cuotas_detail_by_lote(lote_id):
    print("buscando pagos del lote --> " + lote_id);
    # El query es: select sum(nro_cuotas_a_pagar) from principal_pagodecuotas where lote_id = 16108;
    cant_cuotas_pagadas = PagoDeCuotas.objects.filter(lote=lote_id).aggregate(Sum('nro_cuotas_a_pagar'))
    ventas = Venta.objects.filter(lote_id=lote_id)
    for item_venta in ventas:
        print 'Obteniendo la ultima venta'
        try:
            RecuperacionDeLotes.objects.get(venta=item_venta.id)
        except RecuperacionDeLotes.DoesNotExist:
            print 'se encontro la venta no recuperada, la venta actual'
            venta = item_venta

    plan_de_pago = PlanDePago.objects.get(id=venta.plan_de_pago.id)
    # calcular la fecha de vencimiento.    
    if cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']:
        proximo_vencimiento = (
        venta.fecha_primer_vencimiento + MonthDelta(cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'])).strftime(
            '%d/%m/%Y')
    else:
        cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] = 1
        proximo_vencimiento = venta.fecha_primer_vencimiento.strftime('%d/%m/%Y')

    datos = dict([('cant_cuotas_pagadas', cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']),
                  ('cantidad_total_cuotas', plan_de_pago.cantidad_de_cuotas),
                  ('proximo_vencimiento', proximo_vencimiento)])
    return datos


def get_nro_cuota(pago):
    PagoDeCuotas(pago)
    pago_id = pago.id
    fecha_pago = pago.fecha_de_pago
    lote_id = pago.lote_id
    # fecha_fin=pago.fecha_de_pago
 
    cant_cuotas = PagoDeCuotas.objects.filter(lote_id=lote_id, pk__lt=pago_id).aggregate(Sum('nro_cuotas_a_pagar')).values()[0]    
    if cant_cuotas == None:
        cant_cuotas =0
    return cant_cuotas


def pagos_db_to_custom_pagos(lista_pagos_db):
    lista_custom = []
    for pago_db in lista_pagos_db:
        item = {}
        item['fecha'] = pago_db.fecha_de_pago
        lista_custom.append(item)
    return lista_custom

#Funcion que recibe una lista de objetos y una lista de labels,
#serializa la lista de objetos y retorna una lista de diccionarios
def custom_json(object_list, labels):
    try:
        data = serializers.serialize('python', object_list)
        results = []
        label1=labels[0]
        if len(labels) > 1:
            label2=labels[1]
          
        for d in data:
            d['fields']['id'] = d['pk']
            #Como maximo habra 2 labels
            if len(labels) <= 1:
                d['fields']['label'] = u'%s' % (d['fields'][label1])
            else:
                d['fields']['label'] = u'%s %s' % (d['fields'][label1],d['fields'][label2])
            results.append(d['fields'])
        return results
    except Exception, error:  
        print error
        return False

def monthdelta(d1, d2):
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta

def get_cuota_information_by_lote(lote_id,cuotas_pag):
                cant_cuotas_pag =0
                print("lote_id ->" + lote_id)
                cant_cuotas_pagadas = PagoDeCuotas.objects.filter(lote=lote_id).aggregate(Sum('nro_cuotas_a_pagar'))
                ventas = Venta.objects.filter(lote_id=lote_id)
                if cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] == None:
                    cant_cuotas_pag = 0
                else:
                    cant_cuotas_pag = cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']
                cuotas_totales=0
                for item_venta in ventas:
                    print 'Obteniendo la ultima venta'
                    try:
                        RecuperacionDeLotes.objects.get(venta=item_venta.id)
                    except RecuperacionDeLotes.DoesNotExist:
                        print 'se encontro la venta no recuperada, la venta actual'
                        venta = item_venta
                cuotas_totales = (cant_cuotas_pag)
                ultima_fecha_pago = ""
                if cuotas_totales != 0:
                    ultima_fecha_pago = (venta.fecha_primer_vencimiento + MonthDelta(cuotas_totales))
                else:
                    ultima_fecha_pago = venta.fecha_primer_vencimiento
                cuota_a_pagar= {}
                cuotas_a_pagar= []
                for i in range(0, int(cuotas_pag)):
                    nro_cuota = cuotas_totales + 1
                    cuota_a_pagar['nro_cuota'] = str(nro_cuota) + "/" + str(venta.plan_de_pago.cantidad_de_cuotas)
                    cuota_a_pagar['fecha'] = (ultima_fecha_pago + MonthDelta(i)).strftime('%d/%m/%Y')
                    cuotas_totales +=1
                    cuotas_a_pagar.append(cuota_a_pagar)
                    cuota_a_pagar= {}
                    
                return cuotas_a_pagar
            
def filtros_establecidos(request, tipo_informe):
    
    if tipo_informe == 'liquidacion_propietarios':        
        try:
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            tipo_busqueda=request['tipo_busqueda']
            return True
        except:
            print('Parametros no seteados')
            return False
    elif tipo_informe == 'clientes_atrasados':
            #Puede filtrar solo por meses de atraso o solo por fraccion o sin ningun filtro
            try:
                if request['fraccion'] == '' and request['meses_atraso'] == '':               
                    return 0
                elif request['fraccion'] != '' and request['meses_atraso'] == '':
                    fraccion = request['fraccion']
                    return 1
                elif request['fraccion'] == ''and request['meses_atraso'] != '':
                    meses_atraso = request['meses_atraso']
                    return 2
                else:
                    fraccion = request['fraccion']
                    meses_atraso = request['meses_atraso']
                    return 3
            except:
                print('Parametros no seteados')
                return 0
    elif tipo_informe == 'lotes_libres':
        try:
            fraccion_ini=request['fraccion_ini']
            fraccion_fin=request['fraccion_fin']
            return True
        except:
            print('Parametros no seteados')
            
    elif tipo_informe == 'informe_movimientos':
        try:
            lote_id=request['lote_id']
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            return True
        except:
            print('Parametros no seteados')
    elif tipo_informe == "informe_general":
        try:
            fraccion_ini=request['fraccion_ini']
            fraccion_fin=request['fraccion_fin']
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            return True
        except:
            print('Parametros no seteados')
    elif tipo_informe == "liquidacion_vendedores":
        try:
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            busqueda=request['busqueda']
            return True
        except:
            print('Parametros no seteados')      
    elif tipo_informe == "liquidacion_gerentes":
        try:
            fecha=request['fecha']
            return True
        except:
            print('Parametros no seteados')
    elif tipo_informe == "informe_ventas":
        try:
            lote=request['lote_id']
            return True
        except:
            print('Parametros no seteados')  
    elif tipo_informe == 'listado_clientes':
        try:
            tipo_busqueda=request['tipo_busqueda']
            busqueda_label=request['busqueda_label']
            return True
        except:
            print('Parametros no seteados')     
    return False



def obtener_detalle_interes_lote(lote_id,fecha_pago_parsed,proximo_vencimiento_parsed):
    
            resumen_lote=get_cuotas_detail_by_lote(str(lote_id))
            cuotas_pagadas=resumen_lote['cant_cuotas_pagadas']
            
            detalles=[]
            #El cliente tiene cuotas atrasadas
            if fecha_pago_parsed>proximo_vencimiento_parsed:
                
    #         TODO:
    #         Se calcula la diferencia en dias de la fecha del pago que se esta realizando, con 
    #         respecto a la fecha de vencimiento de dicho pago. El porcentaje de interes que se aplica
    #         sobre las cuotas es constante: 0.00067 (0.002/30) -> 2% interes mensual/30
    #         + interes punitorio (0.00020) + iva (0.00009)
    
                
                #Obtenemos la fecha del primer vencimiento de la cuota, de la ultima venta
                ventas = Venta.objects.filter(lote_id=lote_id)
                for item_venta in ventas:
                    print 'Obteniendo la ultima venta'
                    try: 
                        RecuperacionDeLotes.objects.get(venta=item_venta.id)
                    except RecuperacionDeLotes.DoesNotExist:
                        print 'se encontro la venta no recuperada, la venta actual'
                        venta = item_venta  
                
                
                #Calculamos en base al primer vencimiento, cuantas cuotas debieron haberse pagado hasta la fecha
                fecha_primer_vencimiento=venta.fecha_primer_vencimiento
                cantidad_ideal_cuotas=monthdelta(fecha_primer_vencimiento, fecha_pago_parsed)
                #Y obtenemos las cuotas atrasadas
                cuotas_atrasadas=cantidad_ideal_cuotas-cuotas_pagadas+1
                monto_cuota=venta.precio_de_cuota
                
                #Intereses (valores constantes)
                #Interes moratorio por dia
                interes=0.00067
                
                #Interes
                interes_punitorio=0.00020
                
                #Intereses IVA
                interes_iva=0.00009
                
                total_intereses=interes+interes_punitorio+interes_iva
                
                for cuota in range(cuotas_atrasadas):
                    detalle={}
                    fecha_vencimiento=proximo_vencimiento_parsed+MonthDelta(cuota)
                    dias_atraso=(fecha_pago_parsed-fecha_vencimiento).days                
                    intereses=math.ceil(total_intereses*dias_atraso*monto_cuota)
                    
                    detalle['interes']=interes
                    detalle['interes_punitorio']=interes_punitorio
                    detalle['interes_iva']=interes_iva
                    detalle['nro_cuota']=cuotas_pagadas+(cuota+1)
                    detalle['dias_atraso']=dias_atraso
                    detalle['intereses']=intereses
                    detalle['vencimiento']=fecha_vencimiento.strftime('%d/%m/%Y')
                    
                   
                    detalles.append(detalle)
            print detalles
            return detalles
        
        
def obtener_cuotas_a_pagar(venta,fecha_pago,resumen_cuotas_a_pagar):
    
    lista_cuotas = []

    if (datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date() < fecha_pago):
        print 'Hay al menos 1 cuota en mora'
        intereses = obtener_detalle_interes_lote(venta.lote.id,fecha_pago,datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date())
        interes_total = 0 
        for interes_item in intereses:
            interes_total+=interes_item['intereses']
        if len(intereses)<=5: # Hasta 5 cuotas
            for interes_item in intereses:
                cuota = {
                    'numero_cuota': interes_item['nro_cuota'],
                    'monto_cuota':venta.precio_de_cuota + interes_total, 
                    'vencimiento': interes_item['vencimiento'],
                    'fecha_pago' : fecha_pago.strftime("%d/%m/%Y")
                    }
            
                lista_cuotas.append(cuota)
            # Ademas de las cuotas con mora se agrega la cuota actual que es posible pagar
            vencimiento_cuota_acutal = datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date() + MonthDelta(len(intereses))
            cuota = {'numero_cuota': resumen_cuotas_a_pagar['cant_cuotas_pagadas'] + len(intereses) + 1 ,
                 'monto_cuota':venta.precio_de_cuota , 
                 'vencimiento': vencimiento_cuota_acutal.strftime("%d/%m/%Y"),
                 'fecha_pago' : fecha_pago.strftime("%d/%m/%Y")}
            lista_cuotas.append(cuota)
        else:    
            
            error_item = {}
            error_item['codigo'] = '33'
            error_item['mensaje'] = 'Compra con mas de 6 meses de atraso'
            error = {'error': error_item}            
            return error
    else:
        print 'Cliente esta al dia, solo debe abonar una cuota'
        cuota = {'numero_cuota': resumen_cuotas_a_pagar['cant_cuotas_pagadas'] + 1 ,
                 'monto_cuota':venta.precio_de_cuota , 
                 'vencimiento': resumen_cuotas_a_pagar['proximo_vencimiento'],
                 'fecha_pago' : fecha_pago.strftime("%d/%m/%Y")}
        lista_cuotas.append(cuota)
        
    return lista_cuotas
