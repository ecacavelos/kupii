from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Cliente, Lote, Vendedor, PlanDePago, Venta, Reserva, PagoDeCuotas, TransferenciaDeLotes
from django.utils import simplejson as json
from datetime import datetime

# Funcion principal del modulo de lotes.
def movimientos(request):
    t = loader.get_template('movimientos/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

def ventas_de_lotes(request):
    t = loader.get_template('movimientos/ventas_lotes.html')

    if request.method == 'POST':
        data = request.POST

        lote_id = data.get('venta_lote_id', '')
        lote_a_vender = Lote.objects.get(pk=lote_id)

        cliente_id = data.get('venta_cliente_id', '')
        vendedor_id = data.get('venta_vendedor_id', '')
        plan_pago_id = data.get('venta_plan_pago_id', '')

        date_parse_error = False

        try:
            fecha_venta_parsed = datetime.strptime(data.get('venta_fecha_de_venta', ''), "%d/%m/%Y")
            fecha_vencim_parsed = datetime.strptime(data.get('venta_fecha_primer_vencimiento', ''), "%d/%m/%Y")
        except:
            date_parse_error = True

        if date_parse_error == True:
            try:
                fecha_venta_parsed = datetime.strptime(data.get('venta_fecha_de_venta', ''), "%Y-%m-%d")
                fecha_vencim_parsed = datetime.strptime(data.get('venta_fecha_primer_vencimiento', ''), "%Y-%m-%d")
            except:
                date_parse_error = True

        nueva_venta = Venta()
        nueva_venta.lote = lote_a_vender
        nueva_venta.fecha_de_venta = fecha_venta_parsed
        nueva_venta.cliente = Cliente.objects.get(pk=cliente_id)
        nueva_venta.vendedor = Vendedor.objects.get(pk=vendedor_id)
        nueva_venta.plan_de_pago = PlanDePago.objects.get(pk=plan_pago_id)
        nueva_venta.entrega_inicial = long(data.get('venta_entrega_inicial', ''))
        nueva_venta.precio_de_cuota = long(data.get('venta_precio_de_cuota', ''))
        nueva_venta.precio_final_de_venta = long(data.get('venta_precio_final_de_venta', ''))
        nueva_venta.fecha_primer_vencimiento = fecha_vencim_parsed
        nueva_venta.pagos_realizados = 0

        sumatoria_cuotas = nueva_venta.entrega_inicial + (nueva_venta.plan_de_pago.cantidad_de_cuotas * nueva_venta.precio_de_cuota)

        if  sumatoria_cuotas >= nueva_venta.precio_final_de_venta:
            nueva_venta.save()
            lote_a_vender.estado = "3"
            lote_a_vender.save()
        else:
            return HttpResponseServerError("La sumatoria de las cuotas es menor al precio final de venta.")

        return HttpResponse(sumatoria_cuotas)

    else:
        object_list = Lote.objects.none()
    c = RequestContext(request, {
        'object_list': object_list,
    })
    # c.update(csrf(request))
    return HttpResponse(t.render(c))

def ventas_de_lotes_calcular_cuotas(request):
    if request.method == 'GET':
        data = request.GET

    try:
        datos_plan = PlanDePago.objects.get(pk=data.get('plan_pago_establecido', ''))
        entrega_inicial = data.get('entrega_inicial', '')
        monto_cuota = data.get('monto_cuota', '')

        precio_venta_actual = int(data.get('precio_de_venta', ''))

        response_data = {}

        if datos_plan.tipo_de_plan == "credito":
            response_data['monto_total'] = int(entrega_inicial) + (datos_plan.cantidad_de_cuotas * int(monto_cuota))
        else:
            response_data['monto_total'] = int(precio_venta_actual)

        if response_data['monto_total'] >= precio_venta_actual:
            response_data['monto_valido'] = True
        else:
            response_data['monto_valido'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    except:
        return HttpResponseServerError("No se pudo calcular el monto de pago.")

def reservas_de_lotes(request):
    t = loader.get_template('movimientos/reservas_lotes.html')

    if request.method == 'POST':
        data = request.POST

        lote_id = data.get('reserva_lote_id', '')
        lote_a_reservar = Lote.objects.get(pk=lote_id)
        cliente_id = data.get('reserva_cliente_id', '')
        date_parse_error = False
        try:
            fecha_reserva_parsed = datetime.strptime(data.get('reserva_fecha_de_reserva', ''), "%d/%m/%Y")
        except:
            date_parse_error = True

        if date_parse_error == True:
            try:
                fecha_reserva_parsed = datetime.strptime(data.get('reserva_fecha_de_reserva', ''), "%Y-%m-%d")
            except:
                date_parse_error = True
        
        nueva_reserva = Reserva()
        nueva_reserva.lote = lote_a_reservar
        nueva_reserva.fecha_de_reserva = fecha_reserva_parsed
        nueva_reserva.cliente = Cliente.objects.get(pk=cliente_id)

        nueva_reserva.save()
        lote_a_reservar.estado = "2"
        lote_a_reservar.save()

    c = RequestContext(request, {
    })
    return HttpResponse(t.render(c))

def pago_de_cuotas(request):
    t = loader.get_template('movimientos/pago_cuotas.html')
    
    if request.method == 'POST':
        data = request.POST

        lote_id = data.get('pago_lote_id', '')
        venta = Venta.objects.get(lote_id=lote_id)

        cliente_id = data.get('pago_cliente_id', '')
        vendedor_id = data.get('pago_vendedor_id', '')
        plan_pago_id = data.get('pago_plan_de_pago_id', '')
        nro_cuotas_a_pagar = data.get('pago_nro_cuotas_a_pagar', '')
        total_de_cuotas = data.get('pago_total_de_cuotas', '')
        total_de_mora = data.get('pago_total_de_mora', '')
        total_de_pago = data.get('pago_total_de_pago', '')
        
        date_parse_error = False

        try:
            fecha_pago_parsed = datetime.strptime(data.get('pago_fecha_de_pago', ''), "%d/%m/%Y")
        except:
            date_parse_error = True

        if date_parse_error == True:
            try:
                fecha_pago_parsed = datetime.strptime(data.get('pago_fecha_de_pago', ''), "%Y-%m-%d")
            except:
                date_parse_error = True

        nuevo_pago = PagoDeCuotas()
        nuevo_pago.lote = Lote.objects.get(pk=lote_id)
        nuevo_pago.fecha_de_pago = fecha_pago_parsed
        nuevo_pago.nro_cuotas_a_pagar = nro_cuotas_a_pagar
        nuevo_pago.cliente = Cliente.objects.get(pk=cliente_id)
        nuevo_pago.plan_de_pago = PlanDePago.objects.get(pk=plan_pago_id)
        nuevo_pago.vendedor = Vendedor.objects.get(pk=vendedor_id)
        nuevo_pago.total_de_cuotas = total_de_cuotas
        nuevo_pago.total_de_mora = total_de_mora
        nuevo_pago.total_de_pago = total_de_pago
        
        nuevo_pago.save()
        venta.pagos_realizados = int(nro_cuotas_a_pagar) + int(venta.pagos_realizados)
        venta.save()

    c = RequestContext(request, {

    })
    return HttpResponse(t.render(c))

def transferencias_de_lotes(request):
    t = loader.get_template('movimientos/transferencias_lotes.html')
    
    if request.method == 'POST':
        data = request.POST

        lote_id = data.get('transferencia_lote_id', '')
        venta = Venta.objects.get(lote_id=lote_id)


        cliente_original_id = data.get('transferencia_cliente_original_id', '')
        cliente_id = data.get('transferencia_cliente_id', '')
        vendedor_id = data.get('transferencia_vendedor_id', '')
        plan_pago_id = data.get('transferencia_plan_de_pago_id', '')
        
        date_parse_error = False

        try:
            fecha_transferencia_parsed = datetime.strptime(data.get('transferencia_fecha_de_transferencia', ''), "%d/%m/%Y")
        except:
            date_parse_error = True

        if date_parse_error == True:
            try:
                fecha_transferencia_parsed = datetime.strptime(data.get('transferencia_fecha_de_transferencia', ''), "%Y-%m-%d")
            except:
                date_parse_error = True

        nueva_transferencia = TransferenciaDeLotes()
        nueva_transferencia.lote = Lote.objects.get(pk=lote_id)
        nueva_transferencia.fecha_de_transferencia = fecha_transferencia_parsed
        nueva_transferencia.cliente_original = Cliente.objects.get(pk=cliente_original_id)
        nueva_transferencia.cliente = Cliente.objects.get(pk=cliente_id)
        nueva_transferencia.plan_de_pago = PlanDePago.objects.get(pk=plan_pago_id)
        nueva_transferencia.vendedor = Vendedor.objects.get(pk=vendedor_id)
        
        nueva_transferencia.save()
        venta.cliente = Cliente.objects.get(pk=cliente_id)
        venta.save()
        
    c = RequestContext(request, {

    })
    return HttpResponse(t.render(c))