# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Propietario, Fraccion, Lote, Manzana, PagoDeCuotas, Venta, Reserva, CambioDeLotes, RecuperacionDeLotes, TransferenciaDeLotes,Factura, Cliente,Timbrado, TimbradoRangoFacturaUsuario, RangoFactura
from operator import itemgetter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse, resolve
from calendar import monthrange
from principal.common_functions import get_nro_cuota
import json
from django.db import connection
from facturas.forms import FacturaForm
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.units import mm
from num2words import num2words
import xlwt
import math
import json
from principal.common_functions import *
from principal import permisos

def facturacion(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_OPCIONES):
            t = loader.get_template('facturas/index.html')
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


def facturar_operacion(request, tipo_operacion, operacion_id):
    if request.user.is_authenticated():
        if request.method == 'GET':
            
            t = loader.get_template('facturas/facturar_operacion.html')

            # determinamos el grupo al cual pertenece el user en cuestion
            grupo = request.user.groups.get().id
            # retornamos todos los users para que pueda seleccionar
            users = User.objects.all()

            cuota_desde = ''
            cuota_hasta = ''
            
            tipo_venta = ''
            precio_venta = ''
            
            if tipo_operacion == '1':  # PAGO DE CUOTA
                pago = PagoDeCuotas.objects.get(pk=operacion_id)
                cantidad_pagos_anteriores = obtener_cantidad_cuotas_pagadas(pago)
                cuota_desde_num = cantidad_pagos_anteriores - pago.nro_cuotas_a_pagar+1
                # cuota_desde_num = pago.venta.pagos_realizados - pago.nro_cuotas_a_pagar+1
                cuota_desde = unicode(cuota_desde_num)+"/"+unicode( pago.plan_de_pago.cantidad_de_cuotas)
                cuota_hasta = unicode(cuota_desde_num  + pago.nro_cuotas_a_pagar-1)+"/"+unicode( pago.plan_de_pago.cantidad_de_cuotas)
                
            if tipo_operacion == '2':  # VENTA
                venta = Venta.objects.get(pk=operacion_id)
                tipo_venta = "Contado"
                precio_venta = venta.precio_final_de_venta
                entrega_inicial = venta.entrega_inicial
                descripcion = "Venta al Contado de Lote: "+venta.lote.codigo_paralot

            # Se Obtiene el ultimo timbrado cargado
            trfu = TimbradoRangoFacturaUsuario.objects.filter(usuario_id=request.user).latest('timbrado')
            ultimo_timbrado = trfu.timbrado

            # Se pregunta por la fecha de validez del
            hoy = date.today()
            message = ''
            if hoy > ultimo_timbrado.hasta:
                message += 'El último Timbrado agregado ha expirado, agregue un nuevo timbrado.'

            try: 
                ultimaFactura = Factura.objects.filter(rango_factura_id=trfu.rango_factura.id).latest('id')
                ultimo_numero = ultimaFactura.numero.split("-")
                if int(ultimo_numero[2])+1 > int(trfu.rango_factura.nro_hasta):
                    message += ' El numero de factura ha sobrepasado al nro máximo del timbrado, agregue un nuevo timbrado o suba el nro maximo.'
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal)+'-'+unicode(trfu.rango_factura.nro_boca)+'-'+unicode(int(ultimo_numero[2])+1).zfill(7)
            except:
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal)+'-'+unicode(trfu.rango_factura.nro_boca)+'-0000001'
            
            if tipo_operacion == '1':  # PAGO DE CUOTA
                c = RequestContext(request, {
                    'cliente': pago.cliente,
                    'lote': pago.lote.codigo_paralot,
                    'cuota_desde': cuota_desde,
                    'cuota_hasta': cuota_hasta,
                    'ultima_factura': ultima_factura,
                    'ultimo_timbrado_numero': trfu.timbrado.numero,
                    'ultimo_timbrado_id': ultimo_timbrado.id,
                    'tipo_venta': tipo_venta,
                    'precio_venta': precio_venta,
                    'grupo': grupo,
                    'users': users,
                    'message': message,
                })
            if tipo_operacion == '2':  # VENTA
                c = RequestContext(request, {
                    'cliente': venta.cliente,
                    'lote': venta.lote.codigo_paralot,
                    'cuota_desde': '',
                    'cuota_hasta': '',
                    'entrega_inicial': entrega_inicial,
                    'ultima_factura': ultima_factura,
                    'ultimo_timbrado_numero': trfu.timbrado.numero,
                    'ultimo_timbrado_id': ultimo_timbrado.id,
                    'tipo_venta': tipo_venta,
                    'precio_venta': precio_venta,
                    'descripcion': descripcion,
                    'message': message,
                })
            return HttpResponse(t.render(c))
            
        else: #POST se envia el formulario.  
            print 'POST'          
            #Obtener el cliente
            cliente_id = request.POST.get('cliente','')
            
            #Obtener el Lote
            lote_id = request.POST.get('lote','')

            x = unicode(lote_id)
            fraccion_int = int(x[0:3])
            manzana_int = int(x[4:7])
            lote_int = int(x[8:])
            manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
            lote_id = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
            
            #Obtener el TIMBRADO
            timbrado_id = request.POST.get('id_timbrado','')
            
            #Obtener el NUMERO
            numero = request.POST.get('nro_factura','')
            
            #Obtener fecha
            #fecha = datetime.datetime.strptime(request.POST.get('fecha', ''), "%Y-%m-%d")
            fecha = datetime.datetime.strptime(request.POST.get('fecha', ''), "%d/%m/%Y")
            
            #Obtener Tipo (Contado - Crédito)
            tipo = request.POST.get('tipo','')
            
            #Obtener el detalle
            detalle = request.POST.get('detalle','')
            
            #Obtener observacion
            observacion = request.POST.get('observacion','')
            
            
            #Crear un objeto Factura y guardar            
            nueva_factura = Factura()
            nueva_factura.fecha = fecha
            #nueva_factura.timbrado = Timbrado.objects.get(pk=timbrado_id)
            trfu = TimbradoRangoFacturaUsuario.objects.get(timbrado_id = timbrado_id, usuario_id = request.user)
            nueva_factura.rango_factura = trfu.rango_factura
            nueva_factura.numero = numero
            nueva_factura.cliente = Cliente.objects.get(pk=cliente_id)
            nueva_factura.tipo = tipo
            nueva_factura.detalle = detalle
            nueva_factura.lote = lote_id
            nueva_factura.anulado = False
            nueva_factura.observacion = observacion
            nueva_factura.usuario = request.user
            nueva_factura.save()
            
            
            #Se loggea la accion del usuario
            id_objeto = nueva_factura.id
            codigo_lote = request.POST.get('lote','')
            loggear_accion(request.user, "Agregar", "Factura", id_objeto, codigo_lote)
            
            
            #obtener numero de cuotas
            numero_cuota_desde = request.POST.get('nro_cuota_desde','')
            numero_cuota_hasta= request.POST.get('nro_cuota_hasta','')
            if numero_cuota_desde != '' and numero_cuota_hasta !='':
                numero_cuota_desde = request.POST.get('nro_cuota_desde','').split("/") 
                numero_cuota_hasta= request.POST.get('nro_cuota_hasta','').split("/")
                num_desde = int(numero_cuota_desde[0])
                num_hasta = int(numero_cuota_hasta[0])
                
                venta = Venta.objects.get(cliente_id= nueva_factura.cliente.id, lote_id= lote_id.id)
                object_list= get_pago_cuotas(venta, None, None)
                for x in xrange(0,len(object_list)):
                    if num_desde <= int(object_list[x]['nro_cuota']) <= num_hasta:
                        pago = PagoDeCuotas.objects.get(pk=object_list[x]['id'])
                        pago.factura = nueva_factura
                        pago.save()
                         
            return crear_pdf_factura(nueva_factura, request, manzana, lote_id, request.user)
    else:
        return HttpResponseRedirect(reverse('login')) 

# Funcion principal del modulo de facturas.
def facturar(request):    
    if request.user.is_authenticated():
        if request.method == 'GET':
            #Mostrar el formulario basico de factura.            
            t = loader.get_template('facturas/facturar.html')
            # determinamos el grupo al cual pertenece el user en cuestion
            grupo = request.user.groups.get().id
            # retornamos todos los users para que pueda seleccionar
            users = User.objects.all()

            # Se Obtiene el ultimo timbrado cargado
            trfu = TimbradoRangoFacturaUsuario.objects.filter(usuario_id=request.user).latest('timbrado')
            ultimo_timbrado = trfu.timbrado

            # Se pregunta por la fecha de validez del
            hoy = date.today()
            message = ''
            if hoy > ultimo_timbrado.hasta:
                message += 'El último Timbrado agregado ha expirado, agregue un nuevo timbrado.'

            try:
                ultimaFactura = Factura.objects.filter(rango_factura_id=trfu.rango_factura.id).latest('id')
                ultimo_numero = ultimaFactura.numero.split("-")
                if int(ultimo_numero[2]) + 1 > int(trfu.rango_factura.nro_hasta):
                    message += ' El numero de factura ha sobrepasado al nro máximo del timbrado, agregue un nuevo timbrado o suba el nro maximo.'
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal) + '-' + unicode(
                    trfu.rango_factura.nro_boca) + '-' + unicode(int(ultimo_numero[2]) + 1).zfill(7)
            except:
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal) + '-' + unicode(
                    trfu.rango_factura.nro_boca) + '-0000001'
            
            c = RequestContext(request, {
                'ultima_factura': ultima_factura,
                'ultimo_timbrado_numero': trfu.timbrado.numero,
                'ultimo_timbrado_id': ultimo_timbrado.id,
                'grupo': grupo,
                'users': users,
                'message': message,
            })
            return HttpResponse(t.render(c))
        else: #POST se envia el formulario.  
            print 'POST'          
            #Obtener el cliente
            cliente_id = request.POST.get('cliente','')
            
            #Obtener el Lote
            lote_id = request.POST.get('lote','')

            x = unicode(lote_id)
            fraccion_int = int(x[0:3])
            manzana_int = int(x[4:7])
            lote_int = int(x[8:])
            manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
            lote_id = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
            
            #Obtener el TIMBRADO
            timbrado_id = request.POST.get('id_timbrado','')
            
            #Obtener el NUMERO
            numero = request.POST.get('nro_factura','')
            
            #Obtener fecha
            #fecha = datetime.datetime.strptime(request.POST.get('fecha', ''), "%Y-%m-%d")
            fecha = datetime.datetime.strptime(request.POST.get('fecha', ''), "%d/%m/%Y")
            
            #Obtener Tipo (Contado - Crédito)
            tipo = request.POST.get('tipo','')
            
            #Obtener el detalle
            detalle = request.POST.get('detalle','')
            
            #Obtener observacion
            observacion = request.POST.get('observacion','')            
            
            #Crear un objeto Factura y guardar            
            nueva_factura = Factura()
            nueva_factura.fecha = fecha
            trfu = TimbradoRangoFacturaUsuario.objects.get(usuario_id = request.user, timbrado_id = timbrado_id )
            nueva_factura.rango_factura = trfu.rango_factura
            nueva_factura.numero = numero
            nueva_factura.cliente = Cliente.objects.get(pk=cliente_id)
            nueva_factura.tipo = tipo
            nueva_factura.detalle = detalle
            nueva_factura.lote = lote_id
            nueva_factura.anulado = False
            nueva_factura.observacion = observacion
            nueva_factura.usuario = request.user  
            nueva_factura.save()
            
            #Se loggea la accion del usuario
            id_objeto = nueva_factura.id
            codigo_lote = request.POST.get('lote','')
            loggear_accion(request.user, "Agregar", "Factura", id_objeto, codigo_lote)
            
            #obtener numero de cuotas
            numero_cuota_desde = request.POST.get('nro_cuota_desde','')
            numero_cuota_hasta= request.POST.get('nro_cuota_hasta','')
            if numero_cuota_desde != '' and numero_cuota_hasta !='':
                numero_cuota_desde = request.POST.get('nro_cuota_desde','').split("/") 
                numero_cuota_hasta= request.POST.get('nro_cuota_hasta','').split("/")
                num_desde = int(numero_cuota_desde[0])
                num_hasta = int(numero_cuota_hasta[0])
                
                venta = Venta.objects.get(cliente_id= nueva_factura.cliente.id, lote_id= lote_id.id)
                object_list= get_pago_cuotas(venta, None, None)
                for x in xrange(0,len(object_list)):
                    if num_desde <= int(object_list[x]['nro_cuota']) <= num_hasta:
                        pago = PagoDeCuotas.objects.get(pk=object_list[x]['id'])
                        pago.factura = nueva_factura
                        pago.save() 
            return crear_pdf_factura(nueva_factura, request, manzana, lote_id, request.user)

    else:
        return HttpResponseRedirect(reverse('login')) 
    
    
# Funcion para consultar el listado de todas las facturas.
def consultar_facturas(request):
    if request.user.is_authenticated():
        if request.method == 'GET':
            data = request.GET
            # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
            tipo_busqueda = data.get('tipo_busqueda','')
            busqueda = data.get('busqueda','')
            busqueda_label = data.get('busqueda_label','')
            fecha_ini = data.get('fecha_ini', '')
            fecha_fin = data.get('fecha_fin', '')
            if tipo_busqueda == 'rango_fecha':
                fecha_ini_parsed = unicode(datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date())
                fecha_fin_parsed = unicode(datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date())
                object_list = Factura.objects.filter(fecha__range=(fecha_ini_parsed,fecha_fin_parsed)).order_by('id','fecha')                    
                for factura in object_list:
                    monto=0
                    lista_detalles=json.loads(factura.detalle)
                    for key, value in lista_detalles.iteritems():
                        if value['cantidad'] == "" or value['precio_unitario'] == "":
                            print ('Encontramos detalle invalido')
                            monto += 0
                        else:
                            monto += int(int(value['cantidad']) * int(value['precio_unitario']))
                    factura.monto=unicode('{:,}'.format(monto)).replace(",", ".")
            if tipo_busqueda == 'nro_factura':
                object_list = Factura.objects.filter(pk=busqueda).order_by('id','fecha')
                for factura in object_list:
                    monto=0
                    lista_detalles=json.loads(factura.detalle)
                    for key, value in lista_detalles.iteritems():
                        monto+=int(int(value['cantidad'])*int(value['precio_unitario']))
                    factura.monto=unicode('{:,}'.format(monto)).replace(",", ".")

            if tipo_busqueda == '':
                object_list = Factura.objects.all().order_by('-id', '-fecha')
                for factura in object_list:
                    monto = 0
                    lista_detalles = json.loads(factura.detalle)
                    for key, value in lista_detalles.iteritems():
                        if value['cantidad'] == "" or value['precio_unitario'] == "":
                            print ('Encontramos detalle invalido')
                            monto += 0
                        else:
                            monto += int(int(value['cantidad']) * int(value['precio_unitario']))
                    factura.monto = unicode('{:,}'.format(monto)).replace(",", ".")



        paginator=Paginator(object_list,15)
        page=request.GET.get('page','')
        ultima_busqueda = "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin + "&busqueda=" + busqueda + "&busqueda_label=" + busqueda_label + "&tipo_busqueda=" + tipo_busqueda
        try:
            lista=paginator.page(page)
        except PageNotAnInteger:
            lista=paginator.page(1)
        except EmptyPage:
            lista=paginator.page(paginator.num_pages)
    
        t = loader.get_template('facturas/listado.html')
        c = RequestContext(request, {
            'object_list': lista,
            'ultima_busqueda': ultima_busqueda,
            'fecha_ini': fecha_ini,
            'fecha_fin': fecha_fin,
            'busqueda': busqueda,
            'busqueda_label': busqueda_label,
            'tipo_busqueda': tipo_busqueda,
            #'message': message,
        })
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
   

# Funcion para consultar el detalle de una factura.
def detalle_factura(request, factura_id):    
    if request.user.is_authenticated():
        t = loader.get_template('facturas/detalle.html')
        factura = Factura.objects.get(pk=factura_id)
        trfu = TimbradoRangoFacturaUsuario.objects.filter(rango_factura_id= factura.rango_factura.id)[0]
        numero_timbrado = trfu.timbrado.numero 
        lista_detalles=json.loads(factura.detalle)
        detalles=[]
        monto = 0
        grupo= request.user.groups.get().id
        for key, value in lista_detalles.iteritems():
            detalle={}
            #detalle['precio_unitario']=unicode('{:,}'.format(value['precio_unitario']))
            detalle['item']=key
            detalle['cantidad']=value['cantidad']
            detalle['concepto']=value['concepto']
            if value['precio_unitario'] == "":
                detalle['precio_unitario'] = "No se puede obtener precio"
            else:
                detalle['precio_unitario']=unicode('{:,}'.format(int(value['precio_unitario']))).replace(",",".")

            if value['iva_10'] == "":
                detalle['iva_10'] = "No se puede obtener iva 10"
            else:
                detalle['iva_10'] = unicode('{:,}'.format(int(value['iva_10']))).replace(",", ".")

            if value['iva_5'] == "":
                detalle['iva_5'] = "No se puede obtener iva 5"
            else:
                detalle['iva_5'] = unicode('{:,}'.format(int(value['iva_5']))).replace(",", ".")

            if value['exentas'] == "":
                detalle['exentas'] = "No se puede obtener exentas"
            else:
                detalle['exentas'] = unicode('{:,}'.format(int(value['exentas']))).replace(",", ".")

            detalles.append(detalle)
            if value['cantidad'] == "" or value['precio_unitario'] == "":
                monto += 0
            else:
                monto += int(value['cantidad']) * int(value['precio_unitario'])
        if factura.tipo=='co':
            tipo='Contado'
        else:
            tipo='Credito'
        factura.tipo=tipo
        factura.monto =  unicode('{:,}'.format(monto).replace(",","."))
        message = ''
            
        if request.method == 'POST':
            data = request.POST
            if data.get('boton_guardar'):
                form = FacturaForm(data, instance=factura)
                #if form.is_valid():
                message = "Se actualizaron los datos."
                #form.save(commit=False)
                #factura.save()
                
                fecha = form.data['fecha']
                numero = form.data['numero']
                observacion = form.data['observacion']
                
                fac = Factura.objects.get(pk=factura_id)
                user = User.objects.get(pk=data.get('usuario'))
                fac.fecha = datetime.datetime.strptime(fecha, "%d/%m/%Y").date()
                fac.numero = numero
                fac.observacion = observacion
                fac.usuario = user

                if data.get('anulado') == None:
                    fac.anulado = False
                fac.save()    
                #Se loggea la accion del usuario
                id_objeto = factura.id
                codigo_lote = ''
                loggear_accion(request.user, "Actualizar", "Factura", id_objeto, codigo_lote)
                    
            elif data.get('boton_anular'):
                f = Factura.objects.get(pk=factura_id)
                numero_factura = f.numero
                f.anulado = True
                f.save()
                
                #Se loggea la accion del usuario
                id_objeto = factura_id
                codigo_lote = ''
                loggear_accion(request.user, "Anular factura("+numero_factura+")", "Factura", id_objeto, codigo_lote)
                message = "Factura Anulada."
                #return HttpResponseRedirect('/facturacion/listado')
                return HttpResponseRedirect(reverse('frontend_listado_facturas'))
            elif data.get('boton_borrar'):
                f = Factura.objects.get(pk=factura_id)
                numero_factura = f.numero
                f.delete()
                
                #Se loggea la accion del usuario
                id_objeto = factura_id
                codigo_lote = ''
                loggear_accion(request.user, "Borrar factura("+numero_factura+")", "Factura", id_objeto, codigo_lote)
                message = "Factura Borrada."
                #return HttpResponseRedirect('/facturacion/listado')
                return HttpResponseRedirect(reverse('frontend_listado_facturas'))
        else:
            form = FacturaForm(instance=factura)
            grupo= request.user.groups.get().id
    
        c = RequestContext(request, {
            'factura': factura,
            'detalles' : detalles,
            'form': form,
            'grupo': grupo,
            'message': message,
            'numero_timbrado': numero_timbrado
        })
        return HttpResponse(t.render(c))    
    else:
        return HttpResponseRedirect(reverse('login'))
    
    
