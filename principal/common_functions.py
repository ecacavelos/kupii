from django.db.models import Count, Min, Sum, Avg
from principal.models import Lote, Cliente, Vendedor, PlanDePago, Fraccion, Manzana, Venta, Propietario, \
    PlanDePagoVendedor, PagoDeCuotas, RecuperacionDeLotes
from principal.monthdelta import MonthDelta
from calendar import monthrange
from datetime import datetime, timedelta
from django.core import serializers
import json


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
    lote_id = pago.lote_id
    # fecha_fin=pago.fecha_de_pago
    cant_cuotas = PagoDeCuotas.objects.filter(lote_id=lote_id, pk__lte=pago_id).count()

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
    data = serializers.serialize('python', object_list)
    results = []
    label1=labels[0]
    if len(labels) > 1:
        label2=labels[1]
      
    for d in data:
        d['fields']['id'] = d['pk']
        #Como maximo habra 2 labels
        if len(labels) <= 1:
            d['fields']['label'] = d['fields'][label1]
        else:
            d['fields']['label'] = d['fields'][label1]+" "+d['fields'][label2]
        results.append(d['fields'])
    return results

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
