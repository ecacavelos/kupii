from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.template import RequestContext, loader
from datos.models import Cliente, Lote, Vendedor, PlanDeVendedores, PlanDePagos, Venta
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
        # object_list = Lote.objects.all()
        # Si el POST es relativo a lotes.
        if data.get('fraccion', '') and data.get('manzana', '') and data.get('lote', ''):                        
            fraccion_int = int(data.get('fraccion', ''))
            manzana_int = int(data.get('manzana', ''))
            lote_int = int(data.get('lote', ''))            
            
            object_list = Lote.objects.filter(fraccion=fraccion_int, manzana=manzana_int, nro_lote=lote_int)
            r = list(object_list[:1])
            if r:                
                r = r[0]
                # Creamos una cadena JSON para enviar la respuesta al request AJAX POST.
                response_data = {}
                response_data['superficie'] = str(r.superficie)
                response_data['lote_id'] = r.id
                response_data['lote_tag'] = str(r)                                
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:        
                return HttpResponseServerError("No se encontraron lotes.")
        # Si el POST es relativo a clientes.
        if data.get('cliente', ''):
            try:
                object_list = Cliente.objects.get(pk=data.get('cliente', ''))
                # Creamos la respuesta al request.
                response = HttpResponse()
                response.write(object_list.nombres)
                response.write(" ")
                response.write(object_list.apellidos)
                return response
            except:
                return HttpResponseServerError("No se encontraron clientes.")
        # Si el POST es relativo a vendedores.
        if data.get('vendedor', ''):
            try:
                object_list = Vendedor.objects.get(pk=data.get('vendedor', ''))
                # Creamos la respuesta al request.
                response = HttpResponse()
                response.write(object_list.nombres)
                response.write(" ")
                response.write(object_list.apellidos)
                return response
            except:
                return HttpResponseServerError("No se encontraron vendedores.")
        if data.get('plan_vendedor', ''):
            try:
                object_list = PlanDeVendedores.objects.get(pk=data.get('plan_vendedor', ''))
                # Creamos la respuesta al request.
                response = HttpResponse()
                response.write(object_list.nombre_del_plan)
                return response
            except:
                return HttpResponseServerError("No se encontraron planes de vendedores.")
        if data.get('plan_pago', ''):
            try:
                datos_plan = PlanDePagos.objects.get(pk=data.get('plan_pago', ''))
                lote_id = data.get('lote', '')
                datos_lote = Lote.objects.get(pk=lote_id)
                # Creamos la respuesta al request.
                response_data = {}
                response_data['nombre_del_plan'] = str(datos_plan.nombre_del_plan)
                response_data['credito'] = datos_plan.tipo_de_plan
                response_data['cantidad_cuotas'] = datos_plan.cantidad_de_cuotas
                if datos_plan.tipo_de_plan == True:
                    response_data['precio_del_lote'] = datos_lote.precio_credito
                else:
                    response_data['precio_del_lote'] = datos_lote.precio_contado
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            except:
                return HttpResponseServerError("No se encontraron planes de pago.")
        if data.get('calcular_cuotas', '') == "true":
            try:
                # lote_id = data.get('lote_establecido', '')
                # datos_lote = Lote.objects.get(pk=lote_id)
                
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
        if data.get('ingresar_venta' , '') == "true":
            
            lote_id = data.get('venta_lote', '')
            lote_a_vender = Lote.objects.get(pk=lote_id)            
            
            cliente_id = data.get('venta_cliente', '')
            vendedor_id = data.get('venta_vendedor', '')
            plan_vendedor_id = data.get('venta_plan_vendedor', '')
            plan_pago_id = data.get('venta_plan_pago', '')
            
            try:
                fecha_venta_parsed = datetime.strptime(data.get('venta_fecha', ''), "%d/%m/%Y")
                fecha_vencim_parsed = datetime.strptime(data.get('venta_fecha_primer_vencimiento', ''), "%d/%m/%Y")
            except:
                fecha_venta_parsed = datetime.strptime(data.get('venta_fecha', ''), "%Y-%m-%d")
                fecha_vencim_parsed = datetime.strptime(data.get('venta_fecha_primer_vencimiento', ''), "%Y-%m-%d")                    
            
            nueva_venta = Venta()
            nueva_venta.lote = lote_a_vender
            nueva_venta.fecha_de_venta = fecha_venta_parsed
            nueva_venta.cliente = Cliente.objects.get(pk=cliente_id)
            nueva_venta.vendedor = Vendedor.objects.get(pk=vendedor_id)
            nueva_venta.plan_de_vendedor = PlanDeVendedores.objects.get(pk=plan_vendedor_id)
            nueva_venta.plan_de_pago = PlanDePagos.objects.get(pk=plan_pago_id)
            nueva_venta.entrega_inicial = data.get('venta_entrega_inicial', '')
            nueva_venta.precio_de_cuota = data.get('venta_precio_cuota', '')
            nueva_venta.cuota_de_refuerzo = data.get('venta_cuota_refuerzo', '')
            nueva_venta.precio_final_de_venta = data.get('venta_precio_final_venta', '')
            nueva_venta.fecha_primer_vencimiento = fecha_vencim_parsed
            nueva_venta.pagos_realizados = 0
            nueva_venta.save()
            
            lote_a_vender.estado = "3"
            lote_a_vender.save()
                        
            return HttpResponse("Success.")
            
        # Si no se recibio una solicitud POST correcta.
        return HttpResponseServerError("No se encontraron datos.")
    else:
        object_list = Lote.objects.none()
        
    c = RequestContext(request, {
        'object_list': object_list,
    })
    # c.update(csrf(request))
    return HttpResponse(t.render(c))
