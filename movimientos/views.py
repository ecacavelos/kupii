from django.http import HttpResponse, HttpResponseServerError,HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Fraccion, Manzana, Cliente,Propietario, Lote, Vendedor, PlanDePago, PlanDePagoVendedor, Venta, Reserva, PagoDeCuotas, TransferenciaDeLotes, CambioDeLotes, RecuperacionDeLotes
import json
import datetime
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, resolve
from principal.common_functions import *
from principal.monthdelta import MonthDelta 
from django.core import serializers
from principal.common_functions import verificar_permisos
from principal import permisos
 
# Funcion principal del modulo de lotes.
def movimientos(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_OPCIONES):
            t = loader.get_template('movimientos/index.html')
            c = RequestContext(request, {})        
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo  
                })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
        

def ventas_de_lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_VENTA):
            t = loader.get_template('movimientos/ventas_lotes.html')
        
            if request.method == 'POST':
                data = request.POST
                lote_id = data.get('venta_lote_id', '')
                lote_a_vender = Lote.objects.get(pk=lote_id)
        
                cliente_id = data.get('venta_cliente_id', '')
                vendedor_id = data.get('venta_vendedor_id', '')
                plan_pago_id = data.get('venta_plan_pago_id', '')
                plan_pago_vendedor_id=data.get('venta_plan_pago_vendedor_id','')
                cedula_cli =  data.get('venta_cedula_cli', '')
                estado_lote=data.get('estado_lote','')
                monto_c_refuerzo = data.get('monto_refuerzo')
                if monto_c_refuerzo == '':
                    monto_c_refuerzo = 0
                if estado_lote == "2":
                    objeto_reserva=Reserva.objects.filter(cliente_id=cliente_id,lote_id=lote_id)
                    a=len(objeto_reserva)
                    if a==0:
                        return HttpResponseServerError("El lote no fue reservado por este cliente")
                date_parse_error = False
        
                try:
                    fecha_venta_parsed = datetime.datetime.strptime(data.get('venta_fecha_de_venta', ''), "%d/%m/%Y")
                    fecha_vencim_parsed = datetime.datetime.strptime(data.get('venta_fecha_primer_vencimiento', ''), "%d/%m/%Y")
                except:
                    date_parse_error = True
        
                if date_parse_error == True:
                    try:
                        fecha_venta_parsed = datetime.datetime.strptime(data.get('venta_fecha_de_venta', ''), "%Y-%m-%d")
                        fecha_vencim_parsed = datetime.datetime.strptime(data.get('venta_fecha_primer_vencimiento', ''), "%Y-%m-%d")
                    except:
                        date_parse_error = True
                try:        
                    nueva_venta = Venta()
                    nueva_venta.lote = lote_a_vender
                    nueva_venta.fecha_de_venta = fecha_venta_parsed
                    if cliente_id != "":
                        nueva_venta.cliente = Cliente.objects.get(pk=cliente_id)
                    else:
                        nueva_venta.cliente = Cliente.objects.get(cedula=cedula_cli)
                    nueva_venta.vendedor = Vendedor.objects.get(pk=vendedor_id)
                    nueva_venta.plan_de_pago = PlanDePago.objects.get(pk=plan_pago_id)
                    nueva_venta.plan_de_pago_vendedor = PlanDePagoVendedor.objects.get(pk=plan_pago_vendedor_id)
                    nueva_venta.entrega_inicial = long(data.get('venta_entrega_inicial', ''))
                    nueva_venta.precio_de_cuota = long(data.get('venta_precio_de_cuota', ''))
                    nueva_venta.precio_final_de_venta = long(data.get('venta_precio_final_de_venta', ''))
                    nueva_venta.fecha_primer_vencimiento = fecha_vencim_parsed
                    nueva_venta.pagos_realizados = 0    
                    nueva_venta.importacion_paralot=False
                    nueva_venta.plan_de_pago_vendedor= PlanDePagoVendedor.objects.get(pk=plan_pago_vendedor_id)
                    nueva_venta.monto_cuota_refuerzo = long(monto_c_refuerzo)
                except Exception, error:
                    print error 
                    pass           
                if nueva_venta.plan_de_pago.tipo_de_plan != 'contado':
                    cant_cuotas = nueva_venta.plan_de_pago.cantidad_de_cuotas
                    sumatoria_cuotas = nueva_venta.entrega_inicial + (cant_cuotas * nueva_venta.precio_de_cuota)
                else:
                    sumatoria_cuotas = nueva_venta.precio_final_de_venta
                    
                if  sumatoria_cuotas >= nueva_venta.precio_final_de_venta:
                    nueva_venta.save()
                    lote_a_vender.estado = "3"
                    lote_a_vender.save()
                    venta_cli = Venta.objects.get(pk=nueva_venta.id)
                else:
                    return HttpResponseServerError("La sumatoria de las cuotas es menor al precio final de venta.")
                c = RequestContext(request, {
                     'sumatoria_cuotas': sumatoria_cuotas,
                     'ventas': venta_cli
                })
                return HttpResponse(t.render(c))
#                 data = json.dumps({
#                     'ventas': venta_cli})
#                 return HttpResponse(data,content_type="application/json")
            else:
                object_list = Lote.objects.none()
            c = RequestContext(request, {
                'object_list': object_list,
            })
            # c.update(csrf(request))
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo  
                })
            return HttpResponse(t.render(c))
    else: 
        return HttpResponseRedirect(reverse('login'))

def ventas_de_lotes_calcular_cuotas(request):
    
    if request.user.is_authenticated():
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
        except Exception, error:
            print error 
            #return HttpResponseServerError("No se pudo calcular el monto de pago.")
    else:
        return HttpResponseRedirect(reverse('login'))

def reservas_de_lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_RESERVA):
            t = loader.get_template('movimientos/reservas_lotes.html')
        
            if request.method == 'POST':
                data = request.POST
        
                lote_id = data.get('reserva_lote_id', '')
                lote_a_reservar = Lote.objects.get(pk=lote_id)
                cliente_id = data.get('reserva_cliente_id', '')
                date_parse_error = False
                try:
                    fecha_reserva_parsed = datetime.datetime.strptime(data.get('reserva_fecha_de_reserva', ''), "%d/%m/%Y")
                except:
                    date_parse_error = True
        
                if date_parse_error == True:
                    try:
                        fecha_reserva_parsed = datetime.datetime.strptime(data.get('reserva_fecha_de_reserva', ''), "%Y-%m-%d")
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
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo  
                })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

def pago_de_cuotas(request):        
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_PAGODECUOTAS):
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
                plan_pago_vendedor_id=data.get('pago_plan_de_pago_vendedor_id')
                total_de_cuotas = data.get('pago_total_de_cuotas')
                total_de_mora = data.get('pago_total_de_mora')
                total_de_pago = data.get('pago_total_de_pago')
                date_parse_error = False
                fecha_pago=data.get('pago_fecha_de_pago', '')
                fecha_pago_parsed = datetime.datetime.strptime(fecha_pago, "%d/%m/%Y").date()
    #             try:
    #                 fecha_pago_parsed = datetime.strptime(data.get('pago_fecha_de_pago', ''), "%d/%m/%Y")
    #             except:
    #                 date_parse_error = True
    #       
    #             if date_parse_error == True:
    #                 try:
    #                     fecha_pago_parsed = datetime.strptime(data.get('pago_fecha_de_pago', ''), "%Y-%m-%d")
    #                 except:
    #                     date_parse_error = True
                #print fecha_pago
                #print fecha_pago_parsed
                cantidad_cuotas = PlanDePago.objects.get(pk=plan_pago_id)
                cuotas_pagadas = Venta.objects.get(pk=venta.id)        
                cuotas_restantes = int(cantidad_cuotas.cantidad_de_cuotas) - int(cuotas_pagadas.pagos_realizados)        
                if cuotas_restantes >= int(nro_cuotas_a_pagar):
                    try:
                        nuevo_pago = PagoDeCuotas()
                        nuevo_pago.venta = Venta.objects.get(pk=venta_id)
                        nuevo_pago.lote = Lote.objects.get(pk=lote_id)
                        nuevo_pago.fecha_de_pago = fecha_pago_parsed
                        nuevo_pago.nro_cuotas_a_pagar = nro_cuotas_a_pagar
                        nuevo_pago.cliente = Cliente.objects.get(pk=cliente_id)
                        nuevo_pago.plan_de_pago = PlanDePago.objects.get(pk=plan_pago_id)
                        nuevo_pago.plan_de_pago_vendedores= PlanDePagoVendedor.objects.get(pk=plan_pago_vendedor_id)
                        nuevo_pago.vendedor = Vendedor.objects.get(pk=vendedor_id)
                        nuevo_pago.total_de_cuotas = total_de_cuotas
                        nuevo_pago.total_de_mora = total_de_mora
                        nuevo_pago.total_de_pago = total_de_pago
                        nuevo_pago.save()
                    except Exception, error:
                        print error
                        pass
                    venta.save()
                    c = RequestContext(request, {
        
                    })
                    return HttpResponse(t.render(c))        
                else:
                    return HttpResponseServerError("La cantidad de cuotas a pagar, es mayor a la cantidad de cuotas restantes.")  
        
            c = RequestContext(request, {
        
            })
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo  
                })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")

def calcular_interes(request):
    if request.user.is_authenticated():
        #calculando el interes
        if request.method == 'POST':
            data = request.POST    
            lote_id = data.get('lote_id', '')
            print 'lote_id->' + lote_id
            fecha_pago = data.get('fecha_pago', '')
            proximo_vencimiento = data.get('proximo_vencimiento', '')
            fecha_pago_parsed = datetime.datetime.strptime(data.get('fecha_pago'), "%d/%m/%Y").date()

            #fecha_pago_parsed = datetime.strptime(fecha_pago, "%d/%m/%Y").date()
            #proximo_vencimiento = data.get('proximo_vencimiento', '')
            #proximo_vencimiento_parsed = datetime.strptime(proximo_vencimiento, "%d/%m/%Y").date()

            proximo_vencimiento_parsed = datetime.datetime.strptime(data.get('proximo_vencimiento'), "%d/%m/%Y").date()

            
            detalles = obtener_detalle_interes_lote(lote_id,fecha_pago_parsed,proximo_vencimiento_parsed)

            return HttpResponse(json.dumps(detalles),content_type="application/json")
    else:
        return HttpResponseRedirect("/login")

def transferencias_de_lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_TRANSFERENCIADELOTES):
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
                    fecha_transferencia_parsed = datetime.datetime.strptime(data.get('transferencia_fecha_de_transferencia', ''), "%d/%m/%Y")
                except:
                    date_parse_error = True
        
                if date_parse_error == True:
                    try:
                        fecha_transferencia_parsed = datetime.datetime.strptime(data.get('transferencia_fecha_de_transferencia', ''), "%Y-%m-%d")
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
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

def cambio_de_lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_CAMBIODELOTES):
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
                    fecha_cambio_parsed = datetime.datetime.strptime(data.get('cambio_fecha_de_cambio', ''), "%d/%m/%Y")
                except:
                    date_parse_error = True
        
                if date_parse_error == True:
                    try:
                        fecha_cambio_parsed = datetime.datetime.strptime(data.get('cambio_fecha_de_cambio', ''), "%Y-%m-%d")
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
        else:
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
        

def recuperacion_de_lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_RECUPERACIONDELOTES):
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
                    fecha_recuperacion_parsed = datetime.datetime.strptime(data.get('recuperacion_fecha_de_recuperacion', ''), "%d/%m/%Y")
                except:
                    date_parse_error = True
        
                if date_parse_error == True:
                    try:
                        fecha_recuperacion_parsed = datetime.datetime.strptime(data.get('recuperacion_fecha_de_recuperacion', ''), "%Y-%m-%d")
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
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))


# Funcion para consultar el listado de todas las ventas.
def listar_ventas(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('movimientos/listado_ventas.html')
            try:
                object_list = Venta.objects.all().order_by('-fecha_de_venta')
                a = len(object_list)
                if a > 0:
                    for i in object_list:
                        #i.fecha_de_venta = i.fecha_de_venta.strftime("%Y-%m-%d")
                        i.precio_final_de_venta = unicode('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")
                paginator = Paginator(object_list, 15)
                page = request.GET.get('page')
                try:
                    lista = paginator.page(page)
                except PageNotAnInteger:
                    lista = paginator.page(1)
                except EmptyPage:
                    lista = paginator.page(paginator.num_pages)
                    
                c = RequestContext(request, {
                    'object_list': lista,
                })
                return HttpResponse(t.render(c))       
            except Exception, error:
                print error
                #return HttpResponseServerError("No se pudo obtener el Listado de Ventas de Lotes.")
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
            
#Funcion para consultar el listado de todos los pagos.
def listar_pagos(request):  
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('movimientos/listado_pagos.html')
            object_list = PagoDeCuotas.objects.all().order_by('-fecha_de_pago')
            if object_list:
                for i in object_list:
                    try:
                        i.fecha_de_pago=i.fecha_de_pago.strftime("%d/%m/%Y")
                        i.total_de_cuotas=unicode('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                        i.total_de_mora=unicode('{:,}'.format(i.total_de_mora)).replace(",", ".")
                        i.total_de_pago=unicode('{:,}'.format(i.total_de_pago)).replace(",", ".")
                    except Exception, error:
                        print i.id
                        pass
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
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))        
    else:
        return HttpResponseRedirect(reverse('login'))
        
#Funcion para obtener el listado de cambios de lotes.        
def listar_cambios(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('movimientos/listado_cambios.html')
            try:
                object_list = CambioDeLotes.objects.all().order_by('id')
                a=len(object_list)
                if a>0:
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
            except Exception, error:
                print error 
                #return HttpResponseServerError("No se pudo obtener el Listado de Cambios de Lotes.")
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
            
    
#Funcion para listar los lotes recuperados.
def listar_rec(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('movimientos/listado_recuperacion.html')
            try:
                object_list = RecuperacionDeLotes.objects.all().order_by('id')
                a=len(object_list)
                if a>0:
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
            except Exception, error:
                print error    
                #return HttpResponseServerError("No se pudo obtener el Listado de Recuperacion de Lotes.")
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
#Funcion para obtener el listado de los lotes reservados.        
def listar_res(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('movimientos/listado_reservas.html')
            try:
                object_list = Reserva.objects.all().order_by('id','fecha_de_reserva')
                if object_list:
                    for i in object_list:
                        try:
                            i.fecha_de_reserva=i.fecha_de_reserva.strftime("%d/%m/%Y")
                        except Exception, error:
                            print error
                            print i.id
                            pass
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
            except Exception, error:
                print error    
                #return HttpResponseServerError("No se pudo obtener el Listado de Reservas de Lotes.")
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
#Funcion para obtener el listado de los lotes transferidos.
def listar_transf(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('movimientos/listado_transferencias.html')
            f = []
            try:
                object_list = TransferenciaDeLotes.objects.all().order_by('id')
                a = len(object_list)
                if a>0:
                    for i in object_list:
                        #lote = Lote.objects.get(pk=i.lote_id)
                        #manzana = Manzana.objects.get(pk=lote.manzana_id)
                        #f.append(Fraccion.objects.get(pk=manzana.fraccion_id))
                        if(i.fecha_de_transferencia!=None):
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
                    'fraccion': f,
                })
                return HttpResponse(t.render(c))
            except Exception, error:
                print error    
                #return HttpResponseServerError("No se pudo obtener el Listado de Transferencias de Lotes.")
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))


def listar_busqueda_personas(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            if request.method == 'GET':
                #try:
                tabla = request.GET['tabla']
                busqueda = request.GET['busqueda']
                tipo_busqueda=request.GET['tipo_busqueda']            
                print 'busqueda->' + busqueda
                if tabla=='cliente':
                    t = loader.get_template('clientes/listado.html') 
                    object_list = Cliente.objects.filter(pk=busqueda)
                                                   
                if tabla=='propietario':
                    t = loader.get_template('propietarios/listado.html')
                    object_list = Propietario.objects.filter(pk=busqueda)
                           
                if tabla=='vendedor':
                    t = loader.get_template('vendedores/listado.html')
                    object_list = Vendedor.objects.filter(pk=busqueda)
                
                ultima_busqueda = "&tabla="+tabla+"&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
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
                   'ultima_busqueda': ultima_busqueda,
                })
                return HttpResponse(t.render(c))
                #except:
                #    return HttpResponseServerError("Error en la ejecucion.")   
    #         else:
    #             try:
    #                 t = loader.get_template('clientes/listado.html')
    #                 tabla = request.GET['tabla']
    #                 busqueda = request.GET['busqueda']
    #                 tipo_busqueda=request.GET['tipo_busqueda']
    #             
    #                 if tabla=='cliente':
    #                     t = loader.get_template('clientes/listado.html')
    #                     if tipo_busqueda=="nombre":
    #                         object_list = Cliente.objects.filter(nombres__icontains=busqueda)
    #                     if tipo_busqueda=="cedula":
    #                         object_list = Cliente.objects.filter(cedula__icontains=busqueda)
    #                                
    #                 if tabla=='propietario':
    #                     t = loader.get_template('propietarios/listado.html')
    #                     if tipo_busqueda=="nombre":
    #                         object_list = Propietario.objects.filter(nombres__icontains=busqueda)
    #                     if tipo_busqueda=="cedula":
    #                         object_list = Propietario.objects.filter(cedula__icontains=busqueda)
    #         
    #                 if tabla=='vendedor':
    #                     t = loader.get_template('vendedores/listado.html')
    #                     if tipo_busqueda=="nombre":
    #                         object_list = Vendedor.objects.filter(nombres__icontains=busqueda)
    #                     if tipo_busqueda=="cedula":
    #                         object_list = Vendedor.objects.filter(cedula__icontains=busqueda)
    #             
    #                 ultima_busqueda = "&tabla="+tabla+"&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda
    #                 paginator=Paginator(object_list,15)
    #                 page=request.GET.get('page')
    #                 try:
    #                     lista=paginator.page(page)
    #                 except PageNotAnInteger:
    #                     lista=paginator.page(1)
    #                 except EmptyPage:
    #                     lista=paginator.page(paginator.num_pages)
    #     
    #                 c = RequestContext(request, {
    #                     'object_list': lista,
    #                     'ultima_busqueda': ultima_busqueda,
    #                 })
    #                 return HttpResponse(t.render(c))
    #             except:
    #                 return HttpResponseServerError("Error en la ejecucion.")
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:   
        return HttpResponseRedirect(reverse('login'))
    
def listar_busqueda_ventas(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            if request.method == 'GET':
                t = loader.get_template('movimientos/listado_ventas.html')
                tipo_busqueda = request.GET['tipo_busqueda']
                busqueda_label = request.GET['busqueda_label']
                fecha_hasta = request.GET['fecha_hasta']
                busqueda = request.GET['busqueda']            
                ultima_busqueda = "&tipo_busqueda="+tipo_busqueda+"&busqueda_label="+busqueda_label+"&busqueda="+busqueda+"&fecha_hasta="+fecha_hasta
                if tipo_busqueda=='lote':
                    try:
                        lote = request.GET['busqueda_label']                                    
                        x=unicode(lote)
                        fraccion_int = int(x[0:3])
                        manzana_int =int(x[4:7])
                        lote_int = int(x[8:])
                    except Exception, error:
                        print error 
                        #return HttpResponseServerError("Datos erroneos, favor cargar el numero de lote con el formato Fraccion/Manzana/Lote.")       
                    try:
                        manzana_id=Manzana.objects.get(fraccion_id=fraccion_int,nro_manzana=manzana_int)
                        lote_id=Lote.objects.get(manzana_id=manzana_id,nro_lote=lote_int)
                        object_list = Venta.objects.filter(lote_id=lote_id.id)                    
                        if object_list:
                            for i in object_list:
                                i.precio_final_de_venta = unicode('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")                     
                    except Exception, error:
                        print error
                        object_list= []
                    
                if tipo_busqueda=='cliente':
                    try:
                        cliente_id = request.GET['busqueda']
                        object_list = Venta.objects.filter(cliente_id=cliente_id)
                        if object_list:
                            for i in object_list:
                                i.precio_final_de_venta = unicode('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")                                                     
                    except Exception, error:
                        print error
                        object_list= []
               
                if tipo_busqueda=='vendedor':
                    try:
                        vendedor_id = request.GET['busqueda']                    
                        object_list = Venta.objects.filter(vendedor_id=vendedor_id)
                        if object_list:
                            for i in object_list:
                                i.precio_final_de_venta = unicode('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")                                   
                    except Exception, error:
                        print error
                        object_list= []    
                             
                if tipo_busqueda=='fecha':
                    try:
                        fecha_venta = request.GET['busqueda_label']
                        fecha_hasta=request.GET['fecha_hasta']
                        fecha_venta_parsed = datetime.strptime(fecha_venta, "%d/%m/%Y").date()
                        fecha_hasta_parsed=datetime.strptime(fecha_hasta,"%d/%m/%Y").date()
                        object_list = Venta.objects.filter(fecha_de_venta__range=(fecha_venta_parsed,fecha_hasta_parsed)).order_by('-fecha_de_venta') 
                        for i in object_list:
                            i.precio_final_de_venta = unicode('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")                                
                    except Exception, error:
                        print error
                        object_list= []              
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
                    'ultima_busqueda': ultima_busqueda,
                    'tipo_busqueda' : tipo_busqueda,
                    'busqueda_label' : busqueda_label,
                    'fecha_hasta' : fecha_hasta,
                    'busqueda' : busqueda                      
                })                             
                return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))     
    else:
        return HttpResponseRedirect(reverse('login'))

def listar_busqueda_pagos(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            if request.method=='GET':
                t = loader.get_template('movimientos/listado_pagos.html')            
                tipo_busqueda = request.GET['tipo_busqueda']
                busqueda_label = request.GET['busqueda_label']
                fecha_hasta = request.GET['fecha_hasta']
                busqueda = request.GET['busqueda']            
                ultima_busqueda = "&tipo_busqueda="+tipo_busqueda+"&busqueda_label="+busqueda_label+"&busqueda="+busqueda+"&fecha_hasta="+fecha_hasta
                if tipo_busqueda=='lote':
                    try:
                        lote = request.GET['busqueda_label']       
                        x=unicode(lote)
                        fraccion_int = int(x[0:3])
                        manzana_int =int(x[4:7])
                        lote_int = int(x[8:])
                    except Exception, error:
                        print error 
                        #return HttpResponseServerError("Datos erroneos, favor cargar el numero de lote con el formato Fraccion/Manzana/Lote.")       
                    try:
                        manzana_id=Manzana.objects.get(fraccion_id=fraccion_int,nro_manzana=manzana_int)
                        lote_id=Lote.objects.get(manzana_id=manzana_id,nro_lote=lote_int)
                        object_list = PagoDeCuotas.objects.filter(lote_id=lote_id.id)
                        if object_list:
                            for i in object_list:
                                i.total_de_cuotas=unicode('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                                i.total_de_mora=unicode('{:,}'.format(i.total_de_mora)).replace(",", ".")
                                i.total_de_pago=unicode('{:,}'.format(i.total_de_pago)).replace(",", ".")                                             
                    except Exception, error:
                        print error
                        object_list= []   
                if tipo_busqueda=='cliente':
                    try:
                        cliente_id = request.GET['busqueda']
                        object_list = PagoDeCuotas.objects.filter(cliente_id=cliente_id)    
                        if object_list:
                            for i in object_list:
                                i.total_de_cuotas=unicode('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                                i.total_de_mora=unicode('{:,}'.format(i.total_de_mora)).replace(",", ".")
                                i.total_de_pago=unicode('{:,}'.format(i.total_de_pago)).replace(",", ".")             
                    except Exception, error:
                        print error
                        print i.id
                        pass
                        #object_list= []      
                if tipo_busqueda=='fecha':
                    try:
                        fecha_pago = request.GET['busqueda_label']
                        fecha_hasta = request.GET['fecha_hasta']
                        fecha_pago_parsed = datetime.strptime(fecha_pago, "%d/%m/%Y").date()
                        fecha_hasta_parsed = datetime.strptime(fecha_hasta, "%d/%m/%Y").date()
                        object_list = PagoDeCuotas.objects.filter(fecha_de_pago__range=(fecha_pago_parsed,fecha_hasta_parsed)).order_by('-fecha_de_pago') 
                        if object_list:    
                            for i in object_list:
                                i.total_de_cuotas=unicode('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                                i.total_de_mora=unicode('{:,}'.format(i.total_de_mora)).replace(",", ".")
                                i.total_de_pago=unicode('{:,}'.format(i.total_de_pago)).replace(",", ".")              
                    except Exception, error:
                        print error
                        object_list= [] 
                
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
                    'ultima_busqueda': ultima_busqueda,
                    'tipo_busqueda' : tipo_busqueda,
                    'busqueda_label' : busqueda_label,
                    'fecha_hasta' : fecha_hasta,
                    'busqueda' : busqueda                    
                })                    
                return HttpResponse(t.render(c))
        else:
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))     
    else: 
        return HttpResponseRedirect(reverse('login'))
    
    
def listar_busqueda_reservas(request):
    
    if request.user.is_authenticated():    
        if request.method=='POST':
            try:
                t = loader.get_template('movimientos/listado_reservas.html')
                busqueda = request.POST['busqueda']
                tipo_busqueda=request.POST['tipo_busqueda']
                fecha_hasta=request.POST['fecha_hasta']
                
                if tipo_busqueda=='lote':
                    try:
                        x=unicode(busqueda)
                        fraccion_int = int(x[0:3])
                        manzana_int =int(x[4:7])
                        lote_int = int(x[8:])
                    except Exception, error:
                        print error 
                        #return HttpResponseServerError("Datos erroneos, favor cargar el numero de lote con el formato Fraccion/Manzana/Lote.")       
                                          
                    try:
                        manzana_id=Manzana.objects.get(fraccion_id=fraccion_int,nro_manzana=manzana_int)
                        lote_id=Lote.objects.get(manzana_id=manzana_id,nro_lote=lote_int)
                        object_list = Reserva.objects.filter(lote_id=lote_id.id)
                        a = len(object_list)    
                        #if a > 0:
                            #for i in object_list:
                                #i.fecha_de_reserva=i.fecha_de_reserva.strftime("%d/%m/%Y")         
                        
                        ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
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
                                'ultima_busqueda': ultima_busqueda,
                        })
                    except:
                        c = RequestContext(request, {
                            'object_list': [],
                        })                
                    return HttpResponse(t.render(c)) 
                
                if tipo_busqueda=='cliente':
                    try:
                        object_list = Cliente.objects.filter(nombres__icontains=busqueda)    
                        res=[]
                        cantRes=0
                        cantClientes=0
                        for i in object_list:
                            resAux=list(Reserva.objects.filter(cliente_id=i.id))
                            if resAux:
                                res.append(resAux)
                        #f = []
                    
                        a = len(object_list)
                        cantClientes=len(res)    
                        #if a > 0:
                        #    for c in range(0,cantClientes):
                        #        cantRes=len(res[c])
                        #        for v in range (0,cantRes):
                        #            res[c][v].fecha_de_reserva = res[c][v].fecha_de_reserva.strftime("%d/%m/%Y")
                                
                   
                        ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
                        paginator=Paginator(res,15)
                        page=request.GET.get('page')
                        try:
                            lista=paginator.page(page)
                        except PageNotAnInteger:
                            lista=paginator.page(1)
                        except EmptyPage:
                            lista=paginator.page(paginator.num_pages)
                
                        c = RequestContext(request, {
                            'object_list': lista,
                            'ultima_busqueda': ultima_busqueda,
                            'busqueda': 'cliente',
                        })
                    except:
                        c = RequestContext(request, {
                            'object_list': [],
                        })
                    return HttpResponse(t.render(c))     
                
                if tipo_busqueda=='fecha':
                    try:
                        fecha_reserva_parsed = datetime.strptime(busqueda, "%d/%m/%Y").date()
                        fecha_hasta_parsed = datetime.strptime(fecha_hasta, "%d/%m/%Y").date()
                        object_list = Reserva.objects.filter(fecha_de_reserva__range=(fecha_reserva_parsed,fecha_hasta_parsed))
                        a = len(object_list)    
                        #if a > 0:
                        #for i in object_list:
                        #    i.fecha_de_reserva=i.fecha_de_reserva.strftime("%d/%m/%Y")
                
                        ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
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
                            'ultima_busqueda': ultima_busqueda,
                        })
                    except:
                        c = RequestContext(request, {
                            'object_list': [],
                        })
                    return HttpResponse(t.render(c))                      
            except:
                return HttpResponseServerError("Error en la ejecucion") 
        else:
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                try:
                    t = loader.get_template('movimientos/listado_reservas.html')
                    busqueda = request.GET['busqueda']
                    tipo_busqueda=request.GET['tipo_busqueda']
                    fecha_hasta=request.GET['fecha_hasta']
                    
                    if tipo_busqueda=='lote':
                        try:
                            x=unicode(busqueda)
                            fraccion_int = int(x[0:3])
                            manzana_int =int(x[4:7])
                            lote_int = int(x[8:])
                        except Exception, error:
                            print error 
                            #return HttpResponseServerError("Datos erroneos, favor cargar el numero de lote con el formato Fraccion/Manzana/Lote.")       
                                         
                        try:
                            manzana_id=Manzana.objects.get(fraccion_id=fraccion_int,nro_manzana=manzana_int)
                            lote_id=Lote.objects.get(manzana_id=manzana_id,nro_lote=lote_int)
                            object_list = Reserva.objects.filter(lote_id=lote_id.id)
                            a = len(object_list)    
                            #if a > 0:
                            #    for i in object_list:
                            #        i.fecha_de_reserva=i.fecha_de_reserva.strftime("%d/%m/%Y")         
                            
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
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
                                    'ultima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        
                        return HttpResponse(t.render(c)) 
                    
                    if tipo_busqueda=='cliente':
                        try:
                            object_list = Cliente.objects.filter(nombres__icontains=busqueda)    
                            res=[]
                            cantRes=0
                            cantClientes=0
                            for i in object_list:
                                resAux=list(Reserva.objects.filter(cliente_id=i.id))
                                if resAux:
                                    res.append(resAux)          
                            a = len(object_list)
                            cantClientes=len(res)    
                            #if a > 0:
                            #    for c in range(0,cantClientes):
                            #        cantRes=len(res[c])
                            #        for v in range (0,cantRes):
                            #            res[c][v].fecha_de_reserva = res[c][v].fecha_de_reserva.strftime("%d/%m/%Y")
         
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
                            paginator=Paginator(res,15)
                            page=request.GET.get('page')
                            try:
                                lista=paginator.page(page)
                            except PageNotAnInteger:
                                lista=paginator.page(1)
                            except EmptyPage:
                                lista=paginator.page(paginator.num_pages)
                    
                            c = RequestContext(request, {
                                'object_list': lista,
                                'ultima_busqueda': ultima_busqueda,
                                'busqueda': 'cliente',
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))  
                    
                    if tipo_busqueda=='fecha':
                        try:
                            fecha_reserva_parsed = datetime.strptime(busqueda, "%d/%m/%Y").date()
                            fecha_hasta_parsed = datetime.strptime(fecha_hasta, "%d/%m/%Y").date()
                            object_list = Reserva.objects.filter(fecha_de_reserva__range=(fecha_reserva_parsed,fecha_hasta_parsed))    
                            a = len(object_list)    
                            #if a > 0:
                                #for i in object_list:
                                    #i.fecha_de_reserva=i.fecha_de_reserva.strftime("%d/%m/%Y")
                    
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
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
                                'ultima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))  
                              
                except Exception, error:
                    print error 
                    #return HttpResponseServerError("Error en la ejecucion")
            else:
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
        
def listar_busqueda_transferencias(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            if request.method=='POST':
                try:
                    t = loader.get_template('movimientos/listado_transferencias.html')
                    busqueda = request.POST['busqueda']
                    tipo_busqueda=request.POST['tipo_busqueda']
                    fecha_hasta=request.POST['fecha_hasta']
                
                    if tipo_busqueda=='lote':
                        try:
                            x=unicode(busqueda)
                            fraccion_int = int(x[0:3])
                            manzana_int =int(x[4:7])
                            lote_int = int(x[8:])
                        except Exception, error:
                            print error 
                            return HttpResponseServerError("Datos erroneos, favor cargar el numero de lote con el formato Fraccion/Manzana/Lote.")       
                        try:
                            manzana_id=Manzana.objects.get(fraccion_id=fraccion_int,nro_manzana=manzana_int)
                            lote_id=Lote.objects.get(manzana_id=manzana_id,nro_lote=lote_int)
                            object_list = TransferenciaDeLotes.objects.filter(lote_id=lote_id.id)
                            a = len(object_list)    
                            #if a > 0:
                                #for i in object_list:
                                    #i.fecha_de_transferencia=i.fecha_de_transferencia.strftime("%d/%m/%Y")         
                        
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
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
                                'ultima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })                
                        return HttpResponse(t.render(c)) 
                        
                    if tipo_busqueda=='fecha':
                        try:
                            fecha_transferencia_parsed = datetime.strptime(busqueda, "%d/%m/%Y").date()
                            fecha_hasta_parsed = datetime.strptime(fecha_hasta, "%d/%m/%Y").date()
                            object_list = TransferenciaDeLotes.objects.filter(fecha_de_transferencia__range=(fecha_transferencia_parsed,fecha_hasta_parsed)) 
                    
                            a = len(object_list)    
                            #if a > 0:
                            #    for i in object_list:
                                    #i.fecha_de_transferencia=i.fecha_de_transferencia.strftime("%d/%m/%Y")
                               
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda                     
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
                                'ultima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))  
                except Exception, error:
                    print error 
                    #return HttpResponseServerError("Error en la ejecucion")
        else:
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
def listar_busqueda_cambios(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            if request.method=='POST':
                try:
                    t = loader.get_template('movimientos/listado_cambios.html')
                    busqueda = request.POST['busqueda']
                    tipo_busqueda=request.POST['tipo_busqueda']
                    fecha_hasta=request.POST['fecha_hasta']
                    if tipo_busqueda=='cliente':
                        try:
                            object_list = Cliente.objects.filter(nombres__icontains=busqueda)    
                            cambio=[]
                            cantCambios=0
                            cantClientes=0
                            for i in object_list:
                                cambioAux=list(CambioDeLotes.objects.filter(cliente_id=i.id))
                                if cambioAux:
                                    cambio.append(cambioAux)
                        
                            a = len(object_list)
                            cantClientes=len(cambio)    
                            if a > 0:
                                for c in range(0,cantClientes):
                                    cantCambios=len(cambio[c])
                                    #for v in range (0,cantCambios):
                                        #cambio[c][v].fecha_de_cambio = cambio[c][v].fecha_de_cambio.strftime("%d/%m/%Y")
                                                   
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
                            paginator=Paginator(cambio,15)
                            page=request.GET.get('page')
                            try:
                                lista=paginator.page(page)
                            except PageNotAnInteger:
                                lista=paginator.page(1)
                            except EmptyPage:
                                lista=paginator.page(paginator.num_pages)
                 
                            c = RequestContext(request, {
                                'object_list': lista,
                                'ultima_busqueda': ultima_busqueda,
                                'busqueda': 'cliente',
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))  
                        
                    if tipo_busqueda=='fecha':
                        try:
                            fecha_cambio_parsed = datetime.strptime(busqueda, "%d/%m/%Y").date()
                            fecha_hasta_parsed = datetime.strptime(fecha_hasta, "%d/%m/%Y").date()
                            object_list = CambioDeLotes.objects.filter(fecha_de_cambio__range=(fecha_cambio_parsed,fecha_hasta_parsed)) 
                        
                            a = len(object_list)    
                            #if a > 0:
                                #for i in object_list:
                                    #i.fecha_de_cambio=i.fecha_de_cambio.strftime("%d/%m/%Y")
                                           
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda                     
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
                                'ultima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))             
                except Exception, error:
                    print error 
                    #return HttpResponseServerError("Error en la ejecucion")     
            else:
                try:
                    t = loader.get_template('movimientos/listado_cambios.html')
                    busqueda = request.POST['busqueda']
                    tipo_busqueda=request.POST['tipo_busqueda']
                    fecha_hasta=request.POST['fecha_hasta']
                    
                    if tipo_busqueda=='cliente':
                        try:
                            object_list = Cliente.objects.filter(nombres__icontains=busqueda)    
                            cambio=[]
                            cantCambios=0
                            cantClientes=0
                            for i in object_list:
                                cambioAux=list(CambioDeLotes.objects.filter(cliente_id=i.id))
                                if cambioAux:
                                    cambio.append(cambioAux)
                        
                            a = len(object_list)
                            cantClientes=len(cambio)    
                            if a > 0:
                                for c in range(0,cantClientes):
                                    cantCambios=len(cambio[c])
                                    #for v in range (0,cantCambios):
                                        #cambio[c][v].fecha_de_cambio = cambio[c][v].fecha_de_cambio.strftime("%d/%m/%Y")
                                                   
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
                            paginator=Paginator(cambio,15)
                            page=request.GET.get('page')
                            try:
                                lista=paginator.page(page)
                            except PageNotAnInteger:
                                lista=paginator.page(1)
                            except EmptyPage:
                                lista=paginator.page(paginator.num_pages)
                    
                            c = RequestContext(request, {
                                'object_list': lista,
                                'ultima_busqueda': ultima_busqueda,
                                'busqueda': 'cliente',
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))      
                        
                    if tipo_busqueda=='fecha':
                        try:
                            fecha_cambio_parsed = datetime.strptime(busqueda, "%d/%m/%Y").date()
                            fecha_hasta_parsed = datetime.strptime(fecha_hasta, "%d/%m/%Y").date()
                            object_list = CambioDeLotes.objects.filter(fecha_de_cambio__range=(fecha_cambio_parsed,fecha_hasta_parsed)) 
                        
                            a = len(object_list)    
                            #if a > 0:
                                #for i in object_list:
                                    #i.fecha_de_cambio=i.fecha_de_cambio.strftime("%d/%m/%Y")
                                           
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda                     
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
                                'ultima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))             
                except Exception, error:
                    print error 
                    #return HttpResponseServerError("Error en la ejecucion")
        else:
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
        
def listar_busqueda_recuperacion(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            if request.method=='POST':
                try:
                    t = loader.get_template('movimientos/listado_recuperacion.html')
                    busqueda = request.POST['busqueda']
                    tipo_busqueda=request.POST['tipo_busqueda']
                    fecha_hasta=request.POST['fecha_hasta']
                    
                    if tipo_busqueda=='lote':
                        try:
                            x=unicode(busqueda)
                            fraccion_int = int(x[0:3])
                            manzana_int =int(x[4:7])
                            lote_int = int(x[8:])
                        except Exception, error:
                            print error 
                            #return HttpResponseServerError("Datos erroneos, favor cargar el numero de lote con el formato Fraccion/Manzana/Lote.")       
                                      
                        try:
                            manzana_id=Manzana.objects.get(fraccion_id=fraccion_int,nro_manzana=manzana_int)
                            lote_id=Lote.objects.get(manzana_id=manzana_id,nro_lote=lote_int)
                            object_list = RecuperacionDeLotes.objects.filter(lote_id=lote_id.id)
                            a = len(object_list)    
                            #if a > 0:
                                #for i in object_list:
                                    #i.fecha_de_recuperacion=i.fecha_de_recuperacion.strftime("%d/%m/%Y")         
                            
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda    
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
                                'utlima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })                 
                        return HttpResponse(t.render(c))       
                        
                    if tipo_busqueda=='cliente':
                        try:
                            object_list = Cliente.objects.filter(nombres__icontains=busqueda)    
                            rec=[]
                            cantRec=0
                            cantClientes=0
                            for i in object_list:
                                recAux=list(RecuperacionDeLotes.objects.filter(cliente_id=i.id))
                                if recAux:
                                    rec.append(recAux)
                        
                            a = len(object_list)
                            cantClientes=len(rec)    
                            if a > 0:
                                for c in range(0,cantClientes):
                                    cantRec=len(rec[c])
                                    #for v in range (0,cantRec):
                                        #rec[c][v].fecha_de_recuperacion = rec[c][v].fecha_de_recuperacion.strftime("%d/%m/%Y")
                     
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
                            paginator=Paginator(rec,15)
                            page=request.GET.get('page')
                            try:
                                lista=paginator.page(page)
                            except PageNotAnInteger:
                                lista=paginator.page(1)
                            except EmptyPage:
                                lista=paginator.page(paginator.num_pages)
                    
                            c = RequestContext(request, {
                                'object_list': lista,
                                'ultima_busqueda': ultima_busqueda,
                                'busqueda': 'cliente',
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))     
                    
                    if tipo_busqueda=='fecha':
                        try:
                            fecha_recuperacion_parsed = datetime.strptime(busqueda, "%d/%m/%Y").date()
                            fecha_hasta_parsed = datetime.strptime(fecha_hasta, "%d/%m/%Y").date()
                            object_list = RecuperacionDeLotes.objects.filter(fecha_de_recuperacion__range=(fecha_recuperacion_parsed,fecha_hasta_parsed))    
                        
                            a = len(object_list)    
                            #if a > 0:
                                #for i in object_list:
                                    #i.fecha_de_recuperacion=i.fecha_de_recuperacion.strftime("%d/%m/%Y")
                    
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda    
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
                                'ultima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))                    
                except Exception, error:
                    print error 
                    #return HttpResponseServerError("Error en la ejecucion") 
            else:
                try:
                    t = loader.get_template('movimientos/listado_recuperacion.html')
                    busqueda = request.POST['busqueda']
                    tipo_busqueda=request.POST['tipo_busqueda']
                    fecha_hasta=request.POST['fecha_hasta']
                    
                    if tipo_busqueda=='lote':
                        try:
                            x=unicode(busqueda)
                            fraccion_int = int(x[0:3])
                            manzana_int =int(x[4:7])
                            lote_int = int(x[8:])
                        except Exception, error:
                            print error 
                            #return HttpResponseServerError("Datos erroneos, favor cargar el numero de lote con el formato Fraccion/Manzana/Lote.")       
                         
                        try:
                            manzana_id=Manzana.objects.get(fraccion_id=fraccion_int,nro_manzana=manzana_int)
                            lote_id=Lote.objects.get(manzana_id=manzana_id,nro_lote=lote_int)
                            object_list = RecuperacionDeLotes.objects.filter(lote_id=lote_id.id)
                            a = len(object_list)    
                            #if a > 0:
                                #for i in object_list:
                                    #i.fecha_de_recuperacion=i.fecha_de_recuperacion.strftime("%d/%m/%Y")         
                            
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda    
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
                                    'utlima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        
                        return HttpResponse(t.render(c))       
                        
                    if tipo_busqueda=='cliente':
                        try:
                            object_list = Cliente.objects.filter(nombres__icontains=busqueda)    
                            rec=[]
                            cantRec=0
                            cantClientes=0
                            for i in object_list:
                                recAux=list(RecuperacionDeLotes.objects.filter(cliente_id=i.id))
                                if recAux:
                                    rec.append(recAux)                
                                
                            a = len(object_list)
                            cantClientes=len(rec)    
                            if a > 0:
                                for c in range(0,cantClientes):
                                    cantRec=len(rec[c])
                                    #for v in range (0,cantRec):
                                        #rec[c][v].fecha_de_recuperacion = rec[c][v].fecha_de_recuperacion.strftime("%d/%m/%Y")
               
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda      
                            paginator=Paginator(rec,15)
                            page=request.GET.get('page')
                            try:
                                lista=paginator.page(page)
                            except PageNotAnInteger:
                                lista=paginator.page(1)
                            except EmptyPage:
                                lista=paginator.page(paginator.num_pages)
                    
                            c = RequestContext(request, {
                                'object_list': lista,
                                'ultima_busqueda': ultima_busqueda,
                                'busqueda': 'cliente',
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))    
                    
                    if tipo_busqueda=='fecha':
                        try:                    
                            fecha_recuperacion_parsed = datetime.strptime(busqueda, "%d/%m/%Y").date()
                            fecha_hasta_parsed = datetime.strptime(fecha_hasta, "%d/%m/%Y").date()
                            object_list = RecuperacionDeLotes.objects.filter(fecha_de_recuperacion__range=(fecha_recuperacion_parsed,fecha_hasta_parsed))    
                        
                            a = len(object_list)    
                            #if a > 0:
                                #for i in object_list:
                                    #i.fecha_de_recuperacion=i.fecha_de_recuperacion.strftime("%d/%m/%Y")
                    
                            ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda    
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
                                'ultima_busqueda': ultima_busqueda,
                            })
                        except:
                            c = RequestContext(request, {
                                'object_list': [],
                            })
                        return HttpResponse(t.render(c))                    
                except Exception, error:
                    print error 
                    #return HttpResponseServerError("Error en la ejecucion")
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

def modificar_pago_de_cuotas(request, id):        
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.CHANGE_PAGODECUOTAS):
            if request.method == 'GET':
                pago = PagoDeCuotas.objects.get(pk=id)
                fecha = pago.fecha_de_pago.strftime('%d/%m/%Y')
                t = loader.get_template('movimientos/modificar_pagocuota.html')
                c = RequestContext(request, {
                    'pagocuota': pago,
                    'fecha_pago': fecha
                })
            
            if request.method == 'POST':
                pago = PagoDeCuotas.objects.get(pk=id)
                data = request.POST    
                lote_id = data.get('pago_lote_id', '')
                nro_cuotas_a_pagar = data.get('nro_cuotas_a_pagar')
                venta = pago.venta
                venta.pagos_realizados = int(nro_cuotas_a_pagar) + int(venta.pagos_realizados)
                monto_cuota = data.get('monto_cuota')
                total_de_cuotas = int(monto_cuota) * int(nro_cuotas_a_pagar)
                total_de_mora = data.get('total_mora')
                total_de_pago = data.get('monto_total')
                date_parse_error = False
                fecha_pago=data.get('fecha', '')
                fecha_pago_parsed = datetime.strptime(fecha_pago, "%d/%m/%Y").date()
    
                try:
                    pago.total_de_cuotas = total_de_cuotas
                    pago.total_de_mora = total_de_mora
                    pago.total_de_pago = total_de_pago
                    pago.nro_cuotas_a_pagar = nro_cuotas_a_pagar
                    pago.fecha_de_pago = fecha_pago_parsed
                    pago.save()
                except Exception, error:
                    print error
                    pass
                venta.save()
                t = loader.get_template('movimientos/modificar_pagocuota.html')
                fecha = pago.fecha_de_pago.strftime('%d/%m/%Y')
                c = RequestContext(request, {
                    'pagocuota': pago,
                    'fecha_pago': fecha
                })
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")   
        
    '''
    def eliminar_pago_de_cuotas(request, id):        
        if request.user.is_authenticated():
            if request.method == 'GET':
                lote = pago.lote.codigo_paralot
                pago = PagoDeCuotas.objects.get(pk=id)
                pago.delete()
                t = loader.get_template('informes/informe_movimientos.html')
                c = RequestContext(request, {
                    'lote_id': lote,
                    'fecha_ini':"",
                    'fecha_fin':""
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect("/login")'''

def modificar_venta(request, id):        
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.CHANGE_VENTA):
            if request.method == 'GET':
                venta = Venta.objects.get(pk=id)
                fecha_venta = venta.fecha_de_venta.strftime('%d/%m/%Y')
                if venta.fecha_primer_vencimiento != "":
                    fecha_primer_venc = venta.fecha_primer_vencimiento.strftime('%d/%m/%Y')
                else:
                    fecha_primer_venc = ""
                t = loader.get_template('movimientos/modificar_venta.html')
                c = RequestContext(request, {
                    'venta': venta,
                    'fecha_venta': fecha_venta,
                    'fecha_primer_venc': fecha_primer_venc
                })
            
            if request.method == 'POST':
                venta = Venta.objects.get(pk=id)
                data = request.POST            
                fecha_de_venta = data.get('fecha_de_venta', '')
                fecha_de_venta_parsed = datetime.datetime.strptime(fecha_de_venta, "%d/%m/%Y").date()            
                fecha_primer_venc = data.get('fecha_primer_venc', '')
                fecha_primer_venc_parsed = datetime.datetime.strptime(fecha_primer_venc, "%d/%m/%Y").date()
                id_cliente = data.get('cliente', '')
                cliente = Cliente.objects.get(pk=int(id_cliente))
                id_plandepago = data.get('plan_de_pago', '')
                plandepago = PlanDePago.objects.get(pk=int(id_plandepago))
                id_vendedor = data.get('vendedor', '')
                vendedor = Vendedor.objects.get(pk=int(id_vendedor))
                pagos_realizados = data.get('pagos_realizados', '')
                entrega_inicial = data.get('entrega_inicial', '')
                #entrega_inicial_sin_puntos = entrega_inicial.strip('.')
                precio_de_cuota = data.get('precio_de_cuota', '')
                #precio_de_cuota_sin_puntos = precio_de_cuota.strip('.') precio_de_cuota.translate(None, string.punctuation)
                precio_final_venta = data.get('precio_final_venta', '')
                #precio_final_venta_sin_puntos = precio_final_venta.strip('.').
                try:
                    venta.fecha_de_venta = fecha_de_venta_parsed
                    venta.fecha_primer_vencimiento = fecha_primer_venc_parsed
                    venta.entrega_inicial = int(entrega_inicial)
                    venta.precio_de_cuota = int(precio_de_cuota)
                    venta.precio_final_de_venta = int(precio_final_venta)
                    venta.pagos_realizados = int(pagos_realizados)
                    venta.plan_de_pago = plandepago
                    venta.cliente = cliente
                    venta.vendedor = vendedor
                    venta.save()
                    object_list = PagoDeCuotas.objects.filter(venta_id=venta).order_by('fecha_de_pago')
                    for pago in object_list:
                        pago.plan_de_pago = venta.plan_de_pago
                        pago.vendedor = venta.vendedor
                        pago.cliente = venta.cliente
                        pago.save()
                except Exception, error:
                    print error
                t = loader.get_template('movimientos/modificar_venta.html')
                fecha_venta = venta.fecha_de_venta.strftime('%d/%m/%Y')
                fecha_primer_venc = venta.fecha_primer_vencimiento.strftime('%d/%m/%Y')
                c = RequestContext(request, {
                    'venta': venta,
                    'fecha_venta': fecha_venta,
                    'fecha_primer_venc': fecha_primer_venc
                })
                return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))                        
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")
    
def eliminar_venta(request):        
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.DELETE_VENTA):           
            if request.method == 'POST':
                data = request.POST
                pagos = None
                id= int(data.get('venta_id'))
                venta = Venta.objects.get(pk=id)            
                pagos = PagoDeCuotas.objects.filter(venta_id=venta.id)
                if len(pagos) == 0:
                    try:
                        venta.delete()
                        ok=True
                    except Exception, error:
                        print error
                    
                else:
                    ok=False
                data = json.dumps({
                    'ok': ok})
                return HttpResponse(data,content_type="application/json")
    else:
        return HttpResponseRedirect("/login")
    
        