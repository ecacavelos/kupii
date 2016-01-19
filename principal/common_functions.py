from django.db.models import Count, Min, Sum, Avg
from principal.models import Lote, Cliente, Vendedor, PlanDePago, Fraccion, Manzana, Venta, Propietario, \
    PlanDePagoVendedor, PagoDeCuotas, RecuperacionDeLotes, LogUsuario, CoordenadasFactura
from principal.monthdelta import MonthDelta
from calendar import monthrange
from datetime import datetime, timedelta
from django.core import serializers
from django.contrib.auth.models import User, Permission
from django.db.models import Q
import json
import math
import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.units import mm
from num2words import num2words
import xlwt
import math
import json

def get_cuotas_detail_by_lote(lote_id):
    print("buscando pagos del lote --> " + lote_id);
    # El query es: select sum(nro_cuotas_a_pagar) from principal_pagodecuotas where lote_id = 16108;
    venta = get_ultima_venta(lote_id)
    # ventas = Venta.objects.filter(lote_id=lote_id)
    # for item_venta in ventas:
    #     print 'Obteniendo la ultima venta'
    #     try:
    #         RecuperacionDeLotes.objects.get(venta=item_venta.id)
    #     except RecuperacionDeLotes.DoesNotExist:
    #         print 'se encontro la venta no recuperada, la venta actual'
    #         venta = item_venta
    cant_cuotas_pagadas = PagoDeCuotas.objects.filter(venta=venta).aggregate(Sum('nro_cuotas_a_pagar'))
    plan_de_pago = PlanDePago.objects.get(id=venta.plan_de_pago.id)
    # calcular la fecha de vencimiento.    
    if cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']:
        proximo_vencimiento = (
        venta.fecha_primer_vencimiento + MonthDelta(cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'])).strftime(
            '%d/%m/%Y')
    else:
        #cuando no se encuentran cuotas pagadas trae None, seteamos la cantidad de cuotas pagadas a 0
        #porque la venta es independiente a los pagos de cuotas
        #cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] = 1

        cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] = 0
        proximo_vencimiento = venta.fecha_primer_vencimiento.strftime('%d/%m/%Y')

    datos = dict([('cant_cuotas_pagadas', cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']),
                  ('cantidad_total_cuotas', plan_de_pago.cantidad_de_cuotas),
                  ('proximo_vencimiento', proximo_vencimiento)])
    return datos

def loggear_accion(usuario, accion, tipo_objeto, id_objeto, codigo_lote = ''):
    log = LogUsuario()
    log.fecha_hora= datetime.datetime.now()
    log.usuario = usuario
    log.accion = accion
    log.tipo_objeto = tipo_objeto
    log.id_objeto = id_objeto
    log.codigo_lote = codigo_lote
    log.save()

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

def get_cuota_information_by_lote(lote_id,cuotas_pag, facturar = False, ver_vencimientos = False, venta_param = None):
    cant_cuotas_pag =0
    cant_cuotas_pagadas = {}
    #print("lote_id ->" + unicode(lote_id))
    # for item_venta in ventas:
    #     print 'Obteniendo la ultima venta'
    #     try:
    #         RecuperacionDeLotes.objects.get(venta=item_venta.id)
    #     except RecuperacionDeLotes.DoesNotExist:
    #         print 'se encontro la venta no recuperada, la venta actual'
    #         venta = item_venta
    if venta_param == None:
        venta = get_ultima_venta(lote_id) 
    else:
        venta = venta_param
    
    if ver_vencimientos == True:
        cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] = 0
    else:
        cant_cuotas_pagadas = PagoDeCuotas.objects.filter(venta=venta).aggregate(Sum('nro_cuotas_a_pagar'))
    
    #ventas = Venta.objects.filter(lote_id=lote_id)
    if cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] == None:
        cant_cuotas_pag = 0
    else:
        if facturar == False:
            cant_cuotas_pag = cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']
        else:
            cant_cuotas_pag = cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] - cuotas_pag
            
        if ver_vencimientos == True:
            cant_cuotas_pag = cuotas_pag -1
    
    cuotas_totales=0
    cuota_a_pagar= {}
    cuotas_a_pagar= []
    ultima_fecha_pago = ""
    cuotas_totales = (cant_cuotas_pag)
    if cuotas_totales != 0:
        ultima_fecha_pago = (venta.fecha_primer_vencimiento + MonthDelta(cuotas_totales))
    else:
        ultima_fecha_pago = venta.fecha_primer_vencimiento

    if cant_cuotas_pag == venta.plan_de_pago.cantidad_de_cuotas or venta.plan_de_pago.tipo_de_plan == 'contado':
        if venta.plan_de_pago.tipo_de_plan == 'contado':
            cuota_a_pagar['contado'] = True
            cuotas_a_pagar.append(cuota_a_pagar)
        else:
            cuota_a_pagar['pago_cancelado'] = True
            cuotas_a_pagar.append(cuota_a_pagar)
        return cuotas_a_pagar

    #Verificar si el plan tiene cuotas de refuerzo 
    if venta.plan_de_pago.cuotas_de_refuerzo != 0:
        pagos = get_pago_cuotas(venta, None,None)
        cantidad_cuotas_ref_pagadas = cant_cuotas_pagadas_ref(pagos)
        for i in range(0, int(cuotas_pag)):
            nro_cuota = cuotas_totales + 1
            cuota_a_pagar['nro_cuota'] = unicode(nro_cuota) + "/" + unicode(venta.plan_de_pago.cantidad_de_cuotas)
            cuotas_totales +=1
            cuota_a_pagar['fecha'] = (ultima_fecha_pago + MonthDelta(i)).strftime('%d/%m/%Y')
            if (nro_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 and cantidad_cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                cuota_a_pagar['monto_cuota'] = venta.monto_cuota_refuerzo
                cantidad_cuotas_ref_pagadas +=1
            else:
                cuota_a_pagar['monto_cuota'] = venta.precio_de_cuota
            cuotas_a_pagar.append(cuota_a_pagar)
            cuota_a_pagar= {}
    else:    
        for i in range(0, int(cuotas_pag)):
            nro_cuota = cuotas_totales + 1
            cuota_a_pagar['nro_cuota'] = unicode(nro_cuota) + "/" + unicode(venta.plan_de_pago.cantidad_de_cuotas)
            cuota_a_pagar['fecha'] = (ultima_fecha_pago + MonthDelta(i)).strftime('%d/%m/%Y')
            cuota_a_pagar['monto_cuota'] = venta.precio_de_cuota
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
    elif tipo_informe == 'informe_facturacion':        
        try:
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
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
            lote_ini=request['lote_ini']
            lote_fin=request['lote_fin']
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
            lote=request['busqueda']
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


def obtener_dias_atraso (fecha_pago_parsed, fecha_vencimiento_parsed):
    if fecha_pago_parsed > fecha_vencimiento_parsed:
        diferencia = fecha_pago_parsed - fecha_vencimiento_parsed
        dias_atraso = diferencia.days
    else:
        dias_atraso = 0
    return dias_atraso

def obtener_detalle_interes_lote(lote_id,fecha_pago_parsed,proximo_vencimiento_parsed, nro_cuotas_a_pagar):
    
            resumen_lote=get_cuotas_detail_by_lote(unicode(lote_id))
            cuotas_pagadas=resumen_lote['cant_cuotas_pagadas']
            
            detalles=[]
            sumatoria_intereses = 0
            #El cliente tiene cuotas atrasadas
            if fecha_pago_parsed>proximo_vencimiento_parsed:
                
    #         TODO:
    #         Se calcula la diferencia en dias de la fecha del pago que se esta realizando, con 
    #         respecto a la fecha de vencimiento de dicho pago. El porcentaje de interes que se aplica
    #         sobre las cuotas es constante: 0.001 (0.03/30) -> 3% interes mensual/30
    #         + interes punitorio (0.00030) + iva = (interes mensual + interes punitorio)* (10%)=(0.00013)

                venta = get_ultima_venta(lote_id)

                #Calculamos en base al primer vencimiento, cuantas cuotas debieron haberse pagado hasta la fecha
                fecha_primer_vencimiento=venta.fecha_primer_vencimiento
                cantidad_ideal_cuotas=monthdelta(fecha_primer_vencimiento, fecha_pago_parsed) +1
                        #cantidad_ideal_cuotas=monthdelta(fecha_primer_vencimiento, fecha_pago_parsed) +1
                #Y obtenemos las cuotas atrasadas
                cuotas_atrasadas=cantidad_ideal_cuotas-cuotas_pagadas
                
                if cuotas_atrasadas == 0:
                    fecha_proximo_vencimiento_dias = proximo_vencimiento_parsed
                    fecha_pago_dias = fecha_pago_parsed
                    dias_atraso = fecha_pago_dias - fecha_proximo_vencimiento_dias
                    if dias_atraso.days > 5:
                        cuotas_atrasadas = 1
                
                monto_cuota=venta.precio_de_cuota
                
                #Intereses (valores constantes)
                #Interes moratorio por dia
                interes=0.001
                
                #Interes
                #interes_punitorio=0.00030
                
                #Intereses IVA
                #interes_iva=0.00013
                interes_iva=0.0001
                #total_intereses=interes+interes_punitorio+interes_iva
                total_intereses=interes+interes_iva
                #Verificar si tiene cuotas de refuerzo
                if venta.plan_de_pago.cuotas_de_refuerzo != 0:
                    pagos = get_pago_cuotas(venta, None, None)
                    cantidad_pagos_ref = cant_cuotas_pagadas_ref(pagos)
                    es_ref= True    
                else:
                    cantidad_pagos_ref = 0
                    es_ref= False
                    
                if int(nro_cuotas_a_pagar) < int(cuotas_atrasadas):
                    rango = int(nro_cuotas_a_pagar)
                else:
                    rango = int(cuotas_atrasadas)
                    
                for cuota in range(rango):
                    detalle={}
                    fecha_vencimiento=proximo_vencimiento_parsed+MonthDelta(cuota)
                    dias_atraso=(fecha_pago_parsed-fecha_vencimiento).days
                    nro_cuota = cuotas_pagadas+(cuota+1)
                    if es_ref == True:
                        if (nro_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 and cantidad_pagos_ref < venta.plan_de_pago.cuotas_de_refuerzo:
                            monto_cuota = venta.monto_cuota_refuerzo
                            cantidad_pagos_ref += 1
                        else:
                            monto_cuota=venta.precio_de_cuota
                    else:
                        monto_cuota=venta.precio_de_cuota             
                    intereses=math.ceil(total_intereses*dias_atraso*monto_cuota)
                    redondeado=roundup(intereses)
                    detalle['interes']=interes
                    #detalle['interes_punitorio']=interes_punitorio
                    detalle['interes_iva']=interes_iva
                    detalle['nro_cuota']=nro_cuota
                    detalle['dias_atraso']=dias_atraso
                    detalle['intereses']=redondeado
                    detalle['vencimiento']=fecha_vencimiento.strftime('%d/%m/%Y')
                    detalle['tipo']='normal';

                    sumatoria_intereses += redondeado

                    fecha_ultimo_vencimiento = datetime.datetime.strptime(detalle['vencimiento'], "%d/%m/%Y").date()
                    fecha_dias_gracia = fecha_ultimo_vencimiento + datetime.timedelta(days=5)
                    dias_habiles = calcular_dias_habiles(fecha_ultimo_vencimiento,fecha_dias_gracia)

                    if dias_habiles<5:
                        fecha_ultimo_vencimiento = fecha_dias_gracia+datetime.timedelta(days=5-dias_habiles)
                    detalle['vencimiento_gracia']=fecha_ultimo_vencimiento.strftime('%d/%m/%Y')

                    detalles.append(detalle)

                #Calculamos en base al primer vencimiento, cuantas cuotas debieron haberse pagado hasta la fecha
                #fecha_vencimiento_mes_pago = fecha_primer_vencimiento + MonthDelta(+cantidad_ideal_cuotas)
                #fecha_dias_gracia = fecha_vencimiento_mes_pago + datetime.timedelta(days=5)
                #dias_habiles = calcular_dias_habiles(fecha_vencimiento_mes_pago,fecha_dias_gracia)
                #if dias_habiles<5:
                #    fecha_vencimiento_mes_pago = fecha_dias_gracia+datetime.timedelta(days=5-dias_habiles)
                #cantidad_ideal_cuotas=monthdelta(fecha_primer_vencimiento, fecha_vencimiento_mes_pago)
                #cuotas_atrasadas=cantidad_ideal_cuotas-cuotas_pagadas
                
                if cuotas_atrasadas>=6:
                    #gestion_cobranza = int(0.1*(math.ceil(float(cuotas_atrasadas*monto_cuota))+sumatoria_intereses))
                    gestion_cobranza = roundup(0.05*((cuotas_atrasadas*monto_cuota)+sumatoria_intereses) + (0.05*((cuotas_atrasadas*monto_cuota)+sumatoria_intereses))*0.10)
                    detalles.append({'gestion_cobranza':gestion_cobranza, 'tipo': 'gestion_cobranza'})
                    
            print detalles
            return detalles
        
        
def obtener_cuotas_a_pagar(venta,fecha_pago,resumen_cuotas_a_pagar):
    
    lista_cuotas = []
    cantidad_cuotas = 0
    sumatoria_cuotas = 0 
    if (datetime.datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date() < fecha_pago):
        print 'Hay al menos 1 cuota en mora'
        try:
            #Calculamos en base al primer vencimiento, cuantas cuotas debieron haberse pagado hasta la fecha
            fecha_primer_vencimiento=venta.fecha_primer_vencimiento
            cantidad_ideal_cuotas=monthdelta(fecha_primer_vencimiento, fecha_pago)
            #Y obtenemos las cuotas atrasadas
            cuotas_atrasadas=cantidad_ideal_cuotas-int(resumen_cuotas_a_pagar['cant_cuotas_pagadas'])
            intereses = obtener_detalle_interes_lote(venta.lote.id,fecha_pago,datetime.datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date(),cuotas_atrasadas)
        except Exception, error:
            print error
        interes_total = 0
        if len(intereses)<=5: # Hasta 5 cuotas
            for interes_item in intereses:
                if interes_item['tipo'] == 'normal':
                    cantidad_cuotas = cantidad_cuotas+1
                    interes_total+=interes_item['intereses']
                    sumatoria_cuotas = sumatoria_cuotas + venta.precio_de_cuota + interes_total
                    cuota = {
                        'cantidad_sumatoria_cuotas': cantidad_cuotas,
                        'numero_cuota': interes_item['nro_cuota'],
                        'monto_cuota':venta.precio_de_cuota,
                        'interes': interes_item['intereses'],
                        'interes_total': interes_total,
                        'monto_total_a_pagar': venta.precio_de_cuota +  interes_total, 
                        'vencimiento': interes_item['vencimiento'],
                        'fecha_pago' : fecha_pago.strftime("%d/%m/%Y"),
                        'monto_sumatoria_cuotas': sumatoria_cuotas
                        }
            
                lista_cuotas.append(cuota)
            # Ademas de las cuotas con mora se agrega la cuota actual que es posible pagar
            vencimiento_cuota_acutal = datetime.datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date() + MonthDelta(len(intereses))
            cuota = {
                 'cantidad_sumatoria_cuotas': cantidad_cuotas+1,
                 'numero_cuota': resumen_cuotas_a_pagar['cant_cuotas_pagadas'] + len(intereses) + 1 ,
                 'monto_cuota':venta.precio_de_cuota,
                 'interes': 0,
                 'interes_total': 0,
                 'monto_total_a_pagar': venta.precio_de_cuota,  
                 'vencimiento': vencimiento_cuota_acutal.strftime("%d/%m/%Y"),
                 'fecha_pago' : fecha_pago.strftime("%d/%m/%Y"),
                 'monto_sumatoria_cuotas': sumatoria_cuotas+venta.precio_de_cuota
                 }
            lista_cuotas.append(cuota)
        else:    
            
            error_item = {}
            error_item['codigo'] = '33'
            error_item['mensaje'] = 'Compra con mas de 6 meses de atraso'
            error = {'error': error_item}            
            return error
    else:
        print 'Cliente esta al dia, solo debe abonar una cuota'
        cuota = {'cantidad_sumatoria_cuotas': cantidad_cuotas,
                 'numero_cuota': resumen_cuotas_a_pagar['cant_cuotas_pagadas'] + 1 ,
                 'monto_cuota':venta.precio_de_cuota,
                 'interes': 0,
                 'interes_total': 0,
                 'monto_total_a_pagar': venta.precio_de_cuota,   
                 'vencimiento': resumen_cuotas_a_pagar['proximo_vencimiento'],
                 'fecha_pago' : fecha_pago.strftime("%d/%m/%Y"),
                 'monto_sumatoria_cuotas': sumatoria_cuotas+venta.precio_de_cuota
                 }
        lista_cuotas.append(cuota)
        
    return lista_cuotas

def verificar_permisos(user_id, permiso):
    """
    Metodo que comprueba que un usuario determinado tenga permisos sobre esa vista
    @return: True, False
    @rtype: Boolean
    """
    
    print("Id_user->" + unicode(user_id))
    print("Permiso->" + unicode(permiso))
    ok = False
    user = None
    permi = 'principal.' + permiso
    user = User.objects.get(id=user_id)
    perm = user.has_perm(permi)
    if perm == True:
        print("El usuario si posee ese permiso")
        ok = True
    else:
        print("El usuario no posee ese permiso")
        ok = False
    return ok

def get_pago_cuotas(venta, fecha_ini,fecha_fin, pagos = None, pagos_anteriores = None):
    cantidad_pagos_anteriores=0
    if fecha_ini == None and fecha_fin == None:
        #Se traen todos los pagos
        if pagos == None:
            pagos = PagoDeCuotas.objects.filter(venta_id=venta.id).order_by('id')
        
    else:
        #Primero se cuenta cuantos son los pagos anteriores y despues se filtra
        if pagos_anteriores == None:
            cantidad_pagos_anteriores = PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__lt=fecha_ini).aggregate(Sum('nro_cuotas_a_pagar')).values()[0]
        else:
            for pago in pagos_anteriores:
                if pago['venta_id'] == venta.id:
                    cantidad_pagos_anteriores = pago['nro_cuotas_a_pagar__sum']
                    break
                    
        if pagos == None:
            pagos = PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__range=(fecha_ini, fecha_fin)).order_by('fecha_de_pago')
          
        if cantidad_pagos_anteriores == None:
            cantidad_pagos_anteriores = 0
            
    cuotas_ref_pagadas =0;
    numero_cuota=cantidad_pagos_anteriores +1
    ventas_pagos_list = []
    esRefuerzo = False
    if venta.plan_de_pago.cuotas_de_refuerzo != 0:
        for pago in pagos:
            if pago.venta == venta:
                if (numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                        monto_cuota = venta.monto_cuota_refuerzo
                        cuotas_ref_pagadas +=1
                        esRefuerzo =True
                else:
                    monto_cuota = venta.precio_de_cuota
                    esRefuerzo = False
                if pago.nro_cuotas_a_pagar > 1:
                    for x in xrange(1,pago.nro_cuotas_a_pagar + 1):
                        if (numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                            monto_cuota = venta.monto_cuota_refuerzo
                            cuotas_ref_pagadas +=1
                            esRefuerzo =True
                        else:
                            monto_cuota = venta.precio_de_cuota
                            esRefuerzo = False                                  
                        cuota ={}
                        cuota['fecha_de_pago'] = pago.fecha_de_pago
                        cuota['id'] = pago.id
                        cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                        cuota['nro_cuota'] = unicode(numero_cuota)
                        cuota['monto'] = unicode(monto_cuota)
                        cuota['refuerzo'] = esRefuerzo
                        cuota['lote'] = pago.lote
                        cuota['fraccion'] = dict(pago.lote.manzana.fraccion)
                        ventas_pagos_list.append(cuota)
                        numero_cuota +=1
                else:
                    cuota ={}
                    cuota['fecha_de_pago'] = pago.fecha_de_pago
                    cuota['id'] = pago.id
                    cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                    cuota['nro_cuota'] = unicode(numero_cuota)
                    cuota['monto'] = unicode(monto_cuota)
                    cuota['refuerzo'] = esRefuerzo
                    cuota['lote'] = pago.lote
                    cuota['fraccion'] = pago.lote.manzana.fraccion
                    ventas_pagos_list.append(cuota)
                    numero_cuota +=1
    else:
        monto_cuota = venta.precio_de_cuota
        for pago in pagos:
            if pago.venta == venta:
                if pago.nro_cuotas_a_pagar > 1:
                    for x in xrange(1,pago.nro_cuotas_a_pagar + 1):                                  
                        cuota ={}
                        cuota['fecha_de_pago'] = pago.fecha_de_pago
                        cuota['id'] = pago.id
                        cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                        cuota['nro_cuota'] = unicode(numero_cuota)
                        cuota['monto'] = unicode(monto_cuota)
                        cuota['refuerzo'] = esRefuerzo
                        cuota['lote'] = pago.lote
                        cuota['fraccion'] = pago.lote.manzana.fraccion                    
                        ventas_pagos_list.append(cuota)
                        numero_cuota +=1
                else:
                    cuota ={}
                    cuota['fecha_de_pago'] = pago.fecha_de_pago
                    cuota['id'] = pago.id
                    cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                    cuota['nro_cuota'] = unicode(numero_cuota)
                    cuota['monto'] = unicode(monto_cuota)
                    cuota['refuerzo'] = esRefuerzo
                    cuota['lote'] = pago.lote
                    cuota['fraccion'] = pago.lote.manzana.fraccion
                    ventas_pagos_list.append(cuota)
                    numero_cuota +=1
    return ventas_pagos_list

def get_pago_cuotas_2(venta, fecha_ini,fecha_fin):
    if fecha_ini == None and fecha_fin == None:
        #Se traen todos los pagos
        pagos = PagoDeCuotas.objects.filter(venta_id=venta.id).order_by('fecha_de_pago')
        cantidad_pagos_anteriores=0
    else:
        #Primero se cuenta cuantos son los pagos anteriores y despues se filtra
        cantidad_pagos_anteriores = PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__lt=fecha_ini).aggregate(Sum('nro_cuotas_a_pagar')).values()[0]
        pagos = PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__range=(fecha_ini, fecha_fin)).order_by('fecha_de_pago')
        if cantidad_pagos_anteriores == None:
            cantidad_pagos_anteriores = 0
            
    cuotas_ref_pagadas =0;
    numero_cuota=cantidad_pagos_anteriores +1
    ventas_pagos_list = []
    esRefuerzo = False
    if venta.plan_de_pago.cuotas_de_refuerzo != 0:
        for pago in pagos:
            if (numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                    monto_cuota = venta.monto_cuota_refuerzo
                    cuotas_ref_pagadas +=1
                    esRefuerzo =True
            else:
                monto_cuota = venta.precio_de_cuota
                esRefuerzo = False
            if pago.nro_cuotas_a_pagar > 1:
                for x in xrange(1,pago.nro_cuotas_a_pagar + 1):
                    if (numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                        monto_cuota = venta.monto_cuota_refuerzo
                        cuotas_ref_pagadas +=1
                        esRefuerzo =True
                    else:
                        monto_cuota = venta.precio_de_cuota
                        esRefuerzo = False                                  
                    cuota ={}
                    cuota['fecha_de_pago'] = pago.fecha_de_pago
                    cuota['id'] = pago.id
                    cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                    cuota['nro_cuota'] = unicode(numero_cuota)
                    cuota['monto'] = unicode(monto_cuota)
                    cuota['refuerzo'] = esRefuerzo
                    cuota['lote'] = pago.lote
                    #cuota['fraccion'] = dict(pago.lote.manzana.fraccion)
                    ventas_pagos_list.append(cuota)
                    numero_cuota +=1
            else:
                cuota ={}
                cuota['fecha_de_pago'] = pago.fecha_de_pago
                cuota['id'] = pago.id
                cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                cuota['nro_cuota'] = unicode(numero_cuota)
                cuota['monto'] = unicode(monto_cuota)
                cuota['refuerzo'] = esRefuerzo
                cuota['lote'] = pago.lote
                #cuota['fraccion'] = pago.lote.manzana.fraccion
                ventas_pagos_list.append(cuota)
                numero_cuota +=1
    else:
        monto_cuota = venta.precio_de_cuota
        for pago in pagos:
            if pago.nro_cuotas_a_pagar > 1:
                for x in xrange(1,pago.nro_cuotas_a_pagar + 1):                                  
                    cuota ={}
                    cuota['fecha_de_pago'] = pago.fecha_de_pago
                    cuota['id'] = pago.id
                    cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                    cuota['nro_cuota'] = unicode(numero_cuota)
                    cuota['monto'] = unicode(monto_cuota)
                    cuota['refuerzo'] = esRefuerzo
                    cuota['lote'] = pago.lote
                    #cuota['fraccion'] = pago.lote.manzana.fraccion                    
                    ventas_pagos_list.append(cuota)
                    numero_cuota +=1
            else:
                cuota ={}
                cuota['fecha_de_pago'] = pago.fecha_de_pago
                cuota['id'] = pago.id
                cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                cuota['nro_cuota'] = unicode(numero_cuota)
                cuota['monto'] = unicode(monto_cuota)
                cuota['refuerzo'] = esRefuerzo
                cuota['lote'] = pago.lote
                #cuota['fraccion'] = pago.lote.manzana.fraccion
                ventas_pagos_list.append(cuota)
                numero_cuota +=1
    return ventas_pagos_list


def get_pago_cuotas_3(venta, fecha_ini,fecha_fin):
    if fecha_ini == None and fecha_fin == None:
        #Se traen todos los pagos
        pagos = PagoDeCuotas.objects.filter(venta_id=venta.id).order_by('fecha_de_pago')
        cantidad_pagos_anteriores=0
    else:
        #Primero se cuenta cuantos son los pagos anteriores y despues se filtra
        cantidad_pagos_anteriores = PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__lt=fecha_ini).aggregate(Sum('nro_cuotas_a_pagar')).values()[0]
        pagos = PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__range=(fecha_ini, fecha_fin)).order_by('fecha_de_pago')
        if cantidad_pagos_anteriores == None:
            cantidad_pagos_anteriores = 0
            
    cuotas_ref_pagadas =0;
    numero_cuota=cantidad_pagos_anteriores +1
    ventas_pagos_list = []
    esRefuerzo = False
    if venta.plan_de_pago.cuotas_de_refuerzo != 0:
        for pago in pagos:
            if (numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                    monto_cuota = venta.monto_cuota_refuerzo
                    cuotas_ref_pagadas +=1
                    esRefuerzo =True
            else:
                monto_cuota = venta.precio_de_cuota
                esRefuerzo = False
            if pago.nro_cuotas_a_pagar > 1:
                for x in xrange(1,pago.nro_cuotas_a_pagar + 1):
                    if (numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                        monto_cuota = venta.monto_cuota_refuerzo
                        cuotas_ref_pagadas +=1
                        esRefuerzo =True
                    else:
                        monto_cuota = venta.precio_de_cuota
                        esRefuerzo = False                                  
                    cuota ={}
                    cuota['fecha_de_pago'] = pago.fecha_de_pago
                    cuota['id'] = pago.id
                    cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                    cuota['nro_cuota'] = unicode(numero_cuota)
                    cuota['monto'] = unicode(monto_cuota)
                    cuota['refuerzo'] = esRefuerzo
                    #cuota['lote'] = pago.lote
                    #cuota['fraccion'] = dict(pago.lote.manzana.fraccion)
                    ventas_pagos_list.append(cuota)
                    numero_cuota +=1
            else:
                cuota ={}
                cuota['fecha_de_pago'] = pago.fecha_de_pago
                cuota['id'] = pago.id
                cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                cuota['nro_cuota'] = unicode(numero_cuota)
                cuota['monto'] = unicode(monto_cuota)
                cuota['refuerzo'] = esRefuerzo
                #cuota['lote'] = pago.lote
                #cuota['fraccion'] = pago.lote.manzana.fraccion
                ventas_pagos_list.append(cuota)
                numero_cuota +=1
    else:
        monto_cuota = venta.precio_de_cuota
        for pago in pagos:
            if pago.nro_cuotas_a_pagar > 1:
                for x in xrange(1,pago.nro_cuotas_a_pagar + 1):                                  
                    cuota ={}
                    cuota['fecha_de_pago'] = pago.fecha_de_pago
                    cuota['id'] = pago.id
                    cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                    cuota['nro_cuota'] = unicode(numero_cuota)
                    cuota['monto'] = unicode(monto_cuota)
                    cuota['refuerzo'] = esRefuerzo
                    #cuota['lote'] = pago.lote
                    #cuota['fraccion'] = pago.lote.manzana.fraccion                    
                    ventas_pagos_list.append(cuota)
                    numero_cuota +=1
            else:
                cuota ={}
                cuota['fecha_de_pago'] = pago.fecha_de_pago
                cuota['id'] = pago.id
                cuota['nro_cuota_y_total'] = unicode(numero_cuota) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                cuota['nro_cuota'] = unicode(numero_cuota)
                cuota['monto'] = unicode(monto_cuota)
                cuota['refuerzo'] = esRefuerzo
                #cuota['lote'] = pago.lote
                #cuota['fraccion'] = pago.lote.manzana.fraccion
                ventas_pagos_list.append(cuota)
                numero_cuota +=1
    return ventas_pagos_list



def cant_cuotas_pagadas_ref(pagos):
    cuotas_ref_pagadas=0
    for pago in pagos:
        if pago['refuerzo'] ==True:
            cuotas_ref_pagadas +=1
    return cuotas_ref_pagadas

def calcular_dias_habiles(fecha_ini, fecha_fin):
    start = fecha_ini
    end = fecha_fin

    daydiff = end.weekday() - start.weekday()


    #Verificamos cuantos dias habiles hay entre la fecha del ultimo vencimiento
    #y esa misma fecha + 5 dias de gracia
    days = ((end-start).days - daydiff) / 7 * 5 + min(daydiff,5) - (max(end.weekday() - 4, 0) % 5)

    return days
    
    
def roundup(interes):
    #return int(math.ceil(interes / 1000.0)) * 1000
    
    ##### Caso redondeado de a 500  ######
    number = interes / 1000.0
     
    miles = int(number)*1000
     
    centenas = str(number-int(number))[2:]
     
    centenas = int (centenas)
    
    if centenas > 10:
        if centenas >= 500:
            miles = miles +1000
            centenas = 0
        elif centenas < 500 and centenas < 50:
            centenas = 0
        elif centenas < 500 and centenas > 50 and centenas < 100:
            miles = miles +1000
            centenas = 0
        else:
            centenas = 0
        #elif centenas == 500:
            #centenas = 500
        
    else:
        if centenas >= 5:
            miles = miles + 1000
            centenas = 0
        elif centenas < 5:
            centenas = 0
        #elif centenas == 5:
            #centenas = 500
     
    decenas = 0 
     
    resultado = miles+centenas+ decenas
     
    return resultado

####### Caso redondeado de a 100  #########
#     #return int(math.ceil(interes / 1000.0)) * 1000
#     number = interes / 1000.0
#     
#     miles = int(number)*1000
#     
#     centenas = str(number-int(number))[2:]
#     
#     decenas = int(centenas)%100
#     
#     centenas = (int (centenas)/100)*100
#     
#     if decenas > 10:
#         if decenas >50:
#             centenas= centenas +100
#             decenas = 0
#         elif decenas < 50:
#             decenas = 0
#         elif decenas == 50:
#             decenas = 50
#     else:
#         if decenas > 5:
#             centenas= centenas +100
#             decenas = 0
#         elif decenas < 5:
#             decenas = 0
#         elif decenas == 5:
#             decenas = 50 
#     
#     resultado = miles+centenas+ decenas
#     
#     return resultado

#Funcion que encuentra todas las ventas de un lote y retorna la ultima
def get_ultima_venta(lote_id):
    ventas = Venta.objects.filter(lote_id=lote_id).order_by('fecha_de_venta')
    for item_venta in ventas:
        print 'Obteniendo la ultima venta'
        try:
            venta_recuperada = RecuperacionDeLotes.objects.get(venta=item_venta.id)
            venta = item_venta 
        except RecuperacionDeLotes.DoesNotExist:
            print 'se encontro la venta no recuperada, la venta actual'
            venta = item_venta

    return venta

def crear_pdf_factura(nueva_factura, request, manzana, lote_id, usuario):
    response = HttpResponse(content_type='application/pdf')
    nombre_factura = "factura-" + nueva_factura.numero + ".pdf"
    response['Content-Disposition'] = 'attachment; filename=factura' + str(nueva_factura.id) + '.pdf'
    p = canvas.Canvas(response)
    p.setPageSize((210 * mm, 297 * mm))
    p.setFont("Helvetica", 7)

    
    #Obtener las coordenadas de impresion de la factura
    try:
        coor = CoordenadasFactura.objects.get(usuario = usuario)    
    except Exception, error:
        coor = CoordenadasFactura.objects.get(usuario_id = 2)
    
            
    # INICIO PRIMERA IMPRESION
    y_1ra_imp = float(14.05)
    
    p.drawString(coor.numero_1x * cm, float(coor.numero_1y) * cm, unicode(nueva_factura.numero))
    
    p.drawString(coor.fecha_1x * cm, float(coor.fecha_1y) * cm, unicode(request.POST.get('fecha', '')))
    if nueva_factura.tipo == 'co':
        p.drawString(coor.contado_1x * cm, float(coor.contado_1y) * cm, "X")
    else:
        p.drawString(coor.credito_1x * cm, float(coor.credito_1y) * cm, "X")
            
    p.drawString(coor.fraccion_1x * cm, float(coor.fraccion_1y) * cm, unicode(manzana.fraccion.nombre))
            # Solo se imprime el primer nombre y apellido-- Faltaaa
    nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
    p.drawString(coor.nombre_1x * cm, float(coor.nombre_1y) * cm, unicode(nombre_ape))
    p.drawString(coor.manzana_1x * cm, float(coor.manzana_1y) * cm, unicode(manzana.nro_manzana))
    p.drawString(coor.lote_1x * cm, float(coor.lote_1y) * cm, unicode(lote_id.nro_lote))
            
            
    if nueva_factura.cliente.ruc == None:
        nueva_factura.cliente.ruc = ""                
    p.drawString(coor.ruc_1x * cm, float(coor.ruc_1y) * cm, unicode(nueva_factura.cliente.ruc))
    p.drawString(coor.telefono_1x * cm, float(coor.telefono_1y) * cm, unicode(nueva_factura.cliente.telefono_laboral))
    direccion_1_str = (nueva_factura.cliente.direccion_cobro[:56] + '..') if len(nueva_factura.cliente.direccion_cobro) > 56 else nueva_factura.cliente.direccion_cobro        
    p.drawString(coor.direccion_1x * cm, float(coor.direccion_1y) * cm, unicode(direccion_1_str))
    p.drawString(coor.superficie_1x * cm, float(coor.superficie_1y) * cm, unicode(lote_id.superficie) + "  mts2")
    p.drawString(coor.cta_cte_ctral_1x * cm, float(coor.cta_cte_ctral_1y) * cm, unicode(lote_id.cuenta_corriente_catastral))
            
    # Se obtienen la lista de los detalles
    lista_detalles = json.loads(nueva_factura.detalle)
    detalles = []
    pos_y = float(coor.cantidad_1y+ 0.5)
    exentas = 0
    iva10 = 0
    iva5 = 0
    total_iva_10 = 0
    total_iva_5 = 0
    total_iva = 0           
    total_gral = 0
    total_venta = 0
    for key, value in sorted(lista_detalles.iteritems()):
        detalle = {}
        detalle['item'] = key
        detalle['cantidad'] = value['cantidad']
        p.drawString(coor.cantidad_1x * cm, float(pos_y - 0.5) * cm, unicode(detalle['cantidad']))
        detalle['concepto'] = value['concepto']
        p.drawString(coor.descripcion_1x * cm, float(pos_y - 0.5) * cm, unicode(detalle['concepto']))
        detalle['precio_unitario'] = int(value['precio_unitario'])
        p.drawString(coor.precio_1x * cm, float(pos_y - 0.5) * cm, unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
        total_venta += int(detalle['cantidad']) * int(detalle['precio_unitario'])
        detalle['exentas'] = int(value['exentas'])
        p.drawString(coor.exentas_1x * cm, float(pos_y - 0.5) * cm, unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
        if detalle['exentas'] != '':
            exentas += int(detalle['exentas'])
        detalle['iva_5'] = int(value['iva_5'])
        p.drawString(coor.iva5_1x * cm, float(pos_y - 0.5) * cm, unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
        if detalle['iva_5'] != '':
            iva5 += int(detalle['iva_5'])
        detalle['iva_10'] = int(value['iva_10'])
        p.drawString(coor.iva10_1x * cm, float(pos_y - 0.5) * cm, unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
        if detalle['iva_10'] != '':
            iva10 += int(detalle['iva_10'])
        pos_y -= 0.5
        detalles.append(detalle)
    cantidad = 4 - len(detalles)
    pos_y -= (0.5 * cantidad)
    p.drawString(coor.sub_exentas_1x * cm, float(coor.sub_exentas_1y) * cm, unicode('{:,}'.format(exentas).replace(",", "."))) 
    p.drawString(coor.sub_iva5_1x * cm, float(coor.sub_iva5_1y) * cm, unicode('{:,}'.format(iva5).replace(",", ".")))   
    p.drawString(coor.sub_iva10_1x * cm, float(coor.sub_iva10_1y) * cm, unicode('{:,}'.format(iva10).replace(",", ".")))
    pos_y -= 0.5
    p.drawString(coor.total_a_pagar_exentas_iva5_1x * cm, float(coor.total_a_pagar_exentas_iva5_1y) * cm, unicode('{:,}'.format(exentas+iva5).replace(",", ".")))
    p.drawString(coor.total_venta_1x * cm, float(coor.total_venta_1y) * cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
    pos_y -= 1.5
    numalet = num2words(int(total_venta), lang='es')
    p.drawString(coor.total_a_pagar_letra_1x * cm, float(coor.total_a_pagar_letra_1y) * cm, unicode(numalet))
    p.drawString(coor.total_a_pagar_num_1x * cm, float(coor.total_a_pagar_num_1y) * cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
    total_iva_10 = int(iva10 / 11)
    total_iva_5 = int(iva5 / 21)
    total_iva = total_iva_10 + total_iva_5
    pos_y -= 0.5
    p.drawString(coor.liq_iva5_1x * cm, float(coor.liq_iva5_1y) * cm, unicode('{:,}'.format(total_iva_5).replace(",", ".")))
    p.drawString(coor.liq_iva10_1x * cm, float(coor.liq_iva10_1y) * cm, unicode('{:,}'.format(total_iva_10).replace(",", ".")))
    p.drawString(coor.liq_total_iva_1x * cm, float(coor.liq_total_iva_1y) * cm, unicode('{:,}'.format(total_iva).replace(",", ".")))
    # FIN PRIMERA IMPRESION
    ######################################################################################################################################
    # INICIO SEGUNDA IMPRESION
    p.drawString(coor.numero_2x * cm, float(coor.numero_2y) * cm, unicode(nueva_factura.numero))
    
    p.drawString(coor.fecha_2x * cm, float(coor.fecha_2y) * cm, unicode(request.POST.get('fecha', '')))
    if nueva_factura.tipo == 'co':
        p.drawString(coor.contado_2x * cm, float(coor.contado_2y) * cm, "X")
    else:
        p.drawString(coor.credito_2x * cm, float(coor.credito_2y) * cm, "X")
            
    p.drawString(coor.fraccion_2x * cm, float(coor.fraccion_2y) * cm, unicode(manzana.fraccion.nombre))
            # Solo se imprime el primer nombre y apellido-- Faltaaa
    nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
    p.drawString(coor.nombre_2x * cm, float(coor.nombre_2y) * cm, unicode(nombre_ape))
    p.drawString(coor.manzana_2x * cm, float(coor.manzana_2y) * cm, unicode(manzana.nro_manzana))
    p.drawString(coor.lote_2x * cm, float(coor.lote_2y) * cm, unicode(lote_id.nro_lote))
            
            
    if nueva_factura.cliente.ruc == None:
        nueva_factura.cliente.ruc = ""                
    p.drawString(coor.ruc_2x * cm, float(coor.ruc_2y) * cm, unicode(nueva_factura.cliente.ruc))
    p.drawString(coor.telefono_2x * cm, float(coor.telefono_2y) * cm, unicode(nueva_factura.cliente.telefono_laboral))
    direccion_2_str = (nueva_factura.cliente.direccion_cobro[:56] + '..') if len(nueva_factura.cliente.direccion_cobro) > 56 else nueva_factura.cliente.direccion_cobro        
    p.drawString(coor.direccion_2x * cm, float(coor.direccion_2y) * cm, unicode(direccion_2_str))
    p.drawString(coor.superficie_2x * cm, float(coor.superficie_2y) * cm, unicode(lote_id.superficie) + "  mts2")
    p.drawString(coor.cta_cte_ctral_2x * cm, float(coor.cta_cte_ctral_2y) * cm, unicode(lote_id.cuenta_corriente_catastral))
            
    # Se obtienen la lista de los detalles
    lista_detalles = json.loads(nueva_factura.detalle)
    detalles = []
    pos_y = float(coor.cantidad_2y+ 0.5)
    exentas = 0
    iva10 = 0
    iva5 = 0
    total_iva_10 = 0
    total_iva_5 = 0
    total_iva = 0           
    total_gral = 0
    total_venta = 0
    for key, value in sorted(lista_detalles.iteritems()):
        detalle = {}
        detalle['item'] = key
        detalle['cantidad'] = value['cantidad']
        p.drawString(coor.cantidad_2x * cm, float(pos_y - 0.5) * cm, unicode(detalle['cantidad']))
        detalle['concepto'] = value['concepto']
        p.drawString(coor.descripcion_2x * cm, float(pos_y - 0.5) * cm, unicode(detalle['concepto']))
        detalle['precio_unitario'] = int(value['precio_unitario'])
        p.drawString(coor.precio_2x * cm, float(pos_y - 0.5) * cm, unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
        total_venta += int(detalle['cantidad']) * int(detalle['precio_unitario'])
        detalle['exentas'] = int(value['exentas'])
        p.drawString(coor.exentas_2x * cm, float(pos_y - 0.5) * cm, unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
        if detalle['exentas'] != '':
            exentas += int(detalle['exentas'])
        detalle['iva_5'] = int(value['iva_5'])
        p.drawString(coor.iva5_2x * cm, float(pos_y - 0.5) * cm, unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
        if detalle['iva_5'] != '':
            iva5 += int(detalle['iva_5'])
        detalle['iva_10'] = int(value['iva_10'])
        p.drawString(coor.iva10_2x * cm, float(pos_y - 0.5) * cm, unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
        if detalle['iva_10'] != '':
            iva10 += int(detalle['iva_10'])
        pos_y -= 0.5
        detalles.append(detalle)
    cantidad = 4 - len(detalles)
    pos_y -= (0.5 * cantidad)
    p.drawString(coor.sub_exentas_2x * cm, float(coor.sub_exentas_2y) * cm, unicode('{:,}'.format(exentas).replace(",", "."))) 
    p.drawString(coor.sub_iva5_2x * cm, float(coor.sub_iva5_2y) * cm, unicode('{:,}'.format(iva5).replace(",", ".")))   
    p.drawString(coor.sub_iva10_2x * cm, float(coor.sub_iva10_2y) * cm, unicode('{:,}'.format(iva10).replace(",", ".")))
    pos_y -= 0.5
    p.drawString(coor.total_a_pagar_exentas_iva5_2x * cm, float(coor.total_a_pagar_exentas_iva5_2y) * cm, unicode('{:,}'.format(exentas+iva5).replace(",", ".")))
    p.drawString(coor.total_venta_2x * cm, float(coor.total_venta_2y) * cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
    pos_y -= 1.5
    numalet = num2words(int(total_venta), lang='es')
    p.drawString(coor.total_a_pagar_letra_2x * cm, float(coor.total_a_pagar_letra_2y) * cm, unicode(numalet))
    p.drawString(coor.total_a_pagar_num_2x * cm, float(coor.total_a_pagar_num_2y) * cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
    total_iva_10 = int(iva10 / 11)
    total_iva_5 = int(iva5 / 21)
    total_iva = total_iva_10 + total_iva_5
    pos_y -= 0.5
    p.drawString(coor.liq_iva5_2x * cm, float(coor.liq_iva5_2y) * cm, unicode('{:,}'.format(total_iva_5).replace(",", ".")))
    p.drawString(coor.liq_iva10_2x * cm, float(coor.liq_iva10_2y) * cm, unicode('{:,}'.format(total_iva_10).replace(",", ".")))
    p.drawString(coor.liq_total_iva_2x * cm, float(coor.liq_total_iva_2y) * cm, unicode('{:,}'.format(total_iva).replace(",", ".")))
    # FIN SEGUNDA IMPRESION
            
    p.showPage()
    p.save()             
    return response;
def obtener_cantidad_cuotas_pagadas(pago):
    
    id_pago = pago.id
    fecha_pago = pago.fecha_de_pago
    
    id_venta = pago.venta.id
    fecha_venta = pago.venta.fecha_de_venta
    
    pagos = PagoDeCuotas.objects.filter(venta=id_venta, fecha_de_pago__range=(fecha_venta, fecha_pago)).order_by('fecha_de_pago','id').aggregate(Sum('nro_cuotas_a_pagar'))
    print PagoDeCuotas.objects.filter(venta=id_venta, fecha_de_pago__range=(fecha_venta, fecha_pago)).order_by('fecha_de_pago','id').query
    cantidad_pagos = pagos['nro_cuotas_a_pagar__sum']
    return cantidad_pagos
