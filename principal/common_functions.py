from django.db.models import Count, Min, Sum, Avg
from principal.models import Lote, Cliente, Vendedor, PlanDePago, Fraccion, Manzana, Venta, Propietario, PlanDePagoVendedor,PagoDeCuotas
from monthdelta import MonthDelta

def get_cuotas_detail_by_lote(lote_id=None):

    print("buscando pagos del lote --> " + lote_id);    
    # El query es: select sum(nro_cuotas_a_pagar) from principal_pagodecuotas where lote_id = 16108;
    cant_cuotas_pagadas=PagoDeCuotas.objects.filter(lote=lote_id).aggregate(Sum('nro_cuotas_a_pagar'))
    venta = Venta.objects.get(lote_id=lote_id)
    plan_de_pago = PlanDePago.objects.get(id=venta.plan_de_pago.id)
#     calcular la fecha de vencimiento.
    proximo_vencimiento = (venta.fecha_de_venta + MonthDelta(cant_cuotas_pagadas['nro_cuotas_a_pagar__sum'])).strftime('%d/%m/%Y')
    datos = dict([('cant_cuotas_pagadas', cant_cuotas_pagadas['nro_cuotas_a_pagar__sum']), ('cantidad_total_cuotas', plan_de_pago.cantidad_de_cuotas), ('proximo_vencimiento', proximo_vencimiento)])
    return datos    

def get_nro_cuota(pago):
    PagoDeCuotas(pago)
    lote_id=pago.lote_id
    fecha_fin=pago.fecha_de_pago
    pago_id=pago.id
    cuotas_pagadas = PagoDeCuotas.objects.filter(lote=lote_id).order_by('id','fecha_de_pago')
    nro_cuota=0
    current_pago=pago_id
    for cuota in cuotas_pagadas:
        if(cuota.fecha_de_pago<=fecha_fin):
            nro_cuota+=1
        else:    
            break
    #datos=dict([('nro_cuota',nro_cuota)])
    datos=nro_cuota
    return datos