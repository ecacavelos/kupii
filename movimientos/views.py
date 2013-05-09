from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Cliente, Lote, Vendedor, PlanDeVendedores, PlanDePagos, Venta
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

        lote_id = data.get('venta_lote', '')
        lote_a_vender = Lote.objects.get(pk=lote_id)

        cliente_id = data.get('venta_cliente', '')
        vendedor_id = data.get('venta_vendedor', '')
        plan_vendedor_id = data.get('venta_plan_vendedor', '')
        plan_pago_id = data.get('venta_plan_pago', '')

        date_parse_error = False

        try:
            fecha_venta_parsed = datetime.strptime(data.get('venta_fecha', ''), "%d/%m/%Y")
            fecha_vencim_parsed = datetime.strptime(data.get('venta_fecha_primer_vencimiento', ''), "%d/%m/%Y")
        except:
            date_parse_error = True

        if date_parse_error == True:
            try:
                fecha_venta_parsed = datetime.strptime(data.get('venta_fecha', ''), "%Y-%m-%d")
                fecha_vencim_parsed = datetime.strptime(data.get('venta_fecha_primer_vencimiento', ''), "%Y-%m-%d")
            except:
                date_parse_error = True

        nueva_venta = Venta()
        nueva_venta.lote = lote_a_vender
        nueva_venta.fecha_de_venta = fecha_venta_parsed
        nueva_venta.cliente = Cliente.objects.get(pk=cliente_id)
        nueva_venta.vendedor = Vendedor.objects.get(pk=vendedor_id)
        nueva_venta.plan_de_vendedor = PlanDeVendedores.objects.get(pk=plan_vendedor_id)
        nueva_venta.plan_de_pago = PlanDePagos.objects.get(pk=plan_pago_id)
        nueva_venta.entrega_inicial = long(data.get('venta_entrega_inicial', ''))
        nueva_venta.precio_de_cuota = long(data.get('venta_precio_cuota', ''))
        nueva_venta.cuota_de_refuerzo = long(data.get('venta_cuota_refuerzo', ''))
        nueva_venta.precio_final_de_venta = long(data.get('venta_precio_final_venta', ''))
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
        datos_plan = PlanDePagos.objects.get(pk=data.get('plan_pago_establecido', ''))
        entrega_inicial = data.get('entrega_inicial', '')
        monto_cuota = data.get('monto_cuota', '')
        cuota_refuerzo = data.get('cuota_refuerzo', '')

        precio_venta_actual = int(data.get('precio_de_venta', ''))

        response_data = {}

        if datos_plan.tipo_de_plan == True:
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

def reserva_de_lotes(request):
    t = loader.get_template('movimientos/reservas_lotes.html')
    object_list = Lote.objects.all().order_by('fraccion', 'manzana', 'nro_lote')
    c = RequestContext(request, {
        'object_list': object_list,
    })
    return HttpResponse(t.render(c))
