from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Cliente,Propietario, Lote, Vendedor, PlanDePago, Venta, Reserva, PagoDeCuotas, TransferenciaDeLotes, CambioDeLotes, RecuperacionDeLotes
from django.utils import simplejson as json
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

 
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
        estado_lote=data.get('estado_lote','')
        
        if estado_lote == "2":
            objeto_reserva=Reserva.objects.filter(cliente_id=cliente_id,lote_id=lote_id)
            a=len(objeto_reserva)
            if a==0:
                return HttpResponseServerError("El lote no fue reservado por este cliente")
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
        
        if nueva_venta.plan_de_pago.tipo_de_plan != 'contado':
            cant_cuotas = nueva_venta.plan_de_pago.cantidad_de_cuotas
            sumatoria_cuotas = nueva_venta.entrega_inicial + (cant_cuotas * nueva_venta.precio_de_cuota)
        else:
            sumatoria_cuotas = nueva_venta.precio_final_de_venta
            
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
        
        nro_cuotas_a_pagar = data.get('pago_nro_cuotas_a_pagar')
        venta_id = data.get('pago_venta_id')
        venta = Venta.objects.get(pk=venta_id)
        venta.pagos_realizados = int(nro_cuotas_a_pagar) + int(venta.pagos_realizados)
        cliente_id = data.get('pago_cliente_id')
        vendedor_id = data.get('pago_vendedor_id')
        plan_pago_id = data.get('pago_plan_de_pago_id')
        
        total_de_cuotas = data.get('pago_total_de_cuotas')
        total_de_mora = data.get('pago_total_de_mora')
        total_de_pago = data.get('pago_total_de_pago')
        
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
        
        cantidad_cuotas = PlanDePago.objects.get(pk=plan_pago_id)        
        cuotas_restantes = int(cantidad_cuotas.cantidad_de_cuotas) - int(nro_cuotas_a_pagar)        
        if cuotas_restantes >= int(nro_cuotas_a_pagar):
        
            nuevo_pago = PagoDeCuotas()
            nuevo_pago.venta = Venta.objects.get(pk=venta_id)
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
            
            venta.save()
            c = RequestContext(request, {

            })
            return HttpResponse(t.render(c))
        
        else:
            return HttpResponseServerError("La cantidad de cuotas a pagar, es mayor a la cantidad de cuotas restantes.")  

    c = RequestContext(request, {

    })
    return HttpResponse(t.render(c))

def transferencias_de_lotes(request):
    t = loader.get_template('movimientos/transferencias_lotes.html')
    
    if request.method == 'POST':
        data = request.POST

        lote_id = data.get('transferencia_lote_id', '')
        venta_para_id = Venta.objects.filter(lote=lote_id).order_by('-id')[:1]
        venta = Venta.objects.get(pk=venta_para_id[0].id)

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

def cambio_de_lotes(request):
    t = loader.get_template('movimientos/cambio_lotes.html')

    if request.method == 'POST':
        data = request.POST

        #lote_id = data.get('cambio_lote_id', '')
        #cambio = CambioDeLotes.objects.get(lote_id=lote_id)


        lote_original_id = data.get('cambio_lote_original_id', '')
        cliente_id = data.get('cambio_cliente_id', '')
        lote_nuevo_id = data.get('cambio_lote2_id', '')
        #venta_id = data.get('cambio_venta_id', '')
        #plan_de_pago_id = data.get('cambio_plan_de_pago_id', '')
        
        date_parse_error = False

        try:
            fecha_cambio_parsed = datetime.strptime(data.get('cambio_fecha_de_cambio', ''), "%d/%m/%Y")
        except:
            date_parse_error = True

        if date_parse_error == True:
            try:
                fecha_cambio_parsed = datetime.strptime(data.get('cambio_fecha_de_cambio', ''), "%Y-%m-%d")
            except:
                date_parse_error = True

        nuevo_cambio = CambioDeLotes()       
        nuevo_cambio.lote_a_cambiar_id = lote_original_id
        nuevo_cambio.fecha_de_cambio = fecha_cambio_parsed
        nuevo_cambio.cliente_id = cliente_id 
        nuevo_cambio.lote_nuevo_id = lote_nuevo_id
        
        
        lote_nuevo = Lote.objects.get(pk=lote_nuevo_id)
        lote_nuevo.estado="3"
        lote_nuevo.save()
        
        lote_viejo = Lote.objects.get(pk=lote_original_id)
        lote_viejo.estado="1"
        lote_viejo.save()
        
        nuevo_cambio.save()
        
    
    c = RequestContext(request, {

    })
    return HttpResponse(t.render(c))

def recuperacion_de_lotes(request):
    t = loader.get_template('movimientos/recuperacion_lotes.html')

    if request.method == 'POST':
        data = request.POST

        lote_id = data.get('recuperacion_lote_id', '')
        lote_a_recuperar = Lote.objects.get(pk=lote_id)

        venta_id = data.get('recuperacion_venta_id')
        cliente_id = data.get('recuperacion_cliente_id', '')
        vendedor_id = data.get('recuperacion_vendedor_id', '')
        plan_pago_id = data.get('recuperacion_plan_de_pago_id', '')

        date_parse_error = False

        try:
            fecha_recuperacion_parsed = datetime.strptime(data.get('recuperacion_fecha_de_recuperacion', ''), "%d/%m/%Y")
        except:
            date_parse_error = True

        if date_parse_error == True:
            try:
                fecha_recuperacion_parsed = datetime.strptime(data.get('recuperacion_fecha_de_recuperacion', ''), "%Y-%m-%d")
            except:
                date_parse_error = True

        nueva_recuperacion = RecuperacionDeLotes()
        nueva_recuperacion.lote = Lote.objects.get(pk=lote_id)
        nueva_recuperacion.venta = Venta.objects.get(pk=venta_id)
        nueva_recuperacion.fecha_de_recuperacion = fecha_recuperacion_parsed
        nueva_recuperacion.cliente = Cliente.objects.get(pk=cliente_id)
        nueva_recuperacion.plan_de_pago = PlanDePago.objects.get(pk=plan_pago_id)
        nueva_recuperacion.vendedor = Vendedor.objects.get(pk=vendedor_id)

        nueva_recuperacion.save()
        lote_a_recuperar.estado = "1"
        lote_a_recuperar.save()
        
    c = RequestContext(request, {
    })
    return HttpResponse(t.render(c))


# Funcion para consultar el listado de todas las ventas.
def listar_ventas(request):
    t = loader.get_template('movimientos/listado_ventas.html')
    try:
        object_list = Venta.objects.all().order_by('id')
        a = len(object_list)
        if a>0:
            for i in object_list:
                i.fecha_de_venta=i.fecha_de_venta.strftime("%d/%m/%Y")
                i.precio_final_de_venta=str('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")
                
            paginator=Paginator(object_list,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
    except:
        return HttpResponseServerError("No se pudo obtener el Listado de Ventas de Lotes.")


def listar_busqueda_personas(request):
    
    try:
        
        tabla = request.POST['tabla']
        busqueda = request.POST['busqueda']
        tipo_busqueda=request.POST['tipo_busqueda']
        
        if tabla=='cliente':
            t = loader.get_template('clientes/listado.html')

            if tipo_busqueda=="nombre":
                object_list = Cliente.objects.filter(nombres__icontains=busqueda)
            if tipo_busqueda=="cedula":
                object_list = Cliente.objects.filter(cedula__icontains=busqueda)
                
            paginator=Paginator(object_list,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
    
        if tabla=='propietario':
            t = loader.get_template('propietarios/listado.html')

            if tipo_busqueda=="nombre":
                object_list = Propietario.objects.filter(nombres__icontains=busqueda)
            if tipo_busqueda=="cedula":
                object_list = Propietario.objects.filter(cedula__icontains=busqueda)
                
            paginator=Paginator(object_list,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
        
        if tabla=='vendedor':
            t = loader.get_template('vendedores/listado.html')
            if tipo_busqueda=="nombre":
                object_list = Vendedor.objects.filter(nombres__icontains=busqueda)
            if tipo_busqueda=="cedula":
                object_list = Vendedor.objects.filter(cedula__icontains=busqueda)
                   
            paginator=Paginator(object_list,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
    except:
        return HttpResponseServerError("Error en la ejecucion.")     
            
            
#Funcion para consultar el listado de todos los pagos.
def listar_pagos(request):
    t = loader.get_template('movimientos/listado_pagos.html')
    try:
        object_list = PagoDeCuotas.objects.all().order_by('id')
        a = len(object_list)
        if a>0:
            for i in object_list:
                i.fecha_de_pago=i.fecha_de_pago.strftime("%d/%m/%Y")
                i.total_de_cuotas=str('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                i.total_de_mora=str('{:,}'.format(i.total_de_mora)).replace(",", ".")
                i.total_de_pago=str('{:,}'.format(i.total_de_pago)).replace(",", ".")
            paginator=Paginator(object_list,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
    except:   
            return HttpResponseServerError("No se pudo obtener el Listado de Pagos de Lotes.")
        
def listar_cambios(request):
    t = loader.get_template('movimientos/listado_cambios.html')
    try:
        object_list = CambioDeLotes.objects.all().order_by('id')
        for i in object_list:
            if(i.fecha_de_cambio!=None):
                i.fecha_de_cambio=i.fecha_de_cambio.strftime("%d/%m/%Y")
            paginator=Paginator(object_list,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
    except:   
            return HttpResponseServerError("No se pudo obtener el Listado de Cambios de Lotes.")
            
    

def listar_rec(request):
    t = loader.get_template('movimientos/listado_recuperacion.html')
    try:
        object_list = RecuperacionDeLotes.objects.all().order_by('id')
        for i in object_list:
            if(i.fecha_de_recuperacion!=None):
                i.fecha_de_recuperacion=i.fecha_de_recuperacion.strftime("%d/%m/%Y")        
        paginator=Paginator(object_list,15)
        page=request.GET.get('page')
        try:
            lista=paginator.page(page)
        except PageNotAnInteger:
            lista=paginator.page(1)
        except EmptyPage:
            lista=paginator.page(paginator.num_pages)
        c = RequestContext(request, {
            'object_list': lista,
        })
        return HttpResponse(t.render(c))
    except:   
            return HttpResponseServerError("No se pudo obtener el Listado de Recuperacion de Lotes.")
    
        
def listar_res(request):
    t = loader.get_template('movimientos/listado_reservas.html')
    
    try:
        object_list = Reserva.objects.all().order_by('id')
        a = len(object_list)
        if a>0:
            for i in object_list:
                i.fecha_de_reserva=i.fecha_de_reserva.strftime("%d/%m/%Y")
            paginator=Paginator(object_list,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
    except:   
            return HttpResponseServerError("No se pudo obtener el Listado de Reservas de Lotes.")
    
    
def listar_transf(request):
    t = loader.get_template('movimientos/listado_transferencias.html')
    
    try:
        object_list = TransferenciaDeLotes.objects.all().order_by('id')
        a = len(object_list)
        if a>0:
            for i in object_list:
                i.fecha_de_transferencia=i.fecha_de_transferencia.strftime("%d/%m/%Y")
            paginator=Paginator(object_list,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
    except:   
            return HttpResponseServerError("No se pudo obtener el Listado de Transferencias de Lotes.")


