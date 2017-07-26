from django.db.models import Sum
from django.db import connection
from principal.models import Lote, Cliente, PlanDePago, Fraccion, Venta, \
    PagoDeCuotas, RecuperacionDeLotes, LogUsuario, CoordenadasFactura, Reserva, ConfiguracionIntereses, Configuraciones
from principal.monthdelta import MonthDelta
from calendar import monthrange
from django.core import serializers
from datetime import datetime, timedelta, date
import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.units import mm
from num2words import num2words
import math
import json
from principal.excel_styles import *
import logging
from propar01.settings import CODIGO_DE_EMPRESA
from django.utils import timezone


def get_cuotas_detail_by_lote(lote_id):
    print("buscando pagos del lote --> " + unicode(lote_id))
    # El query es: select sum(nro_cuotas_a_pagar) from principal_pagodecuotas where lote_id = 16108
    venta = get_ultima_venta_no_recuperada(lote_id)

    # Chequeamos si es una venta contado
    contado = False
    if venta is not None:

        if venta.plan_de_pago.tipo_de_plan == 'contado':
            contado = True

        cant_cuotas_pagadas = PagoDeCuotas.objects.filter(venta=venta).aggregate(Sum('nro_cuotas_a_pagar'))
        plan_de_pago = PlanDePago.objects.get(id=venta.plan_de_pago.id)

        # Se trae el monto total pagado de todas las cuotas pagadas sin intereses
        total_pagado_cuotas = PagoDeCuotas.objects.filter(venta=venta).aggregate(Sum('total_de_cuotas'))
        if total_pagado_cuotas['total_de_cuotas__sum'] is None:
            total_pagado_cuotas['total_de_cuotas__sum'] = 0
        precio_final_venta = venta.precio_final_de_venta

        # calcular la fecha de vencimiento.
        if cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']:
            proximo_vencimiento = (
                venta.fecha_primer_vencimiento + MonthDelta(cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'])).strftime(
                '%d/%m/%Y')
        else:
            # cuando no se encuentran cuotas pagadas trae None, seteamos la cantidad de cuotas pagadas a 0
            # porque la venta es independiente a los pagos de cuotas
            # cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] = 1

            cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] = 0
            proximo_vencimiento = venta.fecha_primer_vencimiento.strftime('%d/%m/%Y')

        datos = dict([('cant_cuotas_pagadas', cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']),
                      ('cantidad_total_cuotas', plan_de_pago.cantidad_de_cuotas),
                      ('contado', contado),
                      ('proximo_vencimiento', proximo_vencimiento),
                      ('total_pagado_cuotas', total_pagado_cuotas['total_de_cuotas__sum']),
                      ('precio_final_venta', precio_final_venta),
                      ])

    else:
        datos = dict([('cant_cuotas_pagadas', 0),
                      ('cantidad_total_cuotas', 0),
                      ('contado', None),
                      ('proximo_vencimiento', None),
                      ('total_pagado_cuotas', 0),
                      ('precio_final_venta', 0),
                      ])
    return datos


def loggear_accion(usuario, accion, tipo_objeto, id_objeto, codigo_lote=''):
    log = LogUsuario()
    # log.fecha_hora = datetime.datetime.now()
    log.fecha_hora = timezone.now()
    log.usuario = usuario
    log.accion = accion
    log.tipo_objeto = tipo_objeto
    log.id_objeto = id_objeto
    log.codigo_lote = codigo_lote
    log.save()


def get_nro_cuota(pago):
    PagoDeCuotas(pago)
    pago_id = pago.id
    # fecha_pago = pago.fecha_de_pago
    lote_id = pago.lote_id
    # fecha_fin=pago.fecha_de_pago

    cant_cuotas = \
        PagoDeCuotas.objects.filter(lote_id=lote_id, pk__lt=pago_id).aggregate(Sum('nro_cuotas_a_pagar')).values()[0]
    if cant_cuotas is None:
        cant_cuotas = 0
    return cant_cuotas


def pagos_db_to_custom_pagos(lista_pagos_db):
    lista_custom = []
    for pago_db in lista_pagos_db:
        item = {'fecha': pago_db.fecha_de_pago}
        lista_custom.append(item)
    return lista_custom


# Funcion que recibe una lista de objetos y una lista de labels,
# serializa la lista de objetos y retorna una lista de diccionarios
def custom_json(object_list, labels):
    try:
        data = serializers.serialize('python', object_list)
        results = []
        label1 = labels[0]
        label2 = ""
        if len(labels) > 1:
            label2 = labels[1]

        for d in data:
            d['fields']['id'] = d['pk']
            # Como maximo habra 2 labels
            if len(labels) <= 1:
                d['fields']['label'] = u'%s' % (d['fields'][label1])
            else:
                d['fields']['label'] = u'%s %s' % (d['fields'][label1], d['fields'][label2])
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


def get_cuota_information_by_lote(lote_id, cuotas_pag, facturar=False, ver_vencimientos=False, venta_param=None):
    # cant_cuotas_pag = 0
    cant_cuotas_pagadas = {}
    # print("lote_id ->" + unicode(lote_id))
    # for item_venta in ventas:
    #     print 'Obteniendo la ultima venta'
    #     try:
    #         RecuperacionDeLotes.objects.get(venta=item_venta.id)
    #     except RecuperacionDeLotes.DoesNotExist:
    #         print 'se encontro la venta no recuperada, la venta actual'
    #         venta = item_venta
    if venta_param is None:
        venta = get_ultima_venta(lote_id)
    else:
        venta = venta_param

    if ver_vencimientos:
        cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] = 0
    else:
        cant_cuotas_pagadas = PagoDeCuotas.objects.filter(venta=venta).aggregate(Sum('nro_cuotas_a_pagar'))

    # ventas = Venta.objects.filter(lote_id=lote_id)
    if cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] is None:
        cant_cuotas_pag = 0
    else:
        if not facturar:
            cant_cuotas_pag = cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']
        else:
            cant_cuotas_pag = cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'] - cuotas_pag

        if ver_vencimientos:
            cant_cuotas_pag = cuotas_pag - 1

    # cuotas_totales = 0
    cuota_a_pagar = {}
    cuotas_a_pagar = []
    # ultima_fecha_pago = ""
    cuotas_totales = cant_cuotas_pag
    if cuotas_totales != 0:
        ultima_fecha_pago = venta.fecha_primer_vencimiento + MonthDelta(cuotas_totales)
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

    # Verificar si el plan tiene cuotas de refuerzo
    if venta.plan_de_pago.cuotas_de_refuerzo != 0:
        pagos = get_pago_cuotas(venta, None, None)
        cantidad_cuotas_ref_pagadas = cant_cuotas_pagadas_ref(pagos)
        for i in range(0, int(cuotas_pag)):
            nro_cuota = cuotas_totales + 1
            cuota_a_pagar['nro_cuota'] = unicode(nro_cuota) + "/" + unicode(venta.plan_de_pago.cantidad_de_cuotas)
            cuotas_totales += 1
            cuota_a_pagar['fecha'] = (ultima_fecha_pago + MonthDelta(i)).strftime('%d/%m/%Y')
            if (nro_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo) == 0 \
                    and cantidad_cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                cuota_a_pagar['monto_cuota'] = venta.monto_cuota_refuerzo
                cantidad_cuotas_ref_pagadas += 1
            else:
                cuota_a_pagar['monto_cuota'] = venta.precio_de_cuota
            cuotas_a_pagar.append(cuota_a_pagar)
            cuota_a_pagar = {}
    else:
        for i in range(0, int(cuotas_pag)):
            nro_cuota = cuotas_totales + 1
            cuota_a_pagar['nro_cuota'] = unicode(nro_cuota) + "/" + unicode(venta.plan_de_pago.cantidad_de_cuotas)
            cuota_a_pagar['fecha'] = (ultima_fecha_pago + MonthDelta(i)).strftime('%d/%m/%Y')
            cuota_a_pagar['monto_cuota'] = venta.precio_de_cuota
            cuotas_totales += 1
            cuotas_a_pagar.append(cuota_a_pagar)
            cuota_a_pagar = {}

    return cuotas_a_pagar


def get_cuota_information_by_pagodecuota(pagodecuota_id):
    # cant_cuotas_pagadas = {}

    cant_cuotas_pagadas = PagoDeCuotas.objects.filter(pk=pagodecuota_id).aggregate(Sum('nro_cuotas_a_pagar'))

    return cant_cuotas_pagadas


def filtros_establecidos(request, tipo_informe):
    if tipo_informe == 'liquidacion_propietarios':
        try:
            fecha_ini = request['fecha_ini']
            fecha_fin = request['fecha_fin']
            tipo_b = request['tipo_busqueda']
            print("Filtros: " + "fecha_ini = " + fecha_ini + " fecha_fin = " + fecha_fin + " tipo_busqueda = " + tipo_b)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
            return False
    elif tipo_informe == 'informe_facturacion':
        try:
            fecha_ini = request['fecha_ini']
            fecha_fin = request['fecha_fin']
            print("Filtros: " + "fecha_ini = " + fecha_ini + " fecha_fin = " + fecha_fin)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
            return False
    elif tipo_informe == 'clientes_atrasados':
        # Puede filtrar solo por meses de atraso o solo por fraccion o sin ningun filtro
        try:
            if request['fraccion'] == '' and request['meses_atraso'] == '':
                return 0
            elif request['fraccion'] != '' and request['meses_atraso'] == '':
                fraccion = request['fraccion']
                print "Fraccion: " + fraccion
                return 1
            elif request['fraccion'] == '' and request['meses_atraso'] != '':
                meses_atraso = request['meses_atraso']
                print "Meses Atraso: " + meses_atraso
                return 2
            else:
                fraccion = request['fraccion']
                meses_atraso = request['meses_atraso']
                print "Fraccion: " + fraccion + " Meses Atraso: " + meses_atraso
                return 3
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
            return 0
    elif tipo_informe == 'proximos_vencimientos':
        try:
            if request['fraccion'] == '':
                return 0
            else:
                fecha_ini = request['fecha_ini']
                fecha_fin = request['fecha_fin']
                tipo_b = request['tipo_busqueda']
                print("Filtros: " + "fecha_ini = " + fecha_ini + " fecha_fin = " + fecha_fin + " tipo_busqueda = " + tipo_b)
                return 1
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
            return 2
    elif tipo_informe == 'lotes_libres':
        try:
            sucursal = request['sucursal']
            print "Sucursal: " + sucursal
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')

    elif tipo_informe == 'informe_movimientos':
        try:
            objeto = {
                'lote_ini': request['lote_ini'],
                'lote_fin': request['lote_fin'],
                'fecha_ini': request['fecha_ini'],
                'fecha_fin': request['fecha_fin']
            }
            print "Filtros: " + unicode(objeto)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == "informe_general":
        try:
            objeto = {
                'fraccion_ini': request['fraccion_ini'],
                'fraccion_fin': request['fraccion_fin'],
                'fecha_ini': request['fecha_ini'],
                'fecha_fin': request['fecha_fin']
            }
            print "Filtros: " + unicode(objeto)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == "informe_cuotas_por_cobrar":
        try:
            fraccion_ini = request['fraccion_ini']
            print "fraccion_ini: " + fraccion_ini
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == "liquidacion_vendedores":
        try:
            objeto = {
                'fecha_ini': request['fecha_ini'],
                'fecha_fin': request['fecha_fin'],
                'busqueda': request['busqueda']
            }
            print "Filtros: " + unicode(objeto)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == "liquidacion_general_vendedores":
        try:
            objeto = {
                'fecha_ini': request['fecha_ini'],
                'fecha_fin': request['fecha_fin']
            }
            print "Filtros: " + unicode(objeto)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == "liquidacion_gerentes":
        try:
            fecha = request['fecha']
            print "fecha: " + fecha
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == "informe_ventas":
        try:
            lote = request['busqueda']
            print "Lote: " + lote
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == "informe_pagos_practipago":
        try:
            objeto = {
                'fecha_ini': request['fecha_ini'],
                'fecha_fin': request['fecha_fin'],
                'sucursal': request['sucursal']
            }
            print "Filtros: " + unicode(objeto)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == 'listado_clientes':
        try:
            objeto = {
                'tipo_busqueda': request['tipo_busqueda'],
                'busqueda_label': request['busqueda_label']
            }
            print "Filtros: " + unicode(objeto)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == 'informe_cuotas_devengadas':
        try:
            objeto = {
                'fecha_ini': request['fecha_ini'],
                'fecha_fin': request['fecha_fin']
            }
            print "Filtros: " + unicode(objeto)
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    elif tipo_informe == 'deudores_por_venta':
        try:
            fraccion = request['fraccion']
            print "fraccion: " + fraccion
            return True
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            print('Parametros no seteados')
    return False


def obtener_dias_atraso(fecha_pago_parsed, fecha_vencimiento_parsed):
    if fecha_pago_parsed > fecha_vencimiento_parsed:
        diferencia = fecha_pago_parsed - fecha_vencimiento_parsed
        dias_atraso = diferencia.days
    else:
        dias_atraso = 0
    return dias_atraso


def obtener_detalle_interes_lote(lote_id, fecha_pago_parsed, proximo_vencimiento_parsed, nro_cuotas_a_pagar):
    if lote_id == 519:
        print "este es el lote"
    # Si se tienen cuotas en MORA.
    dias_habiles = 0
    dias_atraso_1ra_cuota = 0
    if nro_cuotas_a_pagar > 0:

        resumen_lote = get_cuotas_detail_by_lote(unicode(lote_id))
        cuotas_pagadas = resumen_lote['cant_cuotas_pagadas']

        detalles = []
        sumatoria_intereses = 0
        es_ref = False
        cantidad_pagos_ref = 0
        fecha_dias_gracia = ""
        gestion_cobranza = {}
        # El cliente tiene cuotas atrasadas
        if fecha_pago_parsed > proximo_vencimiento_parsed:

            #         TODO:
            #         Se calcula la diferencia en dias de la fecha del pago que se esta realizando, con
            #         respecto a la fecha de vencimiento de dicho pago. El porcentaje de interes que se aplica
            #         sobre las cuotas es constante: 0.001 (0.03/30) -> 3% interes mensual/30
            #         + interes punitorio (0.00030) + iva = (interes mensual + interes punitorio)* (10%)=(0.00013)

            venta = get_ultima_venta(lote_id)

            # Calculamos en base al primer vencimiento, cuantas cuotas debieron haberse pagado hasta la fecha
            fecha_primer_vencimiento = venta.fecha_primer_vencimiento
            cantidad_ideal_cuotas = monthdelta(fecha_primer_vencimiento, fecha_pago_parsed) + 1
            # cantidad_ideal_cuotas=monthdelta(fecha_primer_vencimiento, fecha_pago_parsed) +1
            # Y obtenemos las cuotas atrasadas
            cuotas_atrasadas = cantidad_ideal_cuotas - cuotas_pagadas

            if cuotas_atrasadas == 0:
                fecha_proximo_vencimiento_dias = proximo_vencimiento_parsed
                fecha_pago_dias = fecha_pago_parsed
                dias_atraso = fecha_pago_dias - fecha_proximo_vencimiento_dias
                if dias_atraso.days > 5:
                    cuotas_atrasadas = 1

            monto_cuota = venta.precio_de_cuota
            # Intereses (valores constantes)
            # Interes moratorio por dia
            config_intereses = ConfiguracionIntereses.objects.get(codigo_empresa=CODIGO_DE_EMPRESA)
            interes = config_intereses.porcentaje_interes_cuota

            # Interes
            # interes_punitorio=0.00030
            # Intereses IVA
            # interes_iva=0.00013
            interes_iva = 0.0001
            # total_intereses=interes+interes_punitorio+interes_iva
            if config_intereses.codigo_empresa == "VIER":
                total_intereses = interes
            else:
                total_intereses = interes + interes_iva
                # Verificar si tiene cuotas de refuerzo
                if venta.plan_de_pago.cuotas_de_refuerzo != 0:
                    pagos = get_pago_cuotas(venta, None, None)
                    cantidad_pagos_ref = cant_cuotas_pagadas_ref(pagos)
                    es_ref = True
                else:
                    cantidad_pagos_ref = 0
                    es_ref = False

            if int(nro_cuotas_a_pagar) < int(cuotas_atrasadas):
                rango = int(nro_cuotas_a_pagar)
            else:
                rango = int(cuotas_atrasadas)

            for cuota in range(rango):
                detalle = {}
                fecha_vencimiento = proximo_vencimiento_parsed + MonthDelta(cuota)
                dias_atraso = (fecha_pago_parsed - fecha_vencimiento).days
                if dias_atraso_1ra_cuota == 0:
                    dias_atraso_1ra_cuota = dias_atraso
                nro_cuota = cuotas_pagadas + (cuota + 1)
                if es_ref:
                    resto_division = nro_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo
                    if resto_division == 0 and cantidad_pagos_ref < venta.plan_de_pago.cuotas_de_refuerzo:
                        monto_cuota = venta.monto_cuota_refuerzo
                        cantidad_pagos_ref += 1
                    else:
                        monto_cuota = venta.precio_de_cuota
                else:
                    monto_cuota = venta.precio_de_cuota
                    detalle['vencimiento'] = fecha_vencimiento.strftime('%d/%m/%Y')
                    fecha_ultimo_vencimiento = datetime.datetime.strptime(detalle['vencimiento'], "%d/%m/%Y").date()
                    if config_intereses.codigo_empresa == "VIER" \
                            and cuotas_atrasadas > config_intereses.cuotas_dias_gracia:
                        fecha_dias_gracia = fecha_ultimo_vencimiento
                    else:
                        fecha_dias_gracia = fecha_ultimo_vencimiento + datetime.timedelta(days=5)
                        dias_habiles = calcular_dias_habiles(fecha_ultimo_vencimiento, fecha_dias_gracia)

                if dias_habiles < 5:
                    fecha_ultimo_vencimiento = fecha_dias_gracia + datetime.timedelta(days=5 - dias_habiles)
                detalle['vencimiento_gracia'] = fecha_ultimo_vencimiento.strftime('%d/%m/%Y')
                if fecha_pago_parsed > fecha_ultimo_vencimiento:
                    if config_intereses.codigo_empresa == "VIER":
                        intereses = math.ceil(total_intereses * (cuotas_atrasadas - cuota) * monto_cuota)
                        redondeado = roundup(intereses)
                    else:
                        intereses = math.ceil(total_intereses * dias_atraso * monto_cuota)
                        redondeado = roundup(intereses)
                else:
                    intereses = 0
                    redondeado = roundup(intereses)

                # detalle['interes'] = interes
                # detalle['interes_punitorio']=interes_punitorio
                detalle['interes_iva'] = interes_iva
                detalle['nro_cuota'] = nro_cuota
                detalle['dias_atraso'] = dias_atraso
                detalle['intereses'] = redondeado
                detalle['tipo'] = 'normal'

                sumatoria_intereses += redondeado

                detalles.append(detalle)

            # Calculamos en base al primer vencimiento, cuantas cuotas debieron haberse pagado hasta la fecha
            # fecha_vencimiento_mes_pago = fecha_primer_vencimiento + MonthDelta(+cantidad_ideal_cuotas)
            # fecha_dias_gracia = fecha_vencimiento_mes_pago + datetime.timedelta(days=5)
            # dias_habiles = calcular_dias_habiles(fecha_vencimiento_mes_pago,fecha_dias_gracia)
            # if dias_habiles<5:
            #    fecha_vencimiento_mes_pago = fecha_dias_gracia+datetime.timedelta(days=5-dias_habiles)
            # cantidad_ideal_cuotas=monthdelta(fecha_primer_vencimiento, fecha_vencimiento_mes_pago)
            # cuotas_atrasadas=cantidad_ideal_cuotas-cuotas_pagadas

            if dias_atraso_1ra_cuota > 180:
                # gestion_cobranza = int(0.1*(math.ceil(float(cuotas_atrasadas*monto_cuota))+sumatoria_intereses))
                if config_intereses.gestion_cobranza:
                    gestion_cobranza = roundup(0.05*(
                        (cuotas_atrasadas*monto_cuota)+sumatoria_intereses) +
                                               (0.05*((cuotas_atrasadas*monto_cuota)+sumatoria_intereses))*0.10)
                detalles.append({'gestion_cobranza': gestion_cobranza, 'tipo': 'gestion_cobranza'})
                print detalles
            return detalles
        else:
            return []


def obtener_cuotas_a_pagar(venta, fecha_pago, resumen_cuotas_a_pagar):
    lista_cuotas = []
    cantidad_cuotas = 0
    sumatoria_cuotas = 0
    proximo_vencimiento = datetime.datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date()
    cuota = {}
    intereses = []
    if proximo_vencimiento < fecha_pago:
        print 'Hay al menos 1 cuota en mora'
        try:
            # Calculamos en base al primer vencimiento, cuantas cuotas debieron haberse pagado hasta la fecha
            fecha_primer_vencimiento = venta.fecha_primer_vencimiento
            cantidad_ideal_cuotas = monthdelta(fecha_primer_vencimiento, fecha_pago)
            # Y obtenemos las cuotas atrasadas
            cuotas_atrasadas = cantidad_ideal_cuotas - int(resumen_cuotas_a_pagar['cant_cuotas_pagadas'])
            intereses = obtener_detalle_interes_lote(venta.lote.id, fecha_pago, datetime.datetime.strptime(
                resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date(), cuotas_atrasadas)
        except Exception, error:
            print error
        interes_total = 0
        if len(intereses) <= 5:  # Hasta 5 cuotas
            for interes_item in intereses:
                if interes_item['tipo'] == 'normal':
                    cantidad_cuotas += 1
                    interes_total += interes_item['intereses']
                    sumatoria_cuotas = sumatoria_cuotas + venta.precio_de_cuota + interes_total
                    cuota = {
                        'cantidad_sumatoria_cuotas': cantidad_cuotas,
                        'numero_cuota': interes_item['nro_cuota'],
                        'monto_cuota': venta.precio_de_cuota,
                        'interes': interes_item['intereses'],
                        'interes_total': interes_total,
                        'monto_total_a_pagar': venta.precio_de_cuota + interes_total,
                        'vencimiento': interes_item['vencimiento'],
                        'fecha_pago': fecha_pago.strftime("%d/%m/%Y"),
                        'monto_sumatoria_cuotas': sumatoria_cuotas
                    }

                lista_cuotas.append(cuota)
            # Ademas de las cuotas con mora se agrega la cuota actual que es posible pagar
            vencimiento_cuota_acutal = datetime.datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'],
                                                                  "%d/%m/%Y").date() + MonthDelta(len(intereses))
            cuota = {
                'cantidad_sumatoria_cuotas': cantidad_cuotas + 1,
                'numero_cuota': resumen_cuotas_a_pagar['cant_cuotas_pagadas'] + len(intereses) + 1,
                'monto_cuota': venta.precio_de_cuota,
                'interes': 0,
                'interes_total': 0,
                'monto_total_a_pagar': venta.precio_de_cuota,
                'vencimiento': vencimiento_cuota_acutal.strftime("%d/%m/%Y"),
                'fecha_pago': fecha_pago.strftime("%d/%m/%Y"),
                'monto_sumatoria_cuotas': sumatoria_cuotas + venta.precio_de_cuota
            }
            lista_cuotas.append(cuota)
        else:

            error_item = {'codigo': '33', 'mensaje': 'Compra con mas de 6 meses de atraso'}
            error = {'error': error_item}
            return error
    else:
        print 'Cliente esta al dia, solo debe abonar una cuota'
        cuota = {'cantidad_sumatoria_cuotas': 1,
                 'numero_cuota': resumen_cuotas_a_pagar['cant_cuotas_pagadas'] + 1,
                 'monto_cuota': venta.precio_de_cuota,
                 'interes': 0,
                 'interes_total': 0,
                 'monto_total_a_pagar': venta.precio_de_cuota,
                 'vencimiento': resumen_cuotas_a_pagar['proximo_vencimiento'],
                 'fecha_pago': fecha_pago.strftime("%d/%m/%Y"),
                 'monto_sumatoria_cuotas': sumatoria_cuotas + venta.precio_de_cuota
                 }
        lista_cuotas.append(cuota)

    return lista_cuotas


def obtener_cuotas_a_pagar_full(venta, fecha_pago, resumen_cuotas_a_pagar, maximo_atraso):
    lista_cuotas = []
    cantidad_cuotas = 0
    sumatoria_cuotas = 0

    if not resumen_cuotas_a_pagar['contado'] and resumen_cuotas_a_pagar['cant_cuotas_pagadas'] \
            != resumen_cuotas_a_pagar['cantidad_total_cuotas']:
        proximo_vencimiento = datetime.datetime.strptime(
            resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y"
        ).date()
        if proximo_vencimiento < fecha_pago:

            print 'Hay al menos 1 cuota en mora'

            # Calculamos en base al primer vencimiento, cuantas cuotas debieron haberse pagado hasta la fecha
            # fecha_primer_vencimiento = venta.fecha_primer_vencimiento

            # Obtenemos las cuotas atrasadas
            cuotas_atrasadas = int(resumen_cuotas_a_pagar['cantidad_total_cuotas']) - int(
                resumen_cuotas_a_pagar['cant_cuotas_pagadas'])

            intereses = obtener_detalle_interes_lote(venta.lote.id, fecha_pago, datetime.datetime.strptime(
                resumen_cuotas_a_pagar['proximo_vencimiento'], "%d/%m/%Y").date(), cuotas_atrasadas)
            interes_total = 0

            if intereses == None:
                print 'intereses es none'

            if len(intereses) <= maximo_atraso:  # Hasta 300 cuotas (infinito)

                for interes_item in intereses:

                    if interes_item['tipo'] == 'normal':

                        cantidad_cuotas += 1
                        interes_total += interes_item['intereses']
                        sumatoria_cuotas = sumatoria_cuotas + venta.precio_de_cuota + interes_item['intereses']
                        cuota = {
                            'cantidad_sumatoria_cuotas': cantidad_cuotas,
                            'numero_cuota': interes_item['nro_cuota'],
                            'monto_cuota': venta.precio_de_cuota,
                            'interes': interes_item['intereses'],
                            'interes_total': interes_total,
                            'monto_total_a_pagar': venta.precio_de_cuota + interes_item['intereses'],
                            'vencimiento': interes_item['vencimiento'],
                            'fecha_pago': fecha_pago.strftime("%d/%m/%Y"),
                            'monto_sumatoria_cuotas': sumatoria_cuotas
                        }
                    else:
                        cuota = {}

                    lista_cuotas.append(cuota)
                # Ademas de las cuotas con mora se agrega la cuota actual que es posible pagar
                vencimiento_cuota_acutal = datetime.datetime.strptime(resumen_cuotas_a_pagar['proximo_vencimiento'],
                                                                      "%d/%m/%Y").date() + MonthDelta(len(intereses))
                cuota = {
                    'cantidad_sumatoria_cuotas': cantidad_cuotas + 1,
                    'numero_cuota': resumen_cuotas_a_pagar['cant_cuotas_pagadas'] + len(intereses) + 1,
                    'monto_cuota': venta.precio_de_cuota,
                    'interes': 0,
                    'interes_total': 0,
                    'monto_total_a_pagar': venta.precio_de_cuota,
                    'vencimiento': vencimiento_cuota_acutal.strftime("%d/%m/%Y"),
                    'fecha_pago': fecha_pago.strftime("%d/%m/%Y"),
                    'monto_sumatoria_cuotas': sumatoria_cuotas + venta.precio_de_cuota
                }
                lista_cuotas.append(cuota)
            else:

                error_item = {'codigo': '33', 'mensaje': 'Compra con mas de ' + maximo_atraso + ' meses de atraso'}
                error = {'error': error_item}
                return error
        else:
            print 'Cliente esta al dia, solo debe abonar una cuota'
            cuota = {'cantidad_sumatoria_cuotas': 1,
                     'numero_cuota': resumen_cuotas_a_pagar['cant_cuotas_pagadas'] + 1,
                     'monto_cuota': venta.precio_de_cuota,
                     'interes': 0,
                     'interes_total': 0,
                     'monto_total_a_pagar': venta.precio_de_cuota,
                     'vencimiento': resumen_cuotas_a_pagar['proximo_vencimiento'],
                     'fecha_pago': fecha_pago.strftime("%d/%m/%Y"),
                     'monto_sumatoria_cuotas': sumatoria_cuotas + venta.precio_de_cuota
                     }
            lista_cuotas.append(cuota)
    else:
        print 'Es una venta al CONTADO'
        lista_cuotas = []

    return lista_cuotas


def verificar_permisos(user_id, permiso_buscado):
    """
    Metodo que comprueba que un usuario determinado tenga permisos sobre esa vista
    @return: True, False
    @rtype: Boolean
    """

    print("Id_user->" + unicode(user_id))
    print("Permiso->" + unicode(permiso_buscado))
    user = User.objects.get(id=user_id)
    lista_permisos = user.get_all_permissions()
    tiene_permiso = False

    for permiso in lista_permisos:
        if user.groups.get().name == "Administradores":
            tiene_permiso = True
            break
        permiso_sin_punto = permiso.split(".")[1]
        if permiso_sin_punto == permiso_buscado:
            tiene_permiso = True
            break

    if tiene_permiso:
        print("El usuario si posee ese permiso")
        ok = True
    else:
        print("El usuario no posee ese permiso")
        ok = False
    return ok


def get_pago_cuotas(venta, fecha_ini, fecha_fin, pagos=None, pagos_anteriores=None):
    cantidad_pagos_anteriores = 0

    if venta.id == 4125:
        print 'esta es la venta'

    if fecha_ini is None and fecha_fin is None:
        # Se traen todos los pagos
        if pagos is None:
            pagos = PagoDeCuotas.objects.filter(venta_id=venta.id).order_by('id')

    else:
        # Primero se cuenta cuantos son los pagos anteriores y despues se filtra
        if pagos_anteriores is None:
            cantidad_pagos_anteriores = \
                PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__lt=fecha_ini).aggregate(
                    Sum('nro_cuotas_a_pagar')).values()[0]
        else:
            for pago in pagos_anteriores:
                if venta.id == 2652:
                    print "esta es la venta"
                if pago['venta_id'] == venta.id:
                    cantidad_pagos_anteriores = pago['nro_cuotas_a_pagar__sum']
                    break

        if pagos is None:
            time = datetime.time(23,59)
            fecha_fin = datetime.datetime.combine(fecha_fin, time)
            pagos = PagoDeCuotas.objects.filter(venta_id=venta.id,
                                                fecha_de_pago__range=(fecha_ini, fecha_fin)).order_by('fecha_de_pago')

        if cantidad_pagos_anteriores is None:
            cantidad_pagos_anteriores = 0

    cuotas_ref_pagadas = 0
    numero_cuota = cantidad_pagos_anteriores + 1
    ventas_pagos_list = []
    es_refuerzo = False
    if venta.plan_de_pago.cuotas_de_refuerzo != 0:
        for pago in pagos:
            if pago.venta == venta:
                resto_division = numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo
                if resto_division == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                    monto_cuota = venta.monto_cuota_refuerzo
                    cuotas_ref_pagadas += 1
                    es_refuerzo = True
                else:
                    monto_cuota = venta.precio_de_cuota
                    es_refuerzo = False
                if pago.nro_cuotas_a_pagar > 1:
                    for x in xrange(1, pago.nro_cuotas_a_pagar + 1):
                        resto_division = numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo
                        if resto_division == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                            monto_cuota = venta.monto_cuota_refuerzo
                            cuotas_ref_pagadas += 1
                            es_refuerzo = True
                        else:
                            monto_cuota = venta.precio_de_cuota
                            es_refuerzo = False
                        cuota = {
                            'fecha_de_pago': pago.fecha_de_pago,
                            'id': pago.id,
                            'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                                pago.plan_de_pago.cantidad_de_cuotas),
                            'nro_cuota': unicode(numero_cuota),
                            'monto': unicode(monto_cuota),
                            'refuerzo': es_refuerzo,
                            'lote': pago.lote,
                            'fraccion': dict(pago.lote.manzana.fraccion),
                            'cuota_obsequio': pago.cuota_obsequio}
                        ventas_pagos_list.append(cuota)
                        numero_cuota += 1
                else:
                    cuota = {
                        'fecha_de_pago': pago.fecha_de_pago,
                        'id': pago.id,
                        'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                            pago.plan_de_pago.cantidad_de_cuotas),
                        'nro_cuota': unicode(numero_cuota),
                        'monto': unicode(monto_cuota),
                        'refuerzo': es_refuerzo,
                        'lote': pago.lote,
                        'fraccion': pago.lote.manzana.fraccion,
                        'cuota_obsequio': pago.cuota_obsequio
                    }
                    ventas_pagos_list.append(cuota)
                    numero_cuota += 1
    else:
        monto_cuota = venta.precio_de_cuota
        for pago in pagos:
            if pago.venta == venta:
                if pago.nro_cuotas_a_pagar > 1:
                    for x in xrange(1, pago.nro_cuotas_a_pagar + 1):
                        cuota = {
                            'fecha_de_pago': pago.fecha_de_pago,
                            'id': pago.id,
                            'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                                pago.plan_de_pago.cantidad_de_cuotas),
                            'nro_cuota': unicode(numero_cuota),
                            'monto': unicode(monto_cuota),
                            'refuerzo': es_refuerzo,
                            'lote': pago.lote,
                            'fraccion': pago.lote.manzana.fraccion,
                            'cuota_obsequio': pago.cuota_obsequio
                        }
                        ventas_pagos_list.append(cuota)
                        numero_cuota += 1
                else:
                    cuota = {
                        'fecha_de_pago': pago.fecha_de_pago,
                        'id': pago.id,
                        'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                            pago.plan_de_pago.cantidad_de_cuotas),
                        'nro_cuota': unicode(numero_cuota),
                        'monto': unicode(monto_cuota),
                        'refuerzo': es_refuerzo,
                        'lote': pago.lote,
                        'fraccion': pago.lote.manzana.fraccion,
                        'cuota_obsequio': pago.cuota_obsequio
                    }
                    ventas_pagos_list.append(cuota)
                    numero_cuota += 1
    return ventas_pagos_list


def get_pago_cuotas_2(venta, fecha_ini, fecha_fin):
    if fecha_ini is None and fecha_fin is None:
        # Se traen todos los pagos
        pagos = PagoDeCuotas.objects.filter(venta_id=venta.id).order_by('fecha_de_pago')
        cantidad_pagos_anteriores = 0
    else:
        # Primero se cuenta cuantos son los pagos anteriores y despues se filtra
        cantidad_pagos_anteriores = \
            PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__lt=fecha_ini).aggregate(
                Sum('nro_cuotas_a_pagar')).values()[0]
        pagos = PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__range=(fecha_ini, fecha_fin)).order_by(
            'fecha_de_pago')
        if cantidad_pagos_anteriores is None:
            cantidad_pagos_anteriores = 0

    cuotas_ref_pagadas = 0
    numero_cuota = cantidad_pagos_anteriores + 1
    ventas_pagos_list = []
    es_refuerzo = False
    if venta.plan_de_pago.cuotas_de_refuerzo != 0:
        for pago in pagos:
            resto_division = numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo
            if resto_division == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                monto_cuota = venta.monto_cuota_refuerzo
                cuotas_ref_pagadas += 1
                es_refuerzo = True
            else:
                monto_cuota = venta.precio_de_cuota
                es_refuerzo = False
            if pago.nro_cuotas_a_pagar > 1:
                for x in xrange(1, pago.nro_cuotas_a_pagar + 1):
                    resto_division = numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo
                    if resto_division == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                        monto_cuota = venta.monto_cuota_refuerzo
                        cuotas_ref_pagadas += 1
                        es_refuerzo = True
                    else:
                        monto_cuota = venta.precio_de_cuota
                        es_refuerzo = False
                    cuota = {
                        'fecha_de_pago': pago.fecha_de_pago,
                        'id': pago.id,
                        'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                                 pago.plan_de_pago.cantidad_de_cuotas),
                        'nro_cuota': unicode(numero_cuota),
                        'monto': unicode(monto_cuota),
                        'refuerzo': es_refuerzo,
                        'lote': pago.lote}
                    # cuota['fraccion'] = dict(pago.lote.manzana.fraccion)
                    ventas_pagos_list.append(cuota)
                    numero_cuota += 1
            else:
                cuota = {
                    'fecha_de_pago': pago.fecha_de_pago,
                    'id': pago.id,
                    'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                             pago.plan_de_pago.cantidad_de_cuotas),
                    'nro_cuota': unicode(numero_cuota),
                    'monto': unicode(monto_cuota),
                    'refuerzo': es_refuerzo,
                    'lote': pago.lote
                }
                # cuota['fraccion'] = pago.lote.manzana.fraccion
                ventas_pagos_list.append(cuota)
                numero_cuota += 1
    else:
        monto_cuota = venta.precio_de_cuota
        for pago in pagos:
            if pago.nro_cuotas_a_pagar > 1:
                for x in xrange(1, pago.nro_cuotas_a_pagar + 1):
                    cuota = {
                        'fecha_de_pago': pago.fecha_de_pago,
                        'id': pago.id,
                        'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                                 pago.plan_de_pago.cantidad_de_cuotas),
                        'nro_cuota': unicode(numero_cuota),
                        'monto': unicode(monto_cuota),
                        'refuerzo': es_refuerzo,
                        'lote': pago.lote}
                    # cuota['fraccion'] = pago.lote.manzana.fraccion
                    ventas_pagos_list.append(cuota)
                    numero_cuota += 1
            else:
                cuota = {
                    'fecha_de_pago': pago.fecha_de_pago,
                    'id': pago.id,
                    'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                             pago.plan_de_pago.cantidad_de_cuotas),
                    'nro_cuota': unicode(numero_cuota),
                    'monto': unicode(monto_cuota),
                    'refuerzo': es_refuerzo,
                    'lote': pago.lote
                }
                # cuota['fraccion'] = pago.lote.manzana.fraccion
                ventas_pagos_list.append(cuota)
                numero_cuota += 1
    return ventas_pagos_list


def get_pago_cuotas_3(venta, fecha_ini, fecha_fin):
    if fecha_ini is None and fecha_fin is None:
        # Se traen todos los pagos
        pagos = PagoDeCuotas.objects.filter(venta_id=venta.id).order_by('fecha_de_pago')
        cantidad_pagos_anteriores = 0
    else:
        # Primero se cuenta cuantos son los pagos anteriores y despues se filtra
        cantidad_pagos_anteriores = \
            PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__lt=fecha_ini).aggregate(
                Sum('nro_cuotas_a_pagar')).values()[0]
        pagos = PagoDeCuotas.objects.filter(venta_id=venta.id, fecha_de_pago__range=(fecha_ini, fecha_fin)).order_by(
            'fecha_de_pago')
        if cantidad_pagos_anteriores is None:
            cantidad_pagos_anteriores = 0

    cuotas_ref_pagadas = 0
    numero_cuota = cantidad_pagos_anteriores + 1
    ventas_pagos_list = []
    es_refuerzo = False
    if venta.plan_de_pago.cuotas_de_refuerzo != 0:
        for pago in pagos:
            resto_division = numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo
            if resto_division == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                monto_cuota = venta.monto_cuota_refuerzo
                cuotas_ref_pagadas += 1
                es_refuerzo = True
            else:
                monto_cuota = venta.precio_de_cuota
                es_refuerzo = False
            if pago.nro_cuotas_a_pagar > 1:
                for x in xrange(1, pago.nro_cuotas_a_pagar + 1):
                    resto_division = numero_cuota % venta.plan_de_pago.intervalo_cuota_refuerzo
                    if resto_division == 0 and cuotas_ref_pagadas < venta.plan_de_pago.cuotas_de_refuerzo:
                        monto_cuota = venta.monto_cuota_refuerzo
                        cuotas_ref_pagadas += 1
                        es_refuerzo = True
                    else:
                        monto_cuota = venta.precio_de_cuota
                        es_refuerzo = False
                    cuota = {
                        'fecha_de_pago': pago.fecha_de_pago,
                        'id': pago.id,
                        'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                                 pago.plan_de_pago.cantidad_de_cuotas),
                        'nro_cuota': unicode(numero_cuota),
                        'monto': unicode(monto_cuota),
                        'refuerzo': es_refuerzo}
                    # cuota['lote'] = pago.lote
                    # cuota['fraccion'] = dict(pago.lote.manzana.fraccion)
                    ventas_pagos_list.append(cuota)
                    numero_cuota += 1
            else:
                cuota = {
                    'fecha_de_pago': pago.fecha_de_pago,
                    'id': pago.id,
                    'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                             pago.plan_de_pago.cantidad_de_cuotas),
                    'nro_cuota': unicode(numero_cuota),
                    'monto': unicode(monto_cuota),
                    'refuerzo': es_refuerzo
                }
                # cuota['lote'] = pago.lote
                # cuota['fraccion'] = pago.lote.manzana.fraccion
                ventas_pagos_list.append(cuota)
                numero_cuota += 1
    else:
        monto_cuota = venta.precio_de_cuota
        for pago in pagos:
            if pago.nro_cuotas_a_pagar > 1:
                for x in xrange(1, pago.nro_cuotas_a_pagar + 1):
                    cuota = {
                        'fecha_de_pago': pago.fecha_de_pago,
                        'id': pago.id,
                        'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                                 pago.plan_de_pago.cantidad_de_cuotas),
                        'nro_cuota': unicode(numero_cuota),
                        'monto': unicode(monto_cuota),
                        'refuerzo': es_refuerzo
                    }
                    # cuota['lote'] = pago.lote
                    # cuota['fraccion'] = pago.lote.manzana.fraccion
                    ventas_pagos_list.append(cuota)
                    numero_cuota += 1
            else:
                cuota = {
                    'fecha_de_pago': pago.fecha_de_pago,
                    'id': pago.id,
                    'nro_cuota_y_total': unicode(numero_cuota) + '/' + unicode(
                             pago.plan_de_pago.cantidad_de_cuotas),
                    'nro_cuota': unicode(numero_cuota),
                    'monto': unicode(monto_cuota),
                    'refuerzo': es_refuerzo
                }
                # cuota['lote'] = pago.lote
                # cuota['fraccion'] = pago.lote.manzana.fraccion
                ventas_pagos_list.append(cuota)
                numero_cuota += 1
    return ventas_pagos_list


def cant_cuotas_pagadas_ref(pagos):
    cuotas_ref_pagadas = 0
    for pago in pagos:
        if pago['refuerzo']:
            cuotas_ref_pagadas += 1
    return cuotas_ref_pagadas


def calcular_dias_habiles(fecha_ini, fecha_fin):
    start = fecha_ini
    end = fecha_fin

    daydiff = end.weekday() - start.weekday()

    # Verificamos cuantos dias habiles hay entre la fecha del ultimo vencimiento
    # y esa misma fecha + 5 dias de gracia
    days = ((end - start).days - daydiff) / 7 * 5 + min(daydiff, 5) - (max(end.weekday() - 4, 0) % 5)

    return days


def roundup(interes):
    # return int(math.ceil(interes / 1000.0)) * 1000

    # Caso redondeado de a 500
    number = interes / 1000.0

    miles = int(number) * 1000

    centenas = str(number - int(number))[2:]

    centenas = int(centenas)

    if centenas > 10:
        if centenas >= 500:
            miles += 1000
            centenas = 0
        elif centenas < 500 and centenas < 50:
            centenas = 0
        elif 500 > centenas > 50 and centenas < 100:
            miles += 1000
            centenas = 0
        else:
            centenas = 0
            # elif centenas == 500:
            # centenas = 500

    else:
        if centenas >= 5:
            miles += 1000
            centenas = 0
        elif centenas < 5:
            centenas = 0
            # elif centenas == 5:
            # centenas = 500

    decenas = 0

    resultado = miles + centenas + decenas

    return resultado


# Caso redondeado de a 100
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

# Funcion que encuentra todas las ventas de un lote y retorna la ultima
def get_ultima_venta(lote_id):
    venta = None
    ventas = Venta.objects.filter(lote_id=lote_id).order_by('fecha_de_venta')
    for item_venta in ventas:
        print 'Obteniendo la ultima venta'
        try:
            venta_recuperada = RecuperacionDeLotes.objects.get(venta=item_venta.id)
            venta = item_venta
        except RecuperacionDeLotes.DoesNotExist:
            print 'se encontro la venta no recuperada, la venta actual'
            venta = item_venta

    if 'venta' in locals():
        print 'SE ENCONTRO LA VENTA'
    else:
        print 'NO SE ENCONTRO LA VENTA'
        venta = Venta.objects.filter(lote_id=lote_id).order_by('fecha_de_venta')
    return venta


# Funcion que encuentra todas las ventas de un lote y retorna la ultima siempre que no sea recuperada
def get_ultima_venta_no_recuperada(lote_id):
    # ventas = Venta.objects.filter(lote_id=lote_id).order_by('fecha_de_venta')
    venta = None
    # QUERY PARA TRAER LA ULTIMA VENTA QUE NO ES RECUPERADA DEL LOTE EN CUESTION
    query = (
        '''
        SELECT * FROM "principal_venta" WHERE "principal_venta"."lote_id" = (%s) AND "principal_venta"."id" NOT IN (
        SELECT "venta_id" FROM "principal_recuperaciondelotes")
        '''
    )
    cursor = connection.cursor()
    cursor.execute(query, [lote_id])
    results = cursor.fetchall()

    # si el result no encuentra nada retorna una lista vacia y eso contemplamos para que no intente obtener la venta
    if len(results) > 0:
        # Obtenemos la Venta con ese id a partir del result
        ventas = Venta.objects.filter(id=results[0][0]).order_by('fecha_de_venta')

        # for item_venta in ventas:
        for item_venta in ventas:
            print 'Obteniendo la ultima venta'
            try:
                venta_recuperada = RecuperacionDeLotes.objects.get(venta=item_venta.id)
                # venta_recuperada = RecuperacionDeLotes.objects.get(venta=results[0])
                venta = None
            except RecuperacionDeLotes.DoesNotExist:
                print 'se encontro la venta no recuperada, la venta actual'
                venta = item_venta

    if 'venta' in locals():
        print 'SE ENCONTRO LA VENTA'
    else:
        print 'NO SE ENCONTRO LA VENTA'
        venta = None
    return venta


def crear_pdf_factura(nueva_factura, manzana, lote_id, usuario):
    response = HttpResponse(content_type='application/pdf')
    # nombre_factura = "factura-" + nueva_factura.numero + ".pdf"
    response['Content-Disposition'] = 'attachment filename=factura' + str(nueva_factura.id) + '.pdf'
    p = canvas.Canvas(response)
    p.setPageSize((210 * mm, 297 * mm))
    p.setFont("Helvetica", 7)

    # Obtener las coordenadas de impresion de la factura
    try:
        coor = CoordenadasFactura.objects.get(usuario=usuario)
    except Exception as e:
        logging.error('Failed.', exc_info=e)

        coor = CoordenadasFactura.objects.get(usuario_id=2)

    # INICIO PRIMERA IMPRESION
    # y_1ra_imp = float(14.05)

    p.drawString(coor.numero_1x * cm, float(coor.numero_1y) * cm, unicode(nueva_factura.numero))

    fecha_str = unicode(nueva_factura.fecha)
    fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))

    p.drawString(coor.fecha_1x * cm, float(coor.fecha_1y) * cm, fecha)
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

    if nueva_factura.cliente.ruc is None:
        nueva_factura.cliente.ruc = ""
    p.drawString(coor.ruc_1x * cm, float(coor.ruc_1y) * cm, unicode(nueva_factura.cliente.ruc))
    p.drawString(coor.telefono_1x * cm, float(coor.telefono_1y) * cm, unicode(nueva_factura.cliente.telefono_laboral))
    direccion_1_str = (nueva_factura.cliente.direccion_cobro[:56] + '..') if len(
        nueva_factura.cliente.direccion_cobro) > 56 else nueva_factura.cliente.direccion_cobro
    p.drawString(coor.direccion_1x * cm, float(coor.direccion_1y) * cm, unicode(direccion_1_str))
    p.drawString(coor.superficie_1x * cm, float(coor.superficie_1y) * cm, unicode(lote_id.superficie) + "  mts2")
    p.drawString(coor.cta_cte_ctral_1x * cm, float(coor.cta_cte_ctral_1y) * cm,
                 unicode(lote_id.cuenta_corriente_catastral))

    # Se obtienen la lista de los detalles
    lista_detalles = json.loads(nueva_factura.detalle)
    detalles = []
    pos_y = float(coor.cantidad_1y + 0.5)
    exentas = 0
    iva10 = 0
    iva5 = 0
    # total_iva_10 = 0
    # total_iva_5 = 0
    # total_iva = 0
    # total_gral = 0
    total_venta = 0
    for key, value in sorted(lista_detalles.iteritems()):
        detalle = {
            'item': key,
            'cantidad': value['cantidad']
        }
        p.drawString(coor.cantidad_1x * cm, float(pos_y - 0.5) * cm, unicode(detalle['cantidad']))
        detalle['concepto'] = value['concepto']
        p.drawString(coor.descripcion_1x * cm, float(pos_y - 0.5) * cm, unicode(detalle['concepto']))
        detalle['precio_unitario'] = int(value['precio_unitario'])
        p.drawString(coor.precio_1x * cm, float(pos_y - 0.5) * cm,
                     unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
        total_venta += int(detalle['cantidad']) * int(detalle['precio_unitario'])
        detalle['exentas'] = int(value['exentas'])
        p.drawString(coor.exentas_1x * cm, float(pos_y - 0.5) * cm,
                     unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
        if detalle['exentas'] != '':
            exentas += int(detalle['exentas'])
        detalle['iva_5'] = int(value['iva_5'])
        p.drawString(coor.iva5_1x * cm, float(pos_y - 0.5) * cm,
                     unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
        if detalle['iva_5'] != '':
            iva5 += int(detalle['iva_5'])
        detalle['iva_10'] = int(value['iva_10'])
        p.drawString(coor.iva10_1x * cm, float(pos_y - 0.5) * cm,
                     unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
        if detalle['iva_10'] != '':
            iva10 += int(detalle['iva_10'])
        pos_y -= 0.5
        detalles.append(detalle)
    cantidad = 4 - len(detalles)
    pos_y -= (0.5 * cantidad)
    p.drawString(coor.sub_exentas_1x * cm, float(coor.sub_exentas_1y) * cm,
                 unicode('{:,}'.format(exentas).replace(",", ".")))
    p.drawString(coor.sub_iva5_1x * cm, float(coor.sub_iva5_1y) * cm, unicode('{:,}'.format(iva5).replace(",", ".")))
    p.drawString(coor.sub_iva10_1x * cm, float(coor.sub_iva10_1y) * cm, unicode('{:,}'.format(iva10).replace(",", ".")))
    pos_y -= 0.5
    p.drawString(coor.total_a_pagar_exentas_iva5_1x * cm, float(coor.total_a_pagar_exentas_iva5_1y) * cm,
                 unicode('{:,}'.format(exentas + iva5).replace(",", ".")))
    p.drawString(coor.total_venta_1x * cm, float(coor.total_venta_1y) * cm,
                 unicode('{:,}'.format(total_venta).replace(",", ".")))
    pos_y -= 1.5
    numalet = num2words(int(total_venta), lang='es')
    p.drawString(coor.total_a_pagar_letra_1x * cm, float(coor.total_a_pagar_letra_1y) * cm, unicode(numalet))
    p.drawString(coor.total_a_pagar_num_1x * cm, float(coor.total_a_pagar_num_1y) * cm,
                 unicode('{:,}'.format(total_venta).replace(",", ".")))
    total_iva_10 = int(iva10 / 11)
    total_iva_5 = int(iva5 / 21)
    total_iva = total_iva_10 + total_iva_5
    pos_y -= 0.5
    p.drawString(coor.liq_iva5_1x * cm, float(coor.liq_iva5_1y) * cm,
                 unicode('{:,}'.format(total_iva_5).replace(",", ".")))
    p.drawString(coor.liq_iva10_1x * cm, float(coor.liq_iva10_1y) * cm,
                 unicode('{:,}'.format(total_iva_10).replace(",", ".")))
    p.drawString(coor.liq_total_iva_1x * cm, float(coor.liq_total_iva_1y) * cm,
                 unicode('{:,}'.format(total_iva).replace(",", ".")))
    # FIN PRIMERA IMPRESION
    # ----------------------------------------------------------------------------------------------------------------
    # INICIO SEGUNDA IMPRESION
    p.drawString(coor.numero_2x * cm, float(coor.numero_2y) * cm, unicode(nueva_factura.numero))

    p.drawString(coor.fecha_2x * cm, float(coor.fecha_2y) * cm, fecha)
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

    if nueva_factura.cliente.ruc is None:
        nueva_factura.cliente.ruc = ""
    p.drawString(coor.ruc_2x * cm, float(coor.ruc_2y) * cm, unicode(nueva_factura.cliente.ruc))
    p.drawString(coor.telefono_2x * cm, float(coor.telefono_2y) * cm, unicode(nueva_factura.cliente.telefono_laboral))
    direccion_2_str = (nueva_factura.cliente.direccion_cobro[:56] + '..') if len(
        nueva_factura.cliente.direccion_cobro) > 56 else nueva_factura.cliente.direccion_cobro
    p.drawString(coor.direccion_2x * cm, float(coor.direccion_2y) * cm, unicode(direccion_2_str))
    p.drawString(coor.superficie_2x * cm, float(coor.superficie_2y) * cm, unicode(lote_id.superficie) + "  mts2")
    p.drawString(coor.cta_cte_ctral_2x * cm, float(coor.cta_cte_ctral_2y) * cm,
                 unicode(lote_id.cuenta_corriente_catastral))

    # Se obtienen la lista de los detalles
    lista_detalles = json.loads(nueva_factura.detalle)
    detalles = []
    pos_y = float(coor.cantidad_2y + 0.5)
    exentas = 0
    iva10 = 0
    iva5 = 0
    # total_iva_10 = 0
    # total_iva_5 = 0
    # total_iva = 0
    # total_gral = 0
    total_venta = 0
    for key, value in sorted(lista_detalles.iteritems()):
        detalle = {
            'item': key,
            'cantidad': value['cantidad']
        }
        p.drawString(coor.cantidad_2x * cm, float(pos_y - 0.5) * cm, unicode(detalle['cantidad']))
        detalle['concepto'] = value['concepto']
        p.drawString(coor.descripcion_2x * cm, float(pos_y - 0.5) * cm, unicode(detalle['concepto']))
        detalle['precio_unitario'] = int(value['precio_unitario'])
        p.drawString(coor.precio_2x * cm, float(pos_y - 0.5) * cm,
                     unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
        total_venta += int(detalle['cantidad']) * int(detalle['precio_unitario'])
        detalle['exentas'] = int(value['exentas'])
        p.drawString(coor.exentas_2x * cm, float(pos_y - 0.5) * cm,
                     unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
        if detalle['exentas'] != '':
            exentas += int(detalle['exentas'])
        detalle['iva_5'] = int(value['iva_5'])
        p.drawString(coor.iva5_2x * cm, float(pos_y - 0.5) * cm,
                     unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
        if detalle['iva_5'] != '':
            iva5 += int(detalle['iva_5'])
        detalle['iva_10'] = int(value['iva_10'])
        p.drawString(coor.iva10_2x * cm, float(pos_y - 0.5) * cm,
                     unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
        if detalle['iva_10'] != '':
            iva10 += int(detalle['iva_10'])
        pos_y -= 0.5
        detalles.append(detalle)
    cantidad = 4 - len(detalles)
    pos_y -= (0.5 * cantidad)
    p.drawString(coor.sub_exentas_2x * cm, float(coor.sub_exentas_2y) * cm,
                 unicode('{:,}'.format(exentas).replace(",", ".")))
    p.drawString(coor.sub_iva5_2x * cm, float(coor.sub_iva5_2y) * cm, unicode('{:,}'.format(iva5).replace(",", ".")))
    p.drawString(coor.sub_iva10_2x * cm, float(coor.sub_iva10_2y) * cm, unicode('{:,}'.format(iva10).replace(",", ".")))
    pos_y -= 0.5
    p.drawString(coor.total_a_pagar_exentas_iva5_2x * cm, float(coor.total_a_pagar_exentas_iva5_2y) * cm,
                 unicode('{:,}'.format(exentas + iva5).replace(",", ".")))
    p.drawString(coor.total_venta_2x * cm, float(coor.total_venta_2y) * cm,
                 unicode('{:,}'.format(total_venta).replace(",", ".")))
    pos_y -= 1.5
    numalet = num2words(int(total_venta), lang='es')
    p.drawString(coor.total_a_pagar_letra_2x * cm, float(coor.total_a_pagar_letra_2y) * cm, unicode(numalet))
    p.drawString(coor.total_a_pagar_num_2x * cm, float(coor.total_a_pagar_num_2y) * cm,
                 unicode('{:,}'.format(total_venta).replace(",", ".")))
    total_iva_10 = int(iva10 / 11)
    total_iva_5 = int(iva5 / 21)
    total_iva = total_iva_10 + total_iva_5
    pos_y -= 0.5
    p.drawString(coor.liq_iva5_2x * cm, float(coor.liq_iva5_2y) * cm,
                 unicode('{:,}'.format(total_iva_5).replace(",", ".")))
    p.drawString(coor.liq_iva10_2x * cm, float(coor.liq_iva10_2y) * cm,
                 unicode('{:,}'.format(total_iva_10).replace(",", ".")))
    p.drawString(coor.liq_total_iva_2x * cm, float(coor.liq_total_iva_2y) * cm,
                 unicode('{:,}'.format(total_iva).replace(",", ".")))
    # FIN SEGUNDA IMPRESION

    p.showPage()
    p.save()
    return response


def crear_json_print_object(factura, manzana, lote_id, usuario, fraccion=None):
    # Obtener las coordenadas de impresion de la factura
    try:
        coor = CoordenadasFactura.objects.get(usuario=usuario)
        conf = Configuraciones.objects.get(codigo_empresa=CODIGO_DE_EMPRESA)
    except Exception as e:
        logging.error('Failed.', exc_info=e)
        coor = CoordenadasFactura.objects.get(usuario_id=2)

    lineas = []

    # nros de facturas
    linea = {
        "valor": factura.numero,
        "coord_x": int(coor.numero_1x * cm),
        "coord_y": int(coor.numero_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": factura.numero,
        "coord_x": int(coor.numero_2x * cm),
        "coord_y": int(coor.numero_2y * cm)
    }
    lineas.append(linea)

    # fechas
    fecha_str = unicode(factura.fecha)
    fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
    linea = {
        "valor": unicode(fecha),
        "coord_x": int(coor.fecha_1x * cm),
        "coord_y": int(coor.fecha_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": unicode(fecha),
        "coord_x": int(coor.fecha_2x * cm),
        "coord_y": int(coor.fecha_2y * cm)
    }
    lineas.append(linea)

    # nombres clientes
    linea = {
        "valor": factura.cliente.nombres + " " + factura.cliente.apellidos,
        "coord_x": int(coor.nombre_1x * cm),
        "coord_y": int(coor.nombre_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": factura.cliente.nombres + " " + factura.cliente.apellidos,
        "coord_x": int(coor.nombre_2x * cm),
        "coord_y": int(coor.nombre_2y * cm)
    }
    lineas.append(linea)

    # fraccion
    if manzana != 0:
        linea = {
            "valor": manzana.fraccion.nombre,
            "coord_x": int(coor.fraccion_1x * cm),
            "coord_y": int(coor.fraccion_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": manzana.fraccion.nombre,
            "coord_x": int(coor.fraccion_2x * cm),
            "coord_y": int(coor.fraccion_2y * cm)
        }
        lineas.append(linea)

        # manzana
        linea = {
            "valor": manzana.nro_manzana,
            "coord_x": int(coor.manzana_1x * cm),
            "coord_y": int(coor.manzana_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": manzana.nro_manzana,
            "coord_x": int(coor.manzana_2x * cm),
            "coord_y": int(coor.manzana_2y * cm)
        }
        lineas.append(linea)
    else:
        linea = {
            "valor": fraccion.nombre,
            "coord_x": int(coor.fraccion_1x * cm),
            "coord_y": int(coor.fraccion_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": fraccion.nombre,
            "coord_x": int(coor.fraccion_2x * cm),
            "coord_y": int(coor.fraccion_2y * cm)
        }
        lineas.append(linea)

    # lote
    if lote_id != 0:
        linea = {
            "valor": lote_id.nro_lote,
            "coord_x": int(coor.lote_1x * cm),
            "coord_y": int(coor.lote_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": lote_id.nro_lote,
            "coord_x": int(coor.lote_2x * cm),
            "coord_y": int(coor.lote_2y * cm)
        }
        lineas.append(linea)

        # superficie
        linea = {
            "valor": unicode(lote_id.superficie) + "  mts2",
            "coord_x": int(coor.superficie_1x * cm),
            "coord_y": int(coor.superficie_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": unicode(lote_id.superficie) + "  mts2",
            "coord_x": int(coor.superficie_2x * cm),
            "coord_y": int(coor.superficie_2y * cm)
        }
        lineas.append(linea)

        # Cta Cte catastral
        linea = {
            "valor": lote_id.cuenta_corriente_catastral,
            "coord_x": int(coor.cta_cte_ctral_1x * cm),
            "coord_y": int(coor.cta_cte_ctral_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": lote_id.cuenta_corriente_catastral,
            "coord_x": int(coor.cta_cte_ctral_2x * cm),
            "coord_y": int(coor.cta_cte_ctral_2y * cm)
        }
        lineas.append(linea)

        #Sucursal
        linea = {
            "valor": factura.lote.manzana.fraccion.sucursal.nombre,
            "coord_x": int(coor.sucursal_1x * cm),
            "coord_y": int(coor.sucursal_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": factura.lote.manzana.fraccion.sucursal.nombre,
            "coord_x": int(coor.sucursal_2x * cm),
            "coord_y": int(coor.sucursal_2y * cm)
        }
        lineas.append(linea)
    else:
        # Sucursal
        linea = {
            "valor": fraccion.sucursal.nombre,
            "coord_x": int(coor.sucursal_1x * cm),
            "coord_y": int(coor.sucursal_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": fraccion.sucursal.nombre,
            "coord_x": int(coor.sucursal_2x * cm),
            "coord_y": int(coor.sucursal_2y * cm)
        }
        lineas.append(linea)

    # if nueva_factura.cliente.ruc == None:
    #     nueva_factura.cliente.ruc = ""
    # ruc
    linea = {
        "valor": factura.cliente.ruc,
        "coord_x": int(coor.ruc_1x * cm),
        "coord_y": int(coor.ruc_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": factura.cliente.ruc,
        "coord_x": int(coor.ruc_2x * cm),
        "coord_y": int(coor.ruc_2y * cm)
    }
    lineas.append(linea)

    # direccion
    linea = {
        "valor": (factura.cliente.direccion_cobro[:56] + '..') if len(
            factura.cliente.direccion_cobro) > 56 else factura.cliente.direccion_cobro,
        "coord_x": int(coor.direccion_1x * cm),
        "coord_y": int(coor.direccion_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": (factura.cliente.direccion_cobro[:56] + '..') if len(
            factura.cliente.direccion_cobro) > 56 else factura.cliente.direccion_cobro,
        "coord_x": int(coor.direccion_2x * cm),
        "coord_y": int(coor.direccion_2y * cm)}
    lineas.append(linea)

    # CONTADO O CREDITO
    if factura.tipo == 'co':
        linea = {
            "valor": 'X',
            "coord_x": int(coor.contado_1x * cm),
            "coord_y": int(coor.contado_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": 'X',
            "coord_x": int(coor.contado_2x * cm),
            "coord_y": int(coor.contado_2y * cm)
        }
        lineas.append(linea)
    else:
        linea = {
            "valor": 'X',
            "coord_x": int(coor.credito_1x * cm),
            "coord_y": int(coor.credito_1y * cm)
        }
        lineas.append(linea)

        linea = {
            "valor": 'X',
            "coord_x": int(coor.credito_2x * cm),
            "coord_y": int(coor.credito_2y * cm)
        }
        lineas.append(linea)

    # telefono
    linea = {
        "valor": factura.cliente.telefono_laboral,
        "coord_x": int(coor.telefono_1x * cm),
        "coord_y": int(coor.telefono_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": factura.cliente.telefono_laboral,
        "coord_x": int(coor.telefono_2x * cm),
        "coord_y": int(coor.telefono_2y * cm)
    }
    lineas.append(linea)

    if conf.copias_facturas == 3:
        # nros de facturas
        linea = {
            "valor": factura.numero,
            "coord_x": int(coor.numero_3x * cm),
            "coord_y": int(coor.numero_3y * cm)
        }
        lineas.append(linea)

        # fechas
        fecha_str = unicode(factura.fecha)
        fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
        linea = {
            "valor": unicode(fecha),
            "coord_x": int(coor.fecha_3x * cm),
            "coord_y": int(coor.fecha_3y * cm)
        }
        lineas.append(linea)

        # nombres clientes
        linea = {
            "valor": factura.cliente.nombres + " " + factura.cliente.apellidos,
            "coord_x": int(coor.nombre_3x * cm),
            "coord_y": int(coor.nombre_3y * cm)
        }
        lineas.append(linea)

        # fraccion
        if manzana != 0:
            linea = {
                "valor": manzana.fraccion.nombre,
                "coord_x": int(coor.fraccion_3x * cm),
                "coord_y": int(coor.fraccion_3y * cm)
            }
            lineas.append(linea)

            # manzana
            linea = {
                "valor": manzana.nro_manzana,
                "coord_x": int(coor.manzana_3x * cm),
                "coord_y": int(coor.manzana_3y * cm)
            }
            lineas.append(linea)

        # lote
        if lote_id != 0:
            linea = {
                "valor": lote_id.nro_lote,
                "coord_x": int(coor.lote_3x * cm),
                "coord_y": int(coor.lote_3y * cm)
            }
            lineas.append(linea)

            # superficie
            linea = {
                "valor": unicode(lote_id.superficie) + "  mts2",
                "coord_x": int(coor.superficie_3x * cm),
                "coord_y": int(coor.superficie_3y * cm)
            }
            lineas.append(linea)

            # Cta Cte catastral
            linea = {
                "valor": lote_id.cuenta_corriente_catastral,
                "coord_x": int(coor.cta_cte_ctral_3x * cm),
                "coord_y": int(coor.cta_cte_ctral_3y * cm)
            }
            lineas.append(linea)

        # if nueva_factura.cliente.ruc == None:
        #     nueva_factura.cliente.ruc = ""
        # ruc
        linea = {
            "valor": factura.cliente.ruc,
            "coord_x": int(coor.ruc_3x * cm),
            "coord_y": int(coor.ruc_3y * cm)
        }
        lineas.append(linea)

        # direccion
        linea = {
            "valor": (factura.cliente.direccion_cobro[:56] + '..') if len(
                factura.cliente.direccion_cobro) > 56 else factura.cliente.direccion_cobro,
            "coord_x": int(coor.direccion_3x * cm),
            "coord_y": int(coor.direccion_3y * cm)}
        lineas.append(linea)

        # CONTADO O CREDITO
        if factura.tipo == 'co':
            linea = {
                "valor": 'X',
                "coord_x": int(coor.contado_3x * cm),
                "coord_y": int(coor.contado_3y * cm)
            }
            lineas.append(linea)
        else:

            linea = {
                "valor": 'X',
                "coord_x": int(coor.credito_3x * cm),
                "coord_y": int(coor.credito_3y * cm)
            }
            lineas.append(linea)

        # telefono
        linea = {
            "valor": factura.cliente.telefono_laboral,
            "coord_x": int(coor.telefono_3x * cm),
            "coord_y": int(coor.telefono_3y * cm)
        }
        lineas.append(linea)

    # ahora debo setear los detalles, para ello debo de recorrer los mismos,
    # Se obtienen la lista de los detalles
    lista_detalles = json.loads(factura.detalle)
    # detalles = []
    pos_x = float(coor.cantidad_1y + 0.5)
    pos_y = float(coor.cantidad_2y + 0.5)
    pos_z = float(coor.cantidad_3y + 0.5)
    exentas = 0
    iva10 = 0
    iva5 = 0
    # total_iva_10 = 0
    # total_iva_5 = 0
    # total_iva = 0
    # total_gral = 0
    total_venta = 0
    for key, value in sorted(lista_detalles.iteritems()):
        # cantidad
        linea = {
            "valor": unicode(value['cantidad']),
            "coord_x": int(coor.cantidad_1x * cm),
            "coord_y": int((pos_x - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.cantidad_1y * cm)
        lineas.append(linea)

        linea = {
            "valor": unicode(value['cantidad']),
            "coord_x": int(coor.cantidad_2x * cm),
            "coord_y": int((pos_y - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.cantidad_2y * cm)
        lineas.append(linea)

        # conceptos, descripcion
        linea = {
            "valor": unicode(value['concepto']),
            "coord_x": int(coor.descripcion_1x * cm),
            "coord_y": int((pos_x - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.descripcion_1x * cm)
        lineas.append(linea)

        linea = {
            "valor": unicode(value['concepto']),
            "coord_x": int(coor.descripcion_2x * cm),
            "coord_y": int((pos_y - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.descripcion_2y * cm)
        lineas.append(linea)

        # precios unitarios
        linea = {
            "valor": unicode('{:,}'.format(int(value['precio_unitario']))),
            "coord_x": int(coor.precio_1x * cm),
            "coord_y": int((pos_x - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.precio_1y * cm)
        lineas.append(linea)

        linea = {
            "valor": unicode('{:,}'.format(int(value['precio_unitario']))),
            "coord_x": int(coor.precio_2x * cm),
            "coord_y": int((pos_y - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.precio_2y * cm)
        lineas.append(linea)

        # exentas
        linea = {
            "valor": unicode('{:,}'.format(int(value['exentas']))),
            "coord_x": int(coor.exentas_1x * cm),
            "coord_y": int((pos_x - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.exentas_1y * cm)
        lineas.append(linea)

        linea = {
            "valor": unicode('{:,}'.format(int(value['exentas']))),
            "coord_x": int(coor.exentas_2x * cm),
            "coord_y": int((pos_y - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.exentas_2y * cm)
        lineas.append(linea)

        # iva 5
        linea = {
            "valor": unicode('{:,}'.format(int(value['iva_5']))),
            "coord_x": int(coor.iva5_1x * cm),
            "coord_y": int((pos_x - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.iva5_1y * cm)
        lineas.append(linea)

        linea = {
            "valor": unicode('{:,}'.format(int(value['iva_5']))),
            "coord_x": int(coor.iva5_2x * cm),
            "coord_y": int((pos_y - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.iva5_2y * cm)
        lineas.append(linea)

        # iva 10
        linea = {
            "valor": unicode('{:,}'.format(int(value['iva_10']))),
            "coord_x": int(coor.iva10_1x * cm),
            "coord_y": int((pos_x - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.iva10_1y * cm)
        lineas.append(linea)

        linea = {
            "valor": unicode('{:,}'.format(int(value['iva_10']))),
            "coord_x": int(coor.iva10_2x * cm),
            "coord_y": int((pos_y - 0.5) * cm)
        }
        # linea["coord_y"] = int(coor.iva10_2y * cm)
        lineas.append(linea)

        total_venta += int(value['cantidad']) * int(value['precio_unitario'])
        if value['exentas'] != '':
            exentas += int(value['exentas'])
        value['iva_5'] = int(value['iva_5'])
        # p.drawString(coor.iva5_2x * cm, float(pos_y - 0.5) * cm, unicode(
        # '{:,}'.format(value['iva_5']).replace(",", ".")))
        if value['iva_5'] != '':
            iva5 += int(value['iva_5'])
        value['iva_10'] = int(value['iva_10'])
        # p.drawString(coor.iva10_2x * cm, float(pos_y - 0.5) * cm, unicode(
        # '{:,}'.format(detalle['iva_10']).replace(",", ".")))
        if value['iva_10'] != '':
            iva10 += int(value['iva_10'])

        if conf.copias_facturas == 3:
            # cantidad
            linea = {
                "valor": unicode(value['cantidad']),
                "coord_x": int(coor.cantidad_3x * cm),
                "coord_y": int((pos_z - 0.5) * cm)
            }
            # linea["coord_y"] = int(coor.cantidad_2y * cm)
            lineas.append(linea)

            # conceptos, descripcion
            linea = {
                "valor": unicode(value['concepto']),
                "coord_x": int(coor.descripcion_3x * cm),
                "coord_y": int((pos_z - 0.5) * cm)
            }
            # linea["coord_y"] = int(coor.descripcion_2y * cm)
            lineas.append(linea)

            # precios unitarios
            linea = {
                "valor": unicode('{:,}'.format(int(value['precio_unitario']))),
                "coord_x": int(coor.precio_3x * cm),
                "coord_y": int((pos_z - 0.5) * cm)
            }
            # linea["coord_y"] = int(coor.precio_2y * cm)
            lineas.append(linea)

            # exentas
            linea = {
                "valor": unicode('{:,}'.format(int(value['exentas']))),
                "coord_x": int(coor.exentas_3x * cm),
                "coord_y": int((pos_z - 0.5) * cm)
            }
            # linea["coord_y"] = int(coor.exentas_2y * cm)
            lineas.append(linea)

            # iva 5
            linea = {
                "valor": unicode('{:,}'.format(int(value['iva_5']))),
                "coord_x": int(coor.iva5_3x * cm),
                "coord_y": int((pos_z - 0.5) * cm)
            }
            # linea["coord_y"] = int(coor.iva5_2y * cm)
            lineas.append(linea)

            # iva 10
            linea = {
                "valor": unicode('{:,}'.format(int(value['iva_10']))),
                "coord_x": int(coor.iva10_3x * cm),
                "coord_y": int((pos_z - 0.5) * cm)
            }
            # linea["coord_y"] = int(coor.iva10_2y * cm)
            lineas.append(linea)

        pos_x += 0.5
        pos_y += 0.5
        pos_z += 0.5

    total_iva_10 = int(iva10 / 11)
    total_iva_5 = int(iva5 / 21)
    total_iva = total_iva_10 + total_iva_5

    # sub-exentas
    linea = {
        "valor": unicode('{:,}'.format(exentas)),
        "coord_x": int(coor.sub_exentas_1x * cm),
        "coord_y": int(coor.sub_exentas_1y * cm)
    }
    # linea["valor"] = unicode(value['exentas'])
    lineas.append(linea)

    linea = {
        "valor": unicode('{:,}'.format(exentas)),
        "coord_x": int(coor.sub_exentas_2x * cm),
        "coord_y": int(coor.sub_exentas_2y * cm)
    }
    # linea["valor"] = unicode(value['exentas'])
    lineas.append(linea)

    # sub-iva 5
    linea = {
        "valor": unicode('{:,}'.format(iva5)),
        "coord_x": int(coor.sub_iva5_1x * cm),
        "coord_y": int(coor.sub_iva5_1y * cm)
    }
    # linea["valor"] = unicode(value['iva_5'])
    lineas.append(linea)

    linea = {
        "valor": unicode('{:,}'.format(iva5)),
        "coord_x": int(coor.sub_iva5_2x * cm),
        "coord_y": int(coor.sub_iva5_2y * cm)
    }
    # linea["valor"] = unicode(value['iva_5'])
    lineas.append(linea)

    # sub-iva 10
    linea = {
        "valor": unicode('{:,}'.format(iva10)),
        "coord_x": int(coor.sub_iva10_1x * cm),
        "coord_y": int(coor.sub_iva10_1y * cm)
    }
    # linea["valor"] = unicode(value['iva_10'])
    lineas.append(linea)

    linea = {
        "valor": unicode('{:,}'.format(iva10)),
        "coord_x": unicode('{:,}'.format(int(coor.sub_iva10_2x * cm))),
        "coord_y": unicode('{:,}'.format(int(coor.sub_iva10_2y * cm)))
    }
    # linea["valor"] = unicode(value['iva_10'])
    lineas.append(linea)

    # total_venta
    linea = {
        "valor": unicode('{:,}'.format(iva10)),
        "coord_x": int(coor.total_venta_1x * cm),
        "coord_y": int(coor.total_venta_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": unicode('{:,}'.format(iva10)),
        "coord_x": int(coor.total_venta_2x * cm),
        "coord_y": int(coor.total_venta_2y * cm)
    }
    lineas.append(linea)

    # total_a_pagar_letra
    numalet = num2words(int(total_venta), lang='es')
    linea = {
        "valor": unicode(numalet),
        "coord_x": int(coor.total_a_pagar_letra_1x * cm),
        "coord_y": int(coor.total_a_pagar_letra_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": unicode(numalet),
        "coord_x": int(coor.total_a_pagar_letra_2x * cm),
        "coord_y": int(coor.total_a_pagar_letra_2y * cm)
    }
    lineas.append(linea)

    # total_a_pagar_nro
    linea = {
        "valor": unicode('{:,}'.format(total_venta)),
        "coord_x": int(coor.total_a_pagar_num_1x * cm),
        "coord_y": int(coor.total_a_pagar_num_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": unicode('{:,}'.format(total_venta)),
        "coord_x": int(coor.total_a_pagar_num_2x * cm),
        "coord_y": int(coor.total_a_pagar_num_2y * cm)
    }
    lineas.append(linea)

    # total_a_pagar_exentas_iva5
    linea = {
        "valor": unicode('{:,}'.format(exentas + iva5)),
        "coord_x": int(coor.total_a_pagar_exentas_iva5_1x * cm),
        "coord_y": int(coor.total_a_pagar_exentas_iva5_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": unicode('{:,}'.format(exentas + iva5)),
        "coord_x": int(coor.total_a_pagar_exentas_iva5_2x * cm),
        "coord_y": int(coor.total_a_pagar_exentas_iva5_2y * cm)
    }
    lineas.append(linea)

    # total_iva_5
    linea = {"valor": unicode('{:,}'.format(total_iva_5)), "coord_x": int(coor.liq_iva5_1x * cm),
             "coord_y": int(coor.liq_iva5_1y * cm)}
    lineas.append(linea)

    linea = {"valor": unicode('{:,}'.format(total_iva_5)), "coord_x": int(coor.liq_iva5_2x * cm),
             "coord_y": int(coor.liq_iva5_2y * cm)}
    lineas.append(linea)

    # total_iva_10
    linea = {
        "valor": unicode('{:,}'.format(total_iva_10)),
        "coord_x": int(coor.liq_iva10_1x * cm),
        "coord_y": int(coor.liq_iva10_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": unicode('{:,}'.format(total_iva_10)),
        "coord_x": int(coor.liq_iva10_2x * cm),
        "coord_y": int(coor.liq_iva10_2y * cm)
    }
    lineas.append(linea)

    # total_iva
    linea = {
        "valor": unicode('{:,}'.format(total_iva)),
        "coord_x": int(coor.liq_total_iva_1x * cm),
        "coord_y": int(coor.liq_total_iva_1y * cm)
    }
    lineas.append(linea)

    linea = {
        "valor": unicode('{:,}'.format(total_iva)),
        "coord_x": int(coor.liq_total_iva_2x * cm),
        "coord_y": int(coor.liq_total_iva_2y * cm)
    }
    lineas.append(linea)

    if conf.copias_facturas == 3:
        # sub-exentas
        linea = {
            "valor": unicode('{:,}'.format(exentas)),
            "coord_x": int(coor.sub_exentas_3x * cm),
            "coord_y": int(coor.sub_exentas_3y * cm)
        }
        # linea["valor"] = unicode(value['exentas'])
        lineas.append(linea)

        # sub-iva 5
        linea = {
            "valor": unicode('{:,}'.format(iva5)),
            "coord_x": int(coor.sub_iva5_3x * cm),
            "coord_y": int(coor.sub_iva5_3y * cm)
        }
        # linea["valor"] = unicode(value['iva_5'])
        lineas.append(linea)

        # sub-iva 10
        linea = {
            "valor": unicode('{:,}'.format(iva10)),
            "coord_x": unicode('{:,}'.format(int(coor.sub_iva10_3x * cm))),
            "coord_y": unicode('{:,}'.format(int(coor.sub_iva10_3y * cm)))
        }
        # linea["valor"] = unicode(value['iva_10'])
        lineas.append(linea)

        # total_venta
        linea = {
            "valor": unicode('{:,}'.format(iva10)),
            "coord_x": int(coor.total_venta_3x * cm),
            "coord_y": int(coor.total_venta_3y * cm)
        }
        lineas.append(linea)

        # total_a_pagar_letra
        numalet = num2words(int(total_venta), lang='es')
        linea = {
            "valor": unicode(numalet),
            "coord_x": int(coor.total_a_pagar_letra_3x * cm),
            "coord_y": int(coor.total_a_pagar_letra_3y * cm)
        }
        lineas.append(linea)

        # total_a_pagar_nro
        linea = {
            "valor": unicode('{:,}'.format(total_venta)),
            "coord_x": int(coor.total_a_pagar_num_3x * cm),
            "coord_y": int(coor.total_a_pagar_num_3y * cm)
        }
        lineas.append(linea)

        # total_a_pagar_exentas_iva5
        linea = {
            "valor": unicode('{:,}'.format(exentas + iva5)),
            "coord_x": int(coor.total_a_pagar_exentas_iva5_3x * cm),
            "coord_y": int(coor.total_a_pagar_exentas_iva5_3y * cm)
        }
        lineas.append(linea)

        # total_iva_5
        linea = {"valor": unicode('{:,}'.format(total_iva_5)), "coord_x": int(coor.liq_iva5_3x * cm),
                 "coord_y": int(coor.liq_iva5_3y * cm)}
        lineas.append(linea)

        # total_iva_10
        linea = {
            "valor": unicode('{:,}'.format(total_iva_10)),
            "coord_x": int(coor.liq_iva10_3x * cm),
            "coord_y": int(coor.liq_iva10_3y * cm)
        }
        lineas.append(linea)

        # total_iva
        linea = {
            "valor": unicode('{:,}'.format(total_iva)),
            "coord_x": int(coor.liq_total_iva_3x * cm),
            "coord_y": int(coor.liq_total_iva_3y * cm)
        }
        lineas.append(linea)


    response = json.dumps(({"tipoPapel": "A4", "fontSize": unicode(conf.tamanho_letra),
                            "lineas": lineas
                            }), separators=(',', ':'))

    return response


def obtener_cantidad_cuotas_pagadas(pago):
    # id_pago = pago.id
    fecha_pago = pago.fecha_de_pago

    id_venta = pago.venta.id
    fecha_venta = pago.venta.fecha_de_venta

    #pagos = PagoDeCuotas.objects.filter(venta=id_venta, id__lte=pago.id, fecha_de_pago__range=(fecha_venta, fecha_pago)).order_by(
    #    'fecha_de_pago', 'id').aggregate(Sum('nro_cuotas_a_pagar'))

    pagos = PagoDeCuotas.objects.filter(venta=id_venta,
                                        fecha_de_pago__range=(fecha_venta, fecha_pago)).order_by(
        'fecha_de_pago', 'id').aggregate(Sum('nro_cuotas_a_pagar'))

    print PagoDeCuotas.objects.filter(venta=id_venta, fecha_de_pago__range=(fecha_venta, fecha_pago)).order_by(
        'fecha_de_pago', 'id').query
    cantidad_pagos = pagos['nro_cuotas_a_pagar__sum']
    return cantidad_pagos


def lote_libre(lote_id):
    # esta_libre = True
    # TODO: Hacer el analisis exaustivo para ver si un lote esta libre o no
    # Contemplar transferencias, reservas, transferencias y cambios.

    if lote_id == 8608:
        print 'hola'

    venta = get_ultima_venta_no_recuperada(lote_id)

    if venta is not None:
        # cuotas_detalles = get_cuotas_detail_by_lote(str(lote_id))
        esta_libre = False
    else:
        # sino esta vendida pero esta recuperada, tabla "recuperada" de la nueva version
        object_list = Reserva.objects.filter(lote_id=lote_id)
        if object_list:
            esta_libre = False
        elif lote_reservado_segun_estado(lote_id):
            esta_libre = False
        elif Lote.objects.get(pk=lote_id).estado == '3':
            esta_libre = False
        else:
            esta_libre = True

    return esta_libre


def lote_reservado_segun_estado(lote_id):
    esta_reservado = False
    # Funcion que verifica el estado de un lote por el campo "estado", para los importados del sistema anterior

    # QUERY PARA TRAER EL LOTE EN CUESTION
    query = '''SELECT * FROM "principal_lote" WHERE "principal_lote"."id" = (%s)'''
    cursor = connection.cursor()
    cursor.execute(query, [lote_id])
    results = cursor.fetchall()
    # si el result no encuentra nada retorna una lista vacia y eso contemplamos para que no intente obtener el estado
    if len(results) > 0:
        # Obtenemos el estado y comparamos con 2 a partir del result
        if results[0][8] == '2':
            esta_reservado = True
    return esta_reservado


def obtener_lotes_disponbiles(sucursal, order_by, fracciones_a_excluir=None):
    lotes_list = []
    # FRACCIONES A EXCLUIR
    if fracciones_a_excluir is None:
        fracciones_a_excluir = []
    # SE OBTIENEN TODOS LOS LOTES DE TODAS LAS FRACCIONES DE LA SUCURSAL
    fracciones = Fraccion.objects.filter(sucursal=sucursal)

    for fraccion in fracciones:
        # Se verifica si la fraccion no esta excluida de la busqueda
        if unicode(fraccion.id) not in fracciones_a_excluir:
            # ORDENAMIENTO POR BASE DE DATOS.
            if order_by == "codigo":
                lotes_fraccion = Lote.objects.filter(manzana__fraccion=fraccion).order_by('codigo_paralot')
            else:
                lotes_fraccion = Lote.objects.filter(manzana__fraccion=fraccion).order_by('codigo_paralot')
                # TODO: Hacer una funcionalidad mas completa de ordenamiento
            for lote in lotes_fraccion:
                lotes_list.append(lote)

    # RECORTAR LA LISTA DE LOTES A LOS LOTES QUE ESTAN LIBRES
    lotes_list_aux = []
    for lote in lotes_list:
        # if lote_libre(lote.pk) == False:
        #     lotes_list.remove(lote)
        if lote_libre(lote.pk):
            lotes_list_aux.append(lote)

    lotes = []
    total_importe_cuotas = 0
    total_contado_fraccion = 0
    total_credito_fraccion = 0
    total_superficie_fraccion = 0
    total_lotes_fraccion = 0
    total_general_lotes = 0

    lotes_list = lotes_list_aux
    misma_fraccion = True
    for index, lote_item in enumerate(lotes_list):
        lote = {}
        # Se setean los datos de cada fila
        if misma_fraccion:
            misma_fraccion = False
            lote['misma_fraccion'] = misma_fraccion
        precio_cuota = int(math.ceil(lote_item.precio_credito / 130))
        lote['fraccion_id'] = unicode(lote_item.manzana.fraccion.id)
        lote['fraccion'] = unicode(lote_item.manzana.fraccion)
        lote['lote'] = unicode(lote_item.manzana).zfill(3) + "/" + unicode(lote_item.nro_lote).zfill(4)
        lote['superficie'] = lote_item.superficie
        lote['precio_contado'] = unicode('{:,}'.format(lote_item.precio_contado)).replace(",", ".")
        lote['precio_credito'] = unicode('{:,}'.format(lote_item.precio_credito)).replace(",", ".")
        lote['importe_cuota'] = unicode('{:,}'.format(precio_cuota)).replace(",", ".")
        lote['id'] = lote_item.id
        lote['ultimo_registro'] = False

        # Se suman los TOTALES por FRACCION
        total_superficie_fraccion += lote_item.superficie
        total_contado_fraccion += lote_item.precio_contado
        total_credito_fraccion += lote_item.precio_credito
        total_importe_cuotas += precio_cuota
        total_lotes_fraccion += 1
        total_general_lotes += 1
        # Es el ultimo lote, cerrar totales de fraccion
        if len(lotes_list) - 1 == index:
            lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".")
            lote['total_credito_fraccion'] = unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
            lote['total_contado_fraccion'] = unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
            lote['total_superficie_fraccion'] = unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
            lote['total_lotes'] = unicode('{:,}'.format(total_lotes_fraccion)).replace(",", ".")
            lote['total_general_lotes'] = unicode('{:,}'.format(total_general_lotes)).replace(",", ".")
            lote['ultimo_registro'] = True

            # Hay cambio de fraccion pero NO es el ultimo elemento todavia
        elif lote_item.manzana.fraccion.id != lotes_list[index + 1].manzana.fraccion.id:
            lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".")
            lote['total_credito_fraccion'] = unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
            lote['total_contado_fraccion'] = unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
            lote['total_superficie_fraccion'] = unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
            lote['total_lotes'] = unicode('{:,}'.format(total_lotes_fraccion)).replace(",", ".")
            # Se CERAN  los TOTALES por FRACCION
            total_importe_cuotas = 0
            total_contado_fraccion = 0
            total_credito_fraccion = 0
            total_superficie_fraccion = 0
            total_lotes_fraccion = 0
            misma_fraccion = True

        lotes.append(lote)
    return lotes


def obtener_lotes_filtrados(busqueda, tipo_busqueda, busqueda_label, fraccion_segun_estado):
    lista_lotes = []
    if tipo_busqueda == 'cedula':
        if busqueda != '':
            ventas = Venta.objects.filter(cliente_id=busqueda)
            for venta in ventas:
                lote = Lote.objects.get(pk=venta.lote_id)
                lista_lotes.append(lote)
        else:
            clientes = Cliente.objects.filter(cedula__icontains=busqueda_label)
            for cliente in clientes:
                ventas = Venta.objects.filter(cliente_id=cliente.id)
                for venta in ventas:
                    lote = Lote.objects.get(pk=venta.lote_id)
                    if lote.estado == '3':
                        lote.cliente = venta.cliente
                        lista_lotes.append(lote)

    if tipo_busqueda == 'nombre':
        if busqueda != '':
            ventas = Venta.objects.filter(cliente_id=busqueda, lote__estado='3')
            for venta in ventas:
                lote = Lote.objects.get(pk=venta.lote_id)
                if lote.estado == '3':
                    lote.cliente = venta.cliente
                    lista_lotes.append(lote)
        else:
            query = (
                '''
                SELECT id
                FROM principal_cliente
                WHERE CONCAT (UPPER(nombres), ' ', UPPER(apellidos)) LIKE UPPER('%''' + busqueda_label + '''%')
                            '''
            )

            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            # lista_clientes = []
            for r in results:
                ventas = Venta.objects.filter(cliente_id=r[0], lote__estado='3')
                for venta in ventas:
                    try:
                        lote = Lote.objects.get(pk=venta.lote_id)
                        lote.cliente = venta.cliente
                        lista_lotes.append(lote)
                    except Exception as e:
                        logging.error('Failed.', exc_info=e)
                        print "No existe el lote " + unicode(venta.lote_id) + " de la venta " + unicode(venta.id)

    if tipo_busqueda == 'codigo':
        if busqueda != '':
            lote = Lote.objects.get(pk=busqueda)
            if lote.estado == '3':
                try:
                    venta = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
                    venta = venta[0]
                    cliente = venta.cliente
                    lote.cliente = cliente
                except Exception as e:
                    logging.error('Failed.', exc_info=e)
                    lote.cliente = 'Lote de estado "vendido" sin venta asociada'
                    print "El lote vendido no esta asociado a una venta."
            lista_lotes.append(lote)
        else:
            lista_lotes = Lote.objects.filter(codigo_paralot__icontains=busqueda_label).order_by('manzana__fraccion',
                                                                                                 'manzana__nro_manzana',
                                                                                                 'nro_lote')
            for lote in lista_lotes:
                if lote.estado == '3':
                    try:
                        venta = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
                        venta = venta[0]
                        cliente = venta.cliente
                        lote.cliente = cliente
                    except Exception as e:
                        logging.error('Failed.', exc_info=e)
                        lote.cliente = 'Lote de estado "vendido" sin venta asociada'
                        print "El lote vendido no esta asociado a una venta."

    if tipo_busqueda == 'nombre_fraccion':
        if busqueda != '':
            fraccion = Fraccion.objects.filter(id=busqueda)
            # Esta manera es haciendo el query estatico, en duro, luego por cada rox ir creando un
            #  objeto Factura y luego ir agregando a una lista lotes
            lista_lotes = []
            # QUERY para traer los lotes de la fraccion en cuestio
            query = ('''SELECT principal_lote.id, nro_lote, manzana_id, precio_contado, precio_credito, superficie,
                        cuenta_corriente_catastral, boleto_nro,
                        estado, precio_costo, principal_lote.importacion_paralot, codigo_paralot
                        FROM principal_lote JOIN principal_manzana ON principal_lote.manzana_id = principal_manzana.id
                        WHERE manzana_id IN (
                        SELECT id FROM principal_manzana WHERE fraccion_id = (
                        SELECT id FROM principal_fraccion WHERE nombre LIKE UPPER ((%s))))
                        ORDER BY nro_manzana, nro_lote''')
            cursor = connection.cursor()
            cursor.execute(query, [fraccion[0].nombre])
            results = cursor.fetchall()
            if len(results) > 0:
                # Obtenemos los lotes con ese id a partir del result
                for row in results:
                    lote = Lote.objects.get(pk=row[0])
                    try:
                        venta = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
                        venta = venta[0]
                        cliente = venta.cliente
                        lote.cliente = cliente
                        lote.venta = venta
                        datos_cuota = get_cuotas_detail_by_lote(str(lote.id))
                        lote.cant_cuotas_pagadas = str(datos_cuota['cant_cuotas_pagadas']) + "/" + str(
                            datos_cuota['cantidad_total_cuotas'])
                        lote.boleto_nro = obtener_ultima_fecha_pago_lote(lote.id)
                        if venta_es_contado(venta.plan_de_pago_id):
                            lote.boleto_nro = venta.fecha_de_venta

                    except Exception as e:
                        logging.error('Failed.', exc_info=e)
                        lote.cliente = 'Lote de estado "vendido" sin venta asociada'
                        print "El lote vendido no esta asociado a una venta."
                    lista_lotes.append(lote)

    if tipo_busqueda == 'estado':
        if busqueda != '':
            fraccion = None
            if fraccion_segun_estado != '':
                fraccion = Fraccion.objects.filter(nombre=fraccion_segun_estado)

            # Esta manera es haciendo el query estatico, en duro, luego por cada row
            # ir creando un objeto Factura y luego ir agregando
            # a una lista lotes
            lista_lotes = []
            # results = ''

            # QUERY para traer los lotes buscados si le pasamos el id y usamos la columna estado
            # query = ('''SELECT id, nro_lote, manzana_id, precio_contado, precio_credito, superficie,
            # cuenta_corriente_catastral, boleto_nro,
            #         estado, precio_costo, importacion_paralot, codigo_paralot
            #         FROM principal_lote where estado =(%s)''')
            # cursor = connection.cursor()
            # cursor.execute(query, busqueda)

            # QUERY para traer los lotes libres que no se encuentran relacionados con la tabla ventas
            if busqueda == '1':
                # query = ('''SELECT * FROM principal_lote where (id not in
                #         (SELECT lote_id FROM principal_venta) or
                #         (id in (SELECT lotesRecuperados.lote_id FROM (SELECT ventasRecuperadas.lote_id FROM
                #         (SELECT * FROM principal_venta WHERE id in (
                # select "venta_id" from "principal_recuperaciondelotes"))
                # as ventasRecuperadas)as lotesRecuperados))) AND
                # (estado not like '2' AND id not in (SELECT lote_id from principal_reserva))''')
                if fraccion is not None:
                    query = ('''SELECT * FROM principal_lote JOIN principal_manzana
ON principal_lote.manzana_id = principal_manzana.id
JOIN principal_fraccion ON principal_manzana.fraccion_id = principal_fraccion.id
WHERE (principal_lote.id NOT IN (
SELECT lote_id FROM principal_venta) OR (principal_lote.id IN (
                                  SELECT lotesRecuperados.lote_id FROM (SELECT ventasRecuperadas.lote_id FROM
                                  (SELECT * FROM principal_venta WHERE principal_lote.id IN (
                                  SELECT "venta_id" FROM "principal_recuperaciondelotes"))
                                  AS ventasRecuperadas)AS lotesRecuperados)))
                                  AND (estado NOT LIKE '2' AND principal_lote.id NOT IN (
                                  SELECT lote_id FROM principal_reserva))
                                  AND principal_fraccion.id = (%s)
                                  ORDER BY principal_fraccion.id, nro_manzana, nro_lote''')
                    cursor = connection.cursor()
                    cursor.execute(query, [fraccion[0].id])
                else:
                    query = '''SELECT * FROM principal_lote
JOIN principal_manzana ON principal_lote.manzana_id = principal_manzana.id
JOIN principal_fraccion ON principal_manzana.fraccion_id = principal_fraccion.id
WHERE (principal_lote.id NOT IN
(SELECT lote_id FROM principal_venta) OR (principal_lote.id IN (
SELECT lotesRecuperados.lote_id FROM (SELECT ventasRecuperadas.lote_id FROM
(SELECT * FROM principal_venta WHERE principal_lote.id IN (
SELECT "venta_id" FROM "principal_recuperaciondelotes"))
AS ventasRecuperadas)AS lotesRecuperados)))
AND (estado NOT LIKE '2' AND principal_lote.id NOT IN (
SELECT lote_id FROM principal_reserva)) ORDER BY principal_fraccion.id, nro_manzana, nro_lote'''
                    cursor = connection.cursor()
                    cursor.execute(query)
                results = cursor.fetchall()
            elif busqueda == '3':
                if fraccion is not None:
                    query = '''SELECT principal_lote.id, nro_lote, manzana_id,
precio_contado, precio_credito, superficie,
cuenta_corriente_catastral, boleto_nro, estado, precio_costo,
principal_lote.importacion_paralot, codigo_paralot
FROM principal_lote JOIN principal_manzana ON principal_lote.manzana_id = principal_manzana.id
JOIN principal_fraccion ON principal_manzana.fraccion_id = principal_fraccion.id
WHERE principal_lote.id IN (SELECT ventasNoRecuperadas.lote_id FROM (
SELECT * FROM principal_venta WHERE principal_lote.id NOT IN (
SELECT "venta_id" FROM "principal_recuperaciondelotes"))
AS ventasNoRecuperadas) AND principal_fraccion.id = (%s)
ORDER BY principal_fraccion.id, nro_manzana, nro_lote'''
                    cursor = connection.cursor()
                    cursor.execute(query, [fraccion[0].id])
                else:
                    query = '''SELECT principal_lote.id, nro_lote, manzana_id, precio_contado,
precio_credito, superficie, cuenta_corriente_catastral, boleto_nro, estado, precio_costo,
principal_lote.importacion_paralot, codigo_paralot
FROM principal_lote JOIN principal_manzana ON principal_lote.manzana_id = principal_manzana.id
JOIN principal_fraccion ON principal_manzana.fraccion_id = principal_fraccion.id
WHERE principal_lote.id IN (
SELECT ventasNoRecuperadas.lote_id FROM (
SELECT * FROM principal_venta WHERE principal_lote.id NOT IN (
SELECT "venta_id" FROM "principal_recuperaciondelotes")) AS ventasNoRecuperadas)
ORDER BY principal_fraccion.id, nro_manzana, nro_lote'''
                    cursor = connection.cursor()
                    cursor.execute(query)
                results = cursor.fetchall()
            else:
                if fraccion is not None:
                    query = '''SELECT principal_lote.id, nro_lote, manzana_id, precio_contado, precio_credito,
 superficie, cuenta_corriente_catastral, boleto_nro, estado,
 precio_costo, principal_lote.importacion_paralot, codigo_paralot
FROM principal_lote JOIN principal_manzana ON principal_lote.manzana_id = principal_manzana.id
JOIN principal_fraccion ON principal_manzana.fraccion_id = principal_fraccion.id
WHERE (estado = (%s) OR principal_lote.id IN (SELECT lote_id FROM principal_reserva))
AND (principal_fraccion.id = (%s)) ORDER BY principal_fraccion.id, nro_manzana, nro_lote'''
                    cursor = connection.cursor()
                    cursor.execute(query, [busqueda, fraccion[0].id])
                else:
                    query = '''SELECT principal_lote.id, nro_lote, manzana_id, precio_contado,
 precio_credito, superficie, cuenta_corriente_catastral, boleto_nro,
estado, precio_costo, principal_lote.importacion_paralot, codigo_paralot
FROM principal_lote JOIN principal_manzana ON principal_lote.manzana_id = principal_manzana.id
JOIN principal_fraccion ON principal_manzana.fraccion_id = principal_fraccion.id
WHERE estado = (%s) OR principal_lote.id IN (SELECT lote_id FROM principal_reserva)
ORDER BY principal_fraccion.id, nro_manzana, nro_lote'''
                    cursor = connection.cursor()
                    cursor.execute(query, busqueda)
                results = cursor.fetchall()

            if len(results) > 0:
                # Obtenemos los lotes con ese numero de estado a partir del result
                for row in results:
                    lote = Lote.objects.get(pk=row[0])
                    try:
                        venta = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
                        venta = venta[0]
                        cliente = venta.cliente
                        lote.cliente = cliente

                    except Exception as e:
                        logging.error('Failed.', exc_info=e)
                        lote.cliente = 'Lote de estado "vendido" sin venta asociada'
                        print "El lote vendido no esta asociado a una venta."

                    try:
                        object_list = Reserva.objects.filter(lote_id=lote.id)
                        if object_list:
                            cliente = object_list.cliente
                            lote.cliente = cliente
                        elif lote_reservado_segun_estado(lote.id):
                            cliente = object_list.cliente
                            lote.cliente = cliente

                    except Exception as e:
                        logging.error('Failed.', exc_info=e)
                        lote.cliente = 'Lote de estado Reservado'
                        print "El lote esta reservado"

                    lista_lotes.append(lote)

    if tipo_busqueda == '':
        lotes_con_ventas_al_contado = []
        lotes_sin_ventas_al_contado = []
        lista_lotes = Lote.objects.filter(estado='4')
        for lote in lista_lotes:
            ventas = Venta.objects.filter(lote_id=lote.id, plan_de_pago__tipo_de_plan='contado')
            if ventas:
                # se cambia a vendido para corregir
                lote.estado = '3'
                lote.save()
                lotes_con_ventas_al_contado.append(lote)
            else:
                print "no tiene venta al contado asociada"
                lotes_sin_ventas_al_contado.append(lote)
        lista_lotes = lotes_sin_ventas_al_contado

    return lista_lotes


def listado_lotes_excel(lista_ordenada):
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('Listado de Lotes', cell_overwrite_ok=True, )
    sheet.paper_size_code = 1

    usuario = "test"
    sheet.header_str = (
        u"&L&8Fecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                          u"&C&8PROPAR S.R.L.\n Listado de Lotes " + " \nPage &P of &N"
    )
    sheet.footer_str = ''

    c = 0
    sheet.write(c, 0, "Fraccion nro", style_normal)
    sheet.write(c, 1, "Manzana nro", style_normal)
    sheet.write(c, 2, "Lote nro", style_normal)
    sheet.write(c, 3, "Nombre Fraccion", style_normal)
    sheet.write(c, 4, "Cliente", style_normal)
    sheet.write(c, 5, "Cedula", style_normal)
    sheet.write(c, 6, "Fecha venta", style_normal)
    sheet.write(c, 7, "Monto cuota", style_normal)
    sheet.write(c, 8, "Cuotas pagadas", style_normal)
    sheet.write(c, 9, "Estado", style_normal)
    sheet.write(c, 10, "Fec Ult Pago", style_normal)
    c += 1
    for lote in lista_ordenada:
        # escribir linea por linea
        try:
            sheet.write(c, 0, lote.manzana.fraccion.id, style_normal)
            sheet.write(c, 1, lote.manzana.nro_manzana, style_normal)
            sheet.write(c, 2, lote.nro_lote, style_normal)
            sheet.write(c, 3, unicode(lote.manzana.fraccion), style_normal)
            sheet.write(c, 4, unicode(lote.cliente), style_normal)
            sheet.write(c, 5, unicode(lote.cliente.cedula), style_normal)
            sheet.write(c, 6, lote.venta.fecha_de_venta, style_normal)
            sheet.write(c, 7, lote.venta.precio_de_cuota, style_normal)
            sheet.write(c, 8, lote.cant_cuotas_pagadas, style_normal)
            sheet.write(c, 9, lote.get_estado_display(), style_normal)
            sheet.write(c, 10, unicode(lote.boleto_nro), style_normal)
            c += 1
        except Exception, error:
            print error
            c += 1

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment filename=' + 'listado_de_lotes_.xls'
    wb.save(response)
    return response


def obtener_ultima_fecha_pago_lote(lote_id):
    fecha_ultimo_pago = None
    # OBTENER LA ULTIMA VENTA Y SU DETALLE
    ultima_venta = get_ultima_venta_no_recuperada(lote_id)

    # SE TRATAN LOS CASOS EN DONDE NO SE ENCUENTRA VENTA PARA ALGUN LOTE.
    if ultima_venta is not None:
        detalle_cuotas = get_cuotas_detail_by_lote(unicode(str(lote_id)))
        hoy = date.today()
        # Maximo atraso = 500 para tener un parametro maximo de atraso en las cuotas.
        cuotas_a_pagar = obtener_cuotas_a_pagar_full(ultima_venta, hoy, detalle_cuotas,
                                                     500)
    else:
        cuotas_a_pagar = []

    if len(cuotas_a_pagar) >= 1:

        # cuotas_atrasadas = len(cuotas_a_pagar)  # CUOTAS ATRASADAS
        # cantidad_cuotas_pagadas = detalle_cuotas['cant_cuotas_pagadas']  # CUOTAS PAGADAS

        # FECHA ULTIMO PAGO
        if len(PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')) > 0:
            fecha_ultimo_pago = \
                PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')[0].fecha_de_pago
        else:
            fecha_ultimo_pago = 'Dato no disponible'

    return fecha_ultimo_pago


def venta_es_contado(plan_de_pago_id):
    query = '''SELECT tipo_de_plan FROM principal_plandepago WHERE id = (%s)'''
    cursor = connection.cursor()
    cursor.execute(query, [plan_de_pago_id])
    results = cursor.fetchall()
    for row in results:
        if row[0] == 'contado':
            return True
        else:
            return False


def obtener_informe_cuotas_por_cobrar(fraccion_ini):
    # lista = []
    filas_fraccion = []
    g_lote = ''
    query = (''' SELECT pc.* FROM principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
            WHERE f.id = ''' + fraccion_ini + '''
            AND (pc.lote_id = l.id AND l.manzana_id=m.id AND m.fraccion_id=f.id)
            ORDER BY f.id, m.nro_manzana, l.nro_lote, pc.fecha_de_pago
            ''')
    object_list = list(PagoDeCuotas.objects.raw(query))
    cuotas = []
    total_cuotas = 0
    # total_mora = 0
    total_pagos = 0
    total_general_cuotas = 0
    total_general_mora = 0
    total_general_pagos = 0
    total_general_pagos_aux = 0
    # total_general_mora_aux = 0
    # ver esto
    # cant_cuotas = 0
    cuota_aux = {}
    resumen_lote = {}
    venta_aux = {}
    for i, cuota_item in enumerate(object_list):
        # Se setean los datos de cada fila
        cuota = {'mismo_lote': True}
        if g_lote == '':
            g_lote = cuota_item.lote.id
            cuota['mismo_lote'] = False
            cuota['total_de_cuotas'] = 0
            cuota['total_de_mora'] = 0
            cuota['total_de_pago'] = 0
        if g_lote != cuota_item.lote.id:
            # seteamos la cant de cuotas que falta por pagar
            cuota_aux['cuota_nro'] = resumen_lote['cantidad_total_cuotas'] - resumen_lote['cant_cuotas_pagadas']
            total_general_cuotas += venta_aux.precio_final_de_venta
            total_general_pagos = total_general_pagos + total_general_pagos_aux
            total_general_mora = total_general_cuotas - total_general_pagos
            filas_fraccion.append(cuota_aux)
            filas_fraccion[0]['mismo_lote'] = False
            cuotas.extend(filas_fraccion)
            filas_fraccion = []
            g_lote = cuota_item.lote.id

            # cuota = {}
            # cuota['mismo_lote'] = False
            # cuota['total_cuotas'] = unicode('{:,}'.format(total_cuotas)).replace(",", ".")
            # cuota['total_mora'] = unicode('{:,}'.format(total_mora)).replace(",", ".")
            # cuota['total_pago'] = unicode('{:,}'.format(total_pagos)).replace(",", ".")
            # cuota['ultimo_pago'] = True
            # cuotas.append(cuota)

            total_cuotas = 0
            # total_mora = 0
            total_pagos = 0

            # cuota = {}
            cuota['ultimo_pago'] = False
            cuota['mismo_lote'] = True
            cuota['fraccion_id'] = unicode(cuota_item.lote.manzana.fraccion.id)
            cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
            cuota['lote'] = unicode(cuota_item.lote)
            cuota['cliente'] = unicode(cuota_item.cliente)
            # cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
            # cuota['cuota_nro'] = get_nro_cuota(cuota_item)
            cuota['plan_de_pago'] = cuota_item.plan_de_pago.nombre_del_plan
            cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
            # cuota['total_de_cuotas'] = total_cuotas + cuota_item.total_de_cuotas
            cuota['total_de_cuotas'] = unicode('{:,}'.format(total_cuotas + cuota_item.total_de_cuotas)).replace(",",
                                                                                                                 ".")
            # cuota['total_de_mora'] = unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
            venta = Venta.objects.get(id=cuota_item.venta.id)
            # seteamos lo que se debe, el total de la venta menos lo que ya se pago hasta la fecha
            cuota['total_de_mora'] = unicode(
                '{:,}'.format(venta.precio_final_de_venta - (total_cuotas + cuota_item.total_de_cuotas))).replace(",",
                                                                                                                  ".")
            # seteamoa el importe total de la venta
            # cuota['total_de_pago'] = unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
            cuota['total_de_pago'] = unicode('{:,}'.format(venta.precio_final_de_venta)).replace(",", ".")
            # Se suman los totales por fraccion
            total_cuotas += cuota_item.total_de_cuotas
            # total_mora += cuota_item.total_de_mora
            total_pagos += cuota_item.total_de_pago

            cuota_aux = cuota
            venta_aux = venta
            total_general_pagos_aux = total_cuotas

            resumen_lote = get_cuotas_detail_by_lote(unicode(cuota_item.lote.id))

        else:
            cuota['ultimo_pago'] = False
            cuota['mismo_lote'] = True
            cuota['fraccion_id'] = unicode(cuota_item.lote.manzana.fraccion.id)
            cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
            cuota['lote'] = unicode(cuota_item.lote)
            cuota['cliente'] = unicode(cuota_item.cliente)
            # cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
            # cuota['cuota_nro'] = get_nro_cuota(cuota_item)
            cuota['plan_de_pago'] = cuota_item.plan_de_pago.nombre_del_plan
            cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
            # cuota['total_de_cuotas'] = total_cuotas + cuota_item.total_de_cuotas
            cuota['total_de_cuotas'] = unicode('{:,}'.format(total_cuotas + cuota_item.total_de_cuotas)).replace(",",
                                                                                                                 ".")
            # cuota['total_de_mora'] = unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
            venta = Venta.objects.get(id=cuota_item.venta.id)
            # seteamos lo que se debe, el total de la venta menos lo que ya se pago hasta la fecha
            cuota['total_de_mora'] = unicode(
                '{:,}'.format(venta.precio_final_de_venta - (total_cuotas + cuota_item.total_de_cuotas))).replace(",",
                                                                                                                  ".")
            # seteamoa el importe total de la venta
            # cuota['total_de_pago'] = unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
            cuota['total_de_pago'] = unicode('{:,}'.format(venta.precio_final_de_venta)).replace(",", ".")
            # Se suman los totales por fraccion
            total_cuotas += cuota_item.total_de_cuotas
            # total_mora += cuota_item.total_de_mora
            total_pagos += cuota_item.total_de_pago

            cuota_aux = cuota
            venta_aux = venta
            total_general_pagos_aux = total_cuotas

            # filas_fraccion.append(cuota)
            resumen_lote = get_cuotas_detail_by_lote(unicode(cuota_item.lote.id))

    cuotas.extend(filas_fraccion)
    # cuota = {}
    # cuota['total_cuotas'] = unicode('{:,}'.format(total_cuotas)).replace(",", ".")
    # cuota['total_mora'] = unicode('{:,}'.format(total_mora)).replace(",", ".")
    # cuota['total_pago'] = unicode('{:,}'.format(total_pagos)).replace(",", ".")
    # cuota['ultimo_pago'] = True
    # cuotas.append(cuota)
    cuota = {
        'total_general_cuotas': unicode('{:,}'.format(total_general_cuotas)).replace(",", "."),
        'total_general_mora': unicode('{:,}'.format(total_general_mora)).replace(",", "."),
        'total_general_pago': unicode('{:,}'.format(total_general_pagos)).replace(",", ".")
    }
    cuotas.append(cuota)
    lista = cuotas

    return lista


def informe_cuotas_por_cobrar_excel(lista_ordenada):
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('Informe de Cuotas por Cobrar', cell_overwrite_ok=True, )
    sheet.paper_size_code = 1
    style = xlwt.easyxf('font: name Calibri, bold True align: horiz center')

    usuario = "test"
    sheet.header_str = (
        u"&L&8Fecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                          u"&C&8PROPAR S.R.L.\n Informe de Cuotas por Cobrar "
        + " \nPage &P of &N"
    )
    sheet.footer_str = ''

    c = 0
    sheet.write(c, 0, "Nro Lote", style)
    sheet.write(c, 1, "Cliente", style)
    sheet.write(c, 2, "Cuotas Rest", style)
    sheet.write(c, 3, "Plan de Pago", style)
    sheet.write(c, 4, "Importe Total", style)
    sheet.write(c, 5, "Imp. Pag.", style)
    sheet.write(c, 6, "Imp. Deuda", style)

    # Ancho de la columna Nro Lote
    col_nro_lote = sheet.col(0)
    col_nro_lote.width = 256 * 12  # 12 characters wide

    # Ancho de la columna Cliente
    col_cliente = sheet.col(1)
    col_cliente.width = 256 * 20  # 20 characters wide

    # Ancho de la columna Cuotas Rest
    col_cuotas_rest = sheet.col(2)
    col_cuotas_rest.width = 256 * 10  # 10 characters wide

    # Ancho de la columna Plan de Pago
    col_plan_de_pago = sheet.col(3)
    col_plan_de_pago.width = 256 * 25  # 25 characters wide

    # Ancho de la columna Importe Total
    col_importe_total = sheet.col(4)
    col_importe_total.width = 256 * 12  # 12 characters wide

    # Ancho de la columna Imp Pag.
    col_importe_pag = sheet.col(5)
    col_importe_pag.width = 256 * 11  # 8 characters wide

    # Ancho de la columna Imp Deuda"
    col_importe_deuda = sheet.col(6)
    col_importe_deuda.width = 256 * 11  # 11 characters wide

    c += 1
    for lote in lista_ordenada:
        # escribir linea por linea
        try:
            sheet.write(c, 0, lote['lote'], style_normal)
            sheet.write(c, 1, lote['cliente'], style_normal)
            sheet.write(c, 2, lote['cuota_nro'], style_normal)
            sheet.write(c, 3, lote['plan_de_pago'], style_normal)
            sheet.write(c, 4, lote['total_de_pago'], style_normal)
            sheet.write(c, 5, lote['total_de_cuotas'], style_normal)
            sheet.write(c, 6, lote['total_de_mora'], style_normal)
            c += 1
        except Exception, error:
            print error
            c += 1

        if lote == lista_ordenada[-1]:
            sheet.write(c, 4, lote['total_general_cuotas'], style)
            sheet.write(c, 5, lote['total_general_pago'], style)
            sheet.write(c, 6, lote['total_general_mora'], style)
            c += 1

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment filename=' + 'informe_de_cuotas_por_cobrar_.xls'
    wb.save(response)
    return response


def get_mes_pagado_by_id_lote_cant_cuotas(lote_id, cuotas_pag):
    cuotas_detalles = []
    try:
        cuotas_detalles = get_cuota_information_by_lote(lote_id, cuotas_pag)
        return cuotas_detalles
    except Exception, error:
        print error
        return cuotas_detalles

