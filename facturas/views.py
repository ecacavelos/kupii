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
import ast

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
            
            if tipo_operacion == '1': # PAGO DE CUOTA
                pago = PagoDeCuotas.objects.get(pk=operacion_id)
                cantidad_pagos_anteriores = obtener_cantidad_cuotas_pagadas(pago)
                cuota_desde_num = cantidad_pagos_anteriores - pago.nro_cuotas_a_pagar+1
                #cuota_desde_num = pago.venta.pagos_realizados - pago.nro_cuotas_a_pagar+1
                cuota_desde = unicode(cuota_desde_num)+"/"+unicode( pago.plan_de_pago.cantidad_de_cuotas)
                cuota_hasta = unicode(cuota_desde_num  + pago.nro_cuotas_a_pagar-1)+"/"+unicode( pago.plan_de_pago.cantidad_de_cuotas)
                
            if tipo_operacion == '2': # VENTA
                venta = Venta.objects.get(pk=operacion_id)
                tipo_venta = "Contado"
                precio_venta = venta.precio_final_de_venta
                entrega_inicial = venta.entrega_inicial
                descripcion = "Venta al Contado de Lote: "+venta.lote.codigo_paralot
            
            ultimo_timbrado = Timbrado.objects.latest('id')
            trfu = TimbradoRangoFacturaUsuario.objects.get(usuario_id=request.user, timbrado_id = ultimo_timbrado.id)
            try: 
                ultimaFactura = Factura.objects.filter(rango_factura_id= trfu.rango_factura.id).latest('id')
                ultimo_numero = ultimaFactura.numero.split("-")
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal)+'-'+unicode(trfu.rango_factura.nro_boca)+'-'+unicode(int(ultimo_numero[2])+1).zfill(7)
            except:
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal)+'-'+unicode(trfu.rango_factura.nro_boca)+'-0000001'
            
            
            
            if tipo_operacion == '1': # PAGO DE CUOTA
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

                })
            if tipo_operacion == '2': # VENTA
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
            #nueva_factura.lote = lote_id
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

def facturar_pagos(request):
        if request.user.is_authenticated():
            if request.method == 'GET':
                params = request.GET

                pagos_id = params.getlist('pagos_id')
                t = loader.get_template('facturas/facturar_pagos.html')

                # determinamos el grupo al cual pertenece el user en cuestion
                grupo = request.user.groups.get().id
                # retornamos todos los users para que pueda seleccionar
                users = User.objects.all()

                cuota_desde = ''
                cuota_hasta = ''

                tipo_venta = ''
                precio_venta = ''

                factura = {}
                pagos_factura = []
                detalles = []

                for pago_id in pagos_id:
                    pago_factura = {}
                    pago = PagoDeCuotas.objects.get(pk=pago_id)
                    factura['cliente'] = pago.cliente
                    pago_factura['lote'] = pago.lote.codigo_paralot
                    cantidad_pagos_anteriores = obtener_cantidad_cuotas_pagadas(pago)
                    cuota_desde_num = cantidad_pagos_anteriores - pago.nro_cuotas_a_pagar + 1
                    # cuota_desde_num = pago.venta.pagos_realizados - pago.nro_cuotas_a_pagar+1
                    cuota_desde = unicode(cuota_desde_num) + "/" + unicode(pago.plan_de_pago.cantidad_de_cuotas)
                    pago_factura['cuota_desde'] = cuota_desde
                    cuota_hasta = unicode(cuota_desde_num + pago.nro_cuotas_a_pagar - 1) + "/" + unicode(
                        pago.plan_de_pago.cantidad_de_cuotas)
                    pago_factura['cuota_hasta'] = cuota_hasta
                    ultimo_timbrado = Timbrado.objects.latest('id')
                    factura['ultimo_timbrado'] = ultimo_timbrado
                    trfu = TimbradoRangoFacturaUsuario.objects.get(usuario_id=request.user, timbrado_id=ultimo_timbrado.id)
                    try:
                        ultimaFactura = Factura.objects.filter(rango_factura_id=trfu.rango_factura.id).latest('id')
                        ultimo_numero = ultimaFactura.numero.split("-")
                        ultima_factura = unicode(trfu.rango_factura.nro_sucursal) + '-' + unicode(
                            trfu.rango_factura.nro_boca) + '-' + unicode(int(ultimo_numero[2]) + 1).zfill(7)
                        factura['ultima_factura'] = ultima_factura
                    except:
                        ultima_factura = unicode(trfu.rango_factura.nro_sucursal) + '-' + unicode(
                            trfu.rango_factura.nro_boca) + '-0000001'
                        factura['ultima_factura'] = ultima_factura
                    factura['ultimo_timbrado_numero'] = trfu.timbrado.numero
                    pagos_factura.append(pago_factura)

                    detalles_lote = get_detalles_factura(pago.lote.codigo_paralot, pago.cliente.id, cuota_desde, cuota_hasta)
                    for detalle_lote in detalles_lote:
                        detalle = {}
                        detalle['cantidad'] = detalle_lote['cantidad']
                        try:
                            detalle['iva10'] = detalle_lote['iva10']
                            print "interes o gestion cobranza"
                        except:
                            concepto = "Pago de Cuota: "+ cuota_desde +"de "+ detalle_lote['cuotas_detalles'][0]['fecha'] +", al "+cuota_hasta+ "de "+detalle_lote['cuotas_detalles'][-1]['fecha']+". Lote: " + pago.lote.codigo_paralot
                            detalle['concepto'] = concepto
                            print "cuotas"


                        detalle['precio_unitario'] = detalle_lote['precio_unitario']
                        detalle['exentas'] = detalle_lote['exentas']
                        detalle['iva5'] = detalle_lote['iva5']
                        detalles.append(detalle)


                factura['pagos'] = pagos_factura
                factura['detalles'] = detalles
                c = RequestContext(request, {
                    'tipo_venta': tipo_venta,
                    'precio_venta': precio_venta,
                    'grupo': grupo,
                    'users': users,
                    'factura': factura
                })

                return HttpResponse(t.render(c))

            else:  # POST se envia el formulario.
                print 'POST'
                # Obtener el cliente
                cliente_id = request.POST.get('cliente', '')

                # Obtener el Lote
                lotes_id = request.POST.get('lote', '')
                #ver bien esto
                for lote_id in lotes_id:
                    x = unicode(lote_id)
                    fraccion_int = int(x[0:3])
                    manzana_int = int(x[4:7])
                    lote_int = int(x[8:])
                    manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
                    lote_id = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)

                # Obtener el TIMBRADO
                timbrado_id = request.POST.get('id_timbrado', '')

                # Obtener el NUMERO
                numero = request.POST.get('nro_factura', '')

                # Obtener fecha
                # fecha = datetime.datetime.strptime(request.POST.get('fecha', ''), "%Y-%m-%d")
                fecha = datetime.datetime.strptime(request.POST.get('fecha', ''), "%d/%m/%Y")

                # Obtener Tipo (Contado - Crédito)
                tipo = request.POST.get('tipo', '')

                # Obtener el detalle
                detalle = request.POST.get('detalle', '')

                # Obtener observacion
                observacion = request.POST.get('observacion', '')

                # Crear un objeto Factura y guardar
                nueva_factura = Factura()
                nueva_factura.fecha = fecha
                # nueva_factura.timbrado = Timbrado.objects.get(pk=timbrado_id)
                trfu = TimbradoRangoFacturaUsuario.objects.get(timbrado_id=timbrado_id, usuario_id=request.user)
                nueva_factura.rango_factura = trfu.rango_factura
                nueva_factura.numero = numero
                nueva_factura.cliente = Cliente.objects.get(pk=cliente_id)
                nueva_factura.tipo = tipo
                nueva_factura.detalle = detalle
                #ver este caso
                #nueva_factura.lote = lote_id
                nueva_factura.anulado = False
                nueva_factura.observacion = observacion
                nueva_factura.usuario = request.user
                nueva_factura.save()

                # Se loggea la accion del usuario
                id_objeto = nueva_factura.id
                codigo_lote = request.POST.get('lote', '')
                loggear_accion(request.user, "Agregar", "Factura", id_objeto, codigo_lote)

                # obtener numero de cuotas
                #ver este caso
                numero_cuota_desde = request.POST.get('nro_cuota_desde', '')
                numero_cuota_hasta = request.POST.get('nro_cuota_hasta', '')
                if numero_cuota_desde != '' and numero_cuota_hasta != '':
                    numero_cuota_desde = request.POST.get('nro_cuota_desde', '').split("/")
                    numero_cuota_hasta = request.POST.get('nro_cuota_hasta', '').split("/")
                    num_desde = int(numero_cuota_desde[0])
                    num_hasta = int(numero_cuota_hasta[0])

                    #ver este caso
                    venta = Venta.objects.get(cliente_id=nueva_factura.cliente.id, lote_id=lote_id.id)
                    object_list = get_pago_cuotas(venta, None, None)
                    for x in xrange(0, len(object_list)):
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

            ultimo_timbrado = Timbrado.objects.latest('id')
            trfu = TimbradoRangoFacturaUsuario.objects.get(usuario_id=request.user, timbrado_id = ultimo_timbrado.id)
            try: 
                ultimaFactura = Factura.objects.filter(rango_factura_id= trfu.rango_factura.id).latest('id')
                ultimo_numero = ultimaFactura.numero.split("-")
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal)+'-'+unicode(trfu.rango_factura.nro_boca)+'-'+unicode(int(ultimo_numero[2])+1).zfill(7)
            except:
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal)+'-'+unicode(trfu.rango_factura.nro_boca)+'-0000001'
            
            c = RequestContext(request, {
                'ultima_factura': ultima_factura,
                'ultimo_timbrado_numero': trfu.timbrado.numero,
                'ultimo_timbrado_id': ultimo_timbrado.id,
                'grupo': grupo,
                'users': users
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
            #nueva_factura.lote = lote_id
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
            #Mostrar la lista de todas las facturas.  
            object_list = Factura.objects.all().order_by('-id','-fecha')
            for factura in object_list:
                monto=0
                lista_detalles=json.loads(factura.detalle)
                for key, value in lista_detalles.iteritems():
                    if value['cantidad'] == "" or value['precio_unitario'] == "":
                        print ('Encontramos detalle invalido')
                        monto+=0
                    else:
                        monto+=int(int(value['cantidad'])*int(value['precio_unitario']))
                factura.monto=unicode('{:,}'.format(monto)).replace(",", ".") 
        else: #POST se envia el formulario con los parametros de busqueda.  
            data = request.POST     
            # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
            tipo_busqueda = data.get('tipo_busqueda')
            busqueda = data.get('busqueda')
            if tipo_busqueda == 'rango_fecha':
                fecha_ini = data.get('fecha_ini', '')
                fecha_fin = data.get('fecha_fin', '')
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
        
        paginator=Paginator(object_list,15)
        page=request.GET.get('page')
        try:
            lista=paginator.page(page)
        except PageNotAnInteger:
            lista=paginator.page(1)
        except EmptyPage:
            lista=paginator.page(paginator.num_pages)
    
        t = loader.get_template('facturas/listado.html')
        c = RequestContext(request, {
            'object_list': lista,
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
                
                #fecha = form.data['fecha']
                numero = data['numero']
                observacion = data['observacion']
                
                fac = Factura.objects.get(pk=factura_id)
                #fac.fecha = fecha
                fac.numero = numero
                fac.observacion = observacion
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

def get_detalles_factura(codigo, cliente_id, nro_cuota_desde, nro_cuota_hasta):
    try:
        nro_cuota_desde = nro_cuota_desde.split("/")
        nro_cuota_hasta = nro_cuota_hasta.split("/")
        num_desde = int(nro_cuota_desde[0])
        num_hasta = int(nro_cuota_hasta[0])
        lote = Lote.objects.get(codigo_paralot=codigo)

        cuotas_pag = ((num_hasta - num_desde) + 1)
        cuotas_detalles = get_cuota_information_by_lote(lote.id, cuotas_pag, True)

        cliente = Cliente.objects.get(pk=cliente_id)
        venta = Venta.objects.get(lote_id=lote.id, cliente_id=cliente.id)
        object_list = get_pago_cuotas(venta, None, None)
        # object_list = sorted(object_list, key=lambda k: k['id'])
        gestion_cobranza = []
        interes_moratorio = 0
        suma_gestion = 0
        detalles = []
        detalle = {}
        ok = False
        cantidad = num_hasta - (num_desde - 1)
        detalle['cantidad'] = cantidad
        detalle['precio_unitario'] = venta.precio_de_cuota

        detalle['iva5'] = int(((cantidad * venta.precio_de_cuota) * 31.5) / 101.5)

        detalle['exentas'] = int((cantidad * venta.precio_de_cuota) - detalle['iva5'])

        detalle['cuotas_detalles'] = cuotas_detalles

        detalles.append(detalle)
        '''
            Se trae los pagos que se van a facturar y se iteran para traer el interes de cada cuota.
            Tambien se acumula la gestion de cobranza que hay en las cuotas
        '''
        cantidad = 0
        gestion_procesada = False
        ultimo_pago = object_list[0]['id']
        for x in xrange(num_desde - 1, num_hasta):
            pago = PagoDeCuotas.objects.get(id=object_list[x]['id'])
            if pago.id != ultimo_pago:
                ultimo_pago = pago.id
                gestion_procesada = False
                cantidad = 0
            if pago.detalle != None:
                detalle = ast.literal_eval(pago.detalle)
                for y in xrange(0, len(detalle)):
                    try:
                        interes_moratorio += int(detalle['item' + str(cantidad)]['intereses'])
                        if detalle['item' + str(cantidad)]['nro_cuota'] == (x + 1):
                            if gestion_procesada == False and ultimo_pago == pago.id:
                                try:
                                    suma_gestion += detalle['item' + str(len(detalle) - 1)]['gestion_cobranza']
                                    gestion_procesada = True
                                except Exception, error:
                                    print "No tiene gestion de cobranza"
                            cantidad += 1
                            break
                    except Exception, error:
                        print error

        if interes_moratorio != 0:
            detalle = {}
            detalle['cantidad'] = 1
            detalle['precio_unitario'] = interes_moratorio
            detalle['exentas'] = 0
            detalle['iva5'] = 0
            detalle['iva10'] = interes_moratorio
            detalles.append(detalle)

        if suma_gestion != 0:
            detalle = {}
            detalle['cantidad'] = 1
            detalle['precio_unitario'] = suma_gestion
            detalle['exentas'] = 0
            detalle['iva5'] = 0
            detalle['iva10'] = suma_gestion
            detalles.append(detalle)
        return detalles
    except Exception, error:
        print error