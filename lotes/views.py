from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Lote, Venta, Manzana, Fraccion, Propietario, Cliente, RecuperacionDeLotes, Reserva, \
    PlanDePago, PagoDeCuotas, PlanDePagoVendedor, Vendedor
from lotes.forms import LoteForm, FraccionManzana
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
import json
import datetime
from datetime import datetime
from django.core.urlresolvers import reverse, resolve
# Funcion principal del modulo de lotes.
from principal.common_functions import *
from principal import permisos
from django.contrib.auth.models import User
from django.db import connection
def lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_OPCIONES):
            t = loader.get_template('lotes/index.html')
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

# Funcion para consultar el listado de todas las lotes.
def consultar_lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_LOTES):
            t = loader.get_template('lotes/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    object_list = Lote.objects.all().order_by( 'manzana__fraccion','manzana__nro_manzana', 'nro_lote')[:15]
    
    for lote in object_list:
        if lote.estado == '3':
            try:
                venta = Venta.objects.filter(lote_id = lote.id).order_by('-fecha_de_venta')
                venta = venta[0]
                cliente = venta.cliente
                lote.cliente = cliente
            except Exception, error:
                lote.cliente = 'Lote de estado "vendido" sin venta asociada'
                print "El lote vendido no esta asociado a una venta."
        
        
    
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

# Funcion para consultar el proximo pago de los lotes.
def consultar_proximo_pago_lote(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_PAGODECUOTAS):
            t = loader.get_template('movimientos/consulta_cuotas.html')
            grupo = request.user.groups.get().id
            if request.method == 'POST':
                data = request.POST
                lote_id = data.get('pago_lote_id', '')
                nro_cuotas_a_pagar = data.get('pago_nro_cuotas_a_pagar')

                #############################################################
                # Codigo agregado: contemplar el caso de los lotes recuperados
                venta = get_ultima_venta(lote_id)
                #############################################################

                venta.pagos_realizados = int(nro_cuotas_a_pagar) + int(venta.pagos_realizados)
                cliente_id = data.get('pago_cliente_id')
                vendedor_id = data.get('pago_vendedor_id')
                plan_pago_id = data.get('pago_plan_de_pago_id')
                plan_pago_vendedor_id = data.get('pago_plan_de_pago_vendedor_id')
                total_de_cuotas = data.get('pago_total_de_cuotas')
                total_de_mora = data.get('pago_total_de_mora')
                total_de_pago = data.get('pago_total_de_pago')
                date_parse_error = False
                fecha_pago = data.get('pago_fecha_de_pago', '')
                fecha_pago_parsed = datetime.datetime.strptime(fecha_pago, "%d/%m/%Y").date()
                detalle = data.get('detalle', '')
                if detalle == '':
                    detalle = None
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
                # print fecha_pago
                # print fecha_pago_parsed
                cantidad_cuotas = PlanDePago.objects.get(pk=plan_pago_id)
                cuotas_pagadas = Venta.objects.get(pk=venta.id)
                cuotas_restantes = int(cantidad_cuotas.cantidad_de_cuotas) - int(cuotas_pagadas.pagos_realizados)
                if cuotas_restantes >= int(nro_cuotas_a_pagar):
                    try:
                        nuevo_pago = PagoDeCuotas()
                        nuevo_pago.venta = Venta.objects.get(pk=venta.id)
                        nuevo_pago.lote = Lote.objects.get(pk=lote_id)
                        nuevo_pago.fecha_de_pago = fecha_pago_parsed
                        nuevo_pago.nro_cuotas_a_pagar = nro_cuotas_a_pagar
                        nuevo_pago.cliente = Cliente.objects.get(pk=cliente_id)
                        nuevo_pago.plan_de_pago = PlanDePago.objects.get(pk=plan_pago_id)
                        nuevo_pago.plan_de_pago_vendedores = PlanDePagoVendedor.objects.get(pk=plan_pago_vendedor_id)
                        nuevo_pago.vendedor = Vendedor.objects.get(pk=vendedor_id)
                        nuevo_pago.total_de_cuotas = total_de_cuotas
                        nuevo_pago.total_de_mora = total_de_mora
                        nuevo_pago.total_de_pago = total_de_pago
                        nuevo_pago.detalle = detalle
                        nuevo_pago.save()

                        # Se loggea la accion del usuario
                        id_objeto = nuevo_pago.id
                        codigo_lote = nuevo_pago.lote.codigo_paralot
                        loggear_accion(request.user, "Agregar", "Pago de cuota", id_objeto, codigo_lote)


                    except Exception, error:
                        print error
                        pass
                    venta.save()

                    # Vuelve al template
                    # c = RequestContext(request, {})
                    # return HttpResponse(t.render(c))

                    # Redirecciona a facturacion (al final hace esto en movimientos_pagos.js
                    # return HttpResponseRedirect("/facturacion/facturar")

                    # retorna el objeto como json
                    object_list = PagoDeCuotas.objects.filter(id=nuevo_pago.id)
                    labels = ["id"]
                    from django.core.serializers.json import DjangoJSONEncoder
                    from django.core.serializers import json
                    return HttpResponse(json.dumps(custom_json(object_list, labels), cls=DjangoJSONEncoder),
                                        content_type="application/json")

                else:
                    return HttpResponseServerError(
                        "La cantidad de cuotas a pagar, es mayor a la cantidad de cuotas restantes.")

            elif request.method == 'GET':
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo = request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")


# Funcion para el detalle de una fraccion: edita o borra una fraccion.
def detalle_lote(request, lote_id):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_LOTES):
            t = loader.get_template('lotes/detalle.html')
            grupo= request.user.groups.get().id
    
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))     

    object_list = Lote.objects.get(pk=lote_id)
    message = ''
    message_id = "message"
    
    ventas_relacionadas = Venta.objects.filter(lote=lote_id)

    if request.method == 'POST':
        request.POST = request.POST.copy()
        data = request.POST
        if data.get('boton_guardar'):
            form = LoteForm(data, instance=object_list)
            if data['boleto_nro'] == '':
                data['boleto_nro'] = 0
            data['nro_lote'] = int(data['nro_lote'])    
            data['precio_contado'] = int(data['precio_contado'].replace(".", "")) 
            data['precio_credito'] = int(data['precio_credito'].replace(".", ""))
            data['precio_costo'] = int(data['precio_costo'].replace(".", ""))
            data['cuota'] = int(data['cuota'].replace(".", ""))
            if form.is_valid():
                message = "Se actualizaron los datos."
                message_id = "message-success"
                form.save(commit=False)
                
                #Se loggea la accion del usuario
                id_objeto = form.instance.id
                codigo_lote = form.instance.codigo_paralot
                loggear_accion(request.user, "Actualizar", "Lote", id_objeto, codigo_lote)
                if object_list.boleto_nro == '':
                    object_list.boleto_nro = 0
                object_list.save()
        elif data.get('boton_borrar'):
            f = Lote.objects.get(pk=lote_id)
            codigo_lote = f.codigo_paralot
            f.delete()
            
            #Se loggea la accion del usuario
            id_objeto = lote_id
            loggear_accion(request.user, "Borrar lote("+codigo_lote+")", "Factura", id_objeto, codigo_lote)
            
            #return HttpResponseRedirect('/lotes/listado')
            return HttpResponseRedirect(reverse('frontend_lotes_index'))
        
        elif data.get('boton_guardar_a_recuperacion'):
            form = LoteForm(data, instance=object_list)
            if data['boleto_nro'] == '':
                data['boleto_nro'] = 0
            data['nro_lote'] = int(data['nro_lote'])    
            data['precio_contado'] = int(data['precio_contado'].replace(".", "")) 
            data['precio_credito'] = int(data['precio_credito'].replace(".", ""))
            data['precio_costo'] = int(data['precio_costo'].replace(".", ""))
            if form.is_valid():
                message = "Se actualizaron los datos."
                message_id = "message-success"
                form.save(commit=False)
                
                #Se loggea la accion del usuario
                id_objeto = form.instance.id
                codigo_lote = form.instance.codigo_paralot
                loggear_accion(request.user, "Actualizar", "Lote", id_objeto, codigo_lote)
                if object_list.boleto_nro == '':
                    object_list.boleto_nro = 0
                object_list.save()
            
            #return HttpResponseRedirect('/movimientos/recuperacion_lotes/')
            return HttpResponseRedirect(reverse('frontend_recuperacion_lotes'))
    else:
        form = LoteForm(instance=object_list)
    
    c = RequestContext(request, {
        'lote': object_list,
        'ventas_relacionadas': ventas_relacionadas,
        'form': form,
        'message_id': message_id,
        'message': message,
        'grupo': grupo
    })
    return HttpResponse(t.render(c))

# Funcion que detalla las ventas relacionadas a un lote determinado.
def detalle_ventas_lote(request, venta_id):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_LOTES):  
            t = loader.get_template('lotes/detalle_ventas.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))  
    
    try:
        venta = Venta.objects.get(pk=venta_id)
        venta.fecha_de_venta=venta.fecha_de_venta.strftime("%d/%m/%Y")
        venta.precio_final_de_venta=unicode('{:,}'.format(venta.precio_final_de_venta)).replace(",", ".")
        c = RequestContext(request, {
            'venta': venta,
            })
        return HttpResponse(t.render(c))
    except:    
        return HttpResponseServerError("No se pudo obtener el Detalle de Venta del Lote.") 

# Funcion para agregar un nuevo lote.
def agregar_lotes(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_LOTE):
            t = loader.get_template('lotes/agregar2.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo                                     })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    message = ""    

    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            form.save()
            id_objeto = form.instance.id
            codigo_lote = form.instance.codigo_paralot
            
            ##id_objeto = 1
            #codigo_lote = 'lalala'
            # Redireccionamos al listado de lotes luego de agregar el nuevo lote.
            loggear_accion(request.user, "Agregar", "Lote", id_objeto, codigo_lote)
            #return HttpResponseRedirect('/lotes/listado')
            return HttpResponseRedirect(reverse('frontend_listado_lote'))
        else:
            form = LoteForm()
            form2 = FraccionManzana()
            message = "Debe Completar los campos requeridos"
            
    else:
        form = LoteForm()
        form2 = FraccionManzana()

    c = RequestContext(request, {
        'form': form,
        'form2': form2,
        'message': message,
    })
    return HttpResponse(t.render(c))



def listar_busqueda_lotes(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_LOTES): 
            t = loader.get_template('lotes/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

    # PARAMETROS RECIBIDOS
    busqueda = request.GET.get('busqueda','')
    tipo_busqueda=request.GET.get('tipo_busqueda','')
    busqueda_label = request.GET.get('busqueda_label','')
    fraccion_segun_estado =   request.GET.get('nombre_frac2_label_value', '')

    if busqueda == '' and busqueda_label == '':
        tipo_busqueda = ''
    
    
    #se busca un lote
    # BUSQUEDA
    lista_ordenada = obtener_lotes_filtrados(busqueda, tipo_busqueda, busqueda_label, fraccion_segun_estado, "numero_lote")

    if request.GET.get('formato-reporte','') == 'pantalla':
        # PAGINACION
        ultima_busqueda = "&tabla=&busqueda=" + busqueda + "&tipo_busqueda=" + tipo_busqueda + "&busqueda_label=" + busqueda_label
        object_list = lista_ordenada

        paginator = Paginator(object_list, 50)
        page = request.GET.get('page')
        try:
            lista = paginator.page(page)
        except PageNotAnInteger:
            lista = paginator.page(1)
        except EmptyPage:
            lista = paginator.page(paginator.num_pages)

        c = RequestContext(request, {
            'object_list': lista,
            'ultima_busqueda': ultima_busqueda,
        })
        return HttpResponse(t.render(c))

    else:
        response = listado_lotes_excel(lista_ordenada)
        return response




   
        
         
    
    
    
    
    