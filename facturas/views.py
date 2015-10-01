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

def facturar_pagos(request, pago_id):
    if request.user.is_authenticated():
        if request.method == 'GET':
            
            t = loader.get_template('facturas/facturar_pagos.html')
            pago = PagoDeCuotas.objects.get(pk=pago_id)
            
            ultimo_timbrado = Timbrado.objects.latest('id')
            trfu = TimbradoRangoFacturaUsuario.objects.get(usuario_id=request.user, timbrado_id = ultimo_timbrado.id)
            try: 
                ultimaFactura = Factura.objects.filter(rango_factura_id= trfu.rango_factura.id).latest('id')
                ultimo_numero = ultimaFactura.numero.split("-")
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal)+'-'+unicode(trfu.rango_factura.nro_boca)+'-'+unicode(int(ultimo_numero[2])+1).zfill(7)
            except:
                ultima_factura = unicode(trfu.rango_factura.nro_sucursal)+'-'+unicode(trfu.rango_factura.nro_boca)+'-0000001'
            
            
            
            cuota_desde_num = pago.venta.pagos_realizados - pago.nro_cuotas_a_pagar+1
            cuota_desde = unicode(cuota_desde_num)+"/"+unicode( pago.plan_de_pago.cantidad_de_cuotas)
            cuota_hasta = unicode(cuota_desde_num  + pago.nro_cuotas_a_pagar-1)+"/"+unicode( pago.plan_de_pago.cantidad_de_cuotas)
            c = RequestContext(request, {
                'cliente': pago.cliente,
                'lote': pago.lote.codigo_paralot,
                'cuota_desde': cuota_desde,
                'cuota_hasta': cuota_hasta,
                'ultima_factura': ultima_factura,
                'ultimo_timbrado_numero': trfu.timbrado.numero,
                'ultimo_timbrado_id': ultimo_timbrado.id,

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
            
            #obtener numero de cuotas
            numero_cuota_desde = request.POST.get('nro_cuota_desde','').split("/") 
            numero_cuota_hasta= request.POST.get('nro_cuota_hasta','').split("/")
            num_desde = int(numero_cuota_desde[0])
            num_hasta = int(numero_cuota_hasta[0])
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
            nueva_factura.save()
            venta = Venta.objects.get(cliente_id= nueva_factura.cliente.id, lote_id= lote_id.id)
            object_list= get_pago_cuotas(venta, None, None)
            for x in xrange(0,len(object_list)):
                if num_desde <= int(object_list[x]['nro_cuota']) <= num_hasta:
                    pago = PagoDeCuotas.objects.get(pk=object_list[x]['id'])
                    pago.factura = nueva_factura
                    pago.save() 
            response = HttpResponse(content_type='application/pdf')
            nombre_factura = "factura-" + nueva_factura.numero + ".pdf"
            response['Content-Disposition'] = 'attachment; filename=factura'+str(nueva_factura.id)+'.pdf'
            p = canvas.Canvas(response)
            p.setPageSize((210*mm, 297*mm))
            p.setFont("Helvetica",  7)
            
            # INICIO PRIMERA IMPRESION
            y_1ra_imp = float(14.8)
            p.drawString(4.4*cm, float(y_1ra_imp+11)*cm, unicode(request.POST.get('fecha', '')))
            if nueva_factura.tipo == 'co':
                p.drawString(12.55*cm, float(y_1ra_imp+11)*cm, "X")
            else:
                p.drawString(14.1*cm, float(y_1ra_imp+11)*cm, "X")
            
            p.drawString(16.6*cm, float(y_1ra_imp+11)*cm, unicode(manzana.fraccion.nombre))
            #Solo se imprime el primer nombre y apellido-- Faltaaa
            nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
            p.drawString(5.3*cm, float(y_1ra_imp+10.3)*cm, unicode(nombre_ape))
            p.drawString(16.4*cm, float(y_1ra_imp+10.4)*cm, unicode(manzana.nro_manzana))
            p.drawString(18.7*cm, float(y_1ra_imp+10.4)*cm, unicode(lote_id.nro_lote))
            
            
            if nueva_factura.cliente.ruc == None:
                nueva_factura.cliente.ruc = ""                
            p.drawString(2.3*cm, float(y_1ra_imp+9.7)*cm, unicode(nueva_factura.cliente.ruc))
            p.drawString(16.7*cm, float(y_1ra_imp+9.7)*cm, unicode(nueva_factura.cliente.telefono_laboral))
            
            p.drawString(3*cm, float(y_1ra_imp+9.1)*cm, unicode(nueva_factura.cliente.direccion_cobro))
            p.drawString(13.1*cm, float(y_1ra_imp+9.1)*cm, unicode(lote_id.superficie)+ "  mts2")
            p.drawString(17.6*cm, float(y_1ra_imp+9.1)*cm, unicode(lote_id.cuenta_corriente_catastral))
            
            #Se obtienen la lista de los detalles
            lista_detalles=json.loads(nueva_factura.detalle)
            detalles=[]
            pos_y = float(y_1ra_imp+7.5)
            exentas = 0
            iva10 =0
            iva5 = 0
            total_iva_10 = 0
            total_iva_5 = 0
            total_iva = 0           
            total_gral = 0
            total_venta = 0
            for key, value in lista_detalles.iteritems():
                detalle={}
                detalle['item']=key
                detalle['cantidad']=value['cantidad']
                p.drawString(1.7*cm, float(pos_y - 0.5)*cm, unicode(detalle['cantidad']))
                detalle['concepto']=value['concepto']
                p.drawString(5*cm, float(pos_y - 0.5)*cm, unicode(detalle['concepto']))
                detalle['precio_unitario']=int(value['precio_unitario'])
                p.drawString(11.2*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
                total_venta +=  int(detalle['cantidad']) * int(detalle['precio_unitario'])
                detalle['exentas']=int(value['exentas'])
                p.drawString(13.5*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
                if detalle['exentas'] != '':
                    exentas += int(detalle['exentas'])
                detalle['iva_5']=int(value['iva_5'])
                p.drawString(15.8*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
                if detalle['iva_5'] != '':
                    iva5 += int(detalle['iva_5'])
                detalle['iva_10']=int(value['iva_10'])
                p.drawString(18.6*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
                if detalle['iva_10'] != '':
                    iva10 += int(detalle['iva_10'])
                pos_y -= 0.5
                detalles.append(detalle)
            cantidad =  4 - len(detalles)
            pos_y -= (0.5 * cantidad)
            p.drawString(13.5*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(exentas).replace(",", "."))) 
            p.drawString(15.7*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(iva5).replace(",", ".")))   
            p.drawString(18*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(iva10).replace(",", ".")))
            pos_y -= 0.5
            p.drawString(18*cm, float(y_1ra_imp+3.2)*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            pos_y -= 1
            numalet= num2words(int(total_venta), lang='es')
            p.drawString(6.5*cm, float(pos_y - 1.5)*cm, unicode(numalet))
            p.drawString(18*cm, float(pos_y - 1.5)*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            total_iva_10 = int(iva10/11)
            total_iva_5 = int(iva5/21)
            total_iva = total_iva_10 + total_iva_5
            pos_y -= 0.5
            p.drawString(5.2*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_5).replace(",", ".")))
            p.drawString(8.5*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_10).replace(",", ".")))
            p.drawString(13*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva).replace(",", ".")))
            # FIN PRIMERA IMPRESION
            ######################################################################################################################################
            # INICIO SEGUNDA IMPRESION
            p.drawString(4.4*cm, 12.1*cm, unicode(request.POST.get('fecha', '')))
            if nueva_factura.tipo == 'co':
                p.drawString(12.55*cm, 12.1*cm, "X")
            else:
                p.drawString(14.1*cm, 12.1*cm, "X")
            
            p.drawString(16.6*cm, 12.1*cm, unicode(manzana.fraccion.nombre))
            #Solo se imprime el primer nombre y apellido-- Faltaaa
            nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
            p.drawString(5.3*cm, 11.5*cm, unicode(nombre_ape))
            p.drawString(16.4*cm, 11.5*cm, unicode(manzana.nro_manzana))
            p.drawString(18.7*cm, 11.5*cm, unicode(lote_id.nro_lote))
            if nueva_factura.cliente.ruc == None:
                nueva_factura.cliente.ruc = ""                
            p.drawString(2.3*cm, 10.8*cm, unicode(nueva_factura.cliente.ruc))
            p.drawString(16.7*cm, 10.8*cm, unicode(nueva_factura.cliente.telefono_laboral))
            
            p.drawString(3*cm, 10.2*cm, unicode(nueva_factura.cliente.direccion_cobro))
            p.drawString(13.1*cm, 10.2*cm, unicode(lote_id.superficie)+ "  mts2")
            p.drawString(17.6*cm, 10.2*cm, unicode(lote_id.cuenta_corriente_catastral))
            
            #Se obtienen la lista de los detalles
            lista_detalles=json.loads(nueva_factura.detalle)
            detalles=[]
            pos_y = float(8.6)
            exentas = 0
            iva10 =0
            iva5 = 0
            total_iva_10 = 0
            total_iva_5 = 0
            total_iva = 0           
            total_gral = 0
            total_venta = 0
            for key, value in lista_detalles.iteritems():
                detalle={}
                detalle['item']=key
                detalle['cantidad']=value['cantidad']
                p.drawString(1.7*cm, float(pos_y - 0.5)*cm, unicode(detalle['cantidad']))
                detalle['concepto']=value['concepto']
                p.drawString(5*cm, float(pos_y - 0.5)*cm, unicode(detalle['concepto']))
                detalle['precio_unitario']=int(value['precio_unitario'])
                p.drawString(11.2*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
                total_venta +=  int(detalle['cantidad']) * int(detalle['precio_unitario'])
                detalle['exentas']=int(value['exentas'])
                p.drawString(13.5*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
                if detalle['exentas'] != '':
                    exentas += int(detalle['exentas'])
                detalle['iva_5']=int(value['iva_5'])
                p.drawString(15.8*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
                if detalle['iva_5'] != '':
                    iva5 += int(detalle['iva_5'])
                detalle['iva_10']=int(value['iva_10'])
                p.drawString(18.6*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
                if detalle['iva_10'] != '':
                    iva10 += int(detalle['iva_10'])
                pos_y -= 0.5
                detalles.append(detalle)
            cantidad =  4 - len(detalles)
            pos_y -= (0.5 * cantidad)
            p.drawString(13.5*cm, 4.8*cm, unicode('{:,}'.format(exentas).replace(",", "."))) 
            p.drawString(15.7*cm, 4.8*cm, unicode('{:,}'.format(iva5).replace(",", ".")))   
            p.drawString(18*cm, 4.8*cm, unicode('{:,}'.format(iva10).replace(",", ".")))
            pos_y -= 0.5
            p.drawString(18*cm, 4.2*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            pos_y -= 1
            numalet= num2words(int(total_venta), lang='es')
            p.drawString(6.5*cm, float(pos_y - 1.5)*cm, unicode(numalet))
            p.drawString(18*cm, float(pos_y - 1.5)*cm, unicode('{:,}'.format(total_venta).replace(",", "."))) 
            total_iva_10 = int(iva10/11)
            total_iva_5 = int(iva5/21)
            total_iva = total_iva_10 + total_iva_5
            pos_y -= 0.5
            p.drawString(5.2*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_5).replace(",", ".")))
            p.drawString(8.5*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_10).replace(",", ".")))
            p.drawString(13*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva).replace(",", ".")))
            # FIN SEGUNDA IMPRESION
            
            p.showPage()
            p.save()             
            return response;
    else:
        return HttpResponseRedirect(reverse('login')) 

# Funcion principal del modulo de facturas.
def facturar(request):    
    if request.user.is_authenticated():
        if request.method == 'GET':
            #Mostrar el formulario basico de factura.            
            t = loader.get_template('facturas/facturar.html')
            
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
            
            #obtener numero de cuotas
            numero_cuota_desde = request.POST.get('nro_cuota_desde','').split("/") 
            numero_cuota_hasta= request.POST.get('nro_cuota_hasta','').split("/")
            num_desde = int(numero_cuota_desde[0])
            num_hasta = int(numero_cuota_hasta[0])
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
            nueva_factura.save()
            venta = Venta.objects.get(cliente_id= nueva_factura.cliente.id, lote_id= lote_id.id)
            object_list= get_pago_cuotas(venta, None, None)
            for x in xrange(0,len(object_list)):
                if num_desde <= int(object_list[x]['nro_cuota']) <= num_hasta:
                    pago = PagoDeCuotas.objects.get(pk=object_list[x]['id'])
                    pago.factura = nueva_factura
                    pago.save() 
            response = HttpResponse(content_type='application/pdf')
            nombre_factura = "factura-" + nueva_factura.numero + ".pdf"
            response['Content-Disposition'] = 'attachment; filename=factura'+str(nueva_factura.id)+'.pdf'
            p = canvas.Canvas(response)
            p.setPageSize((210*mm, 297*mm))
            p.setFont("Helvetica",  7)
            
            # INICIO PRIMERA IMPRESION
            y_1ra_imp = float(14.8)
            p.drawString(4.4*cm, float(y_1ra_imp+11)*cm, unicode(request.POST.get('fecha', '')))
            if nueva_factura.tipo == 'co':
                p.drawString(12.55*cm, float(y_1ra_imp+11)*cm, "X")
            else:
                p.drawString(14.1*cm, float(y_1ra_imp+11)*cm, "X")
            
            p.drawString(16.6*cm, float(y_1ra_imp+11)*cm, unicode(manzana.fraccion.nombre))
            #Solo se imprime el primer nombre y apellido-- Faltaaa
            nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
            p.drawString(5.3*cm, float(y_1ra_imp+10.3)*cm, unicode(nombre_ape))
            p.drawString(16.4*cm, float(y_1ra_imp+10.4)*cm, unicode(manzana.nro_manzana))
            p.drawString(18.7*cm, float(y_1ra_imp+10.4)*cm, unicode(lote_id.nro_lote))
            
            
            if nueva_factura.cliente.ruc == None:
                nueva_factura.cliente.ruc = ""                
            p.drawString(2.3*cm, float(y_1ra_imp+9.7)*cm, unicode(nueva_factura.cliente.ruc))
            p.drawString(16.7*cm, float(y_1ra_imp+9.7)*cm, unicode(nueva_factura.cliente.telefono_laboral))
            
            p.drawString(3*cm, float(y_1ra_imp+9.1)*cm, unicode(nueva_factura.cliente.direccion_cobro))
            p.drawString(13.1*cm, float(y_1ra_imp+9.1)*cm, unicode(lote_id.superficie)+ "  mts2")
            p.drawString(17.6*cm, float(y_1ra_imp+9.1)*cm, unicode(lote_id.cuenta_corriente_catastral))
            
            #Se obtienen la lista de los detalles
            lista_detalles=json.loads(nueva_factura.detalle)
            detalles=[]
            pos_y = float(y_1ra_imp+7.5)
            exentas = 0
            iva10 =0
            iva5 = 0
            total_iva_10 = 0
            total_iva_5 = 0
            total_iva = 0           
            total_gral = 0
            total_venta = 0
            for key, value in lista_detalles.iteritems():
                detalle={}
                detalle['item']=key
                detalle['cantidad']=value['cantidad']
                p.drawString(1.7*cm, float(pos_y - 0.5)*cm, unicode(detalle['cantidad']))
                detalle['concepto']=value['concepto']
                p.drawString(5*cm, float(pos_y - 0.5)*cm, unicode(detalle['concepto']))
                detalle['precio_unitario']=int(value['precio_unitario'])
                p.drawString(11.2*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
                total_venta +=  int(detalle['cantidad']) * int(detalle['precio_unitario'])
                detalle['exentas']=int(value['exentas'])
                p.drawString(13.5*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
                if detalle['exentas'] != '':
                    exentas += int(detalle['exentas'])
                detalle['iva_5']=int(value['iva_5'])
                p.drawString(15.8*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
                if detalle['iva_5'] != '':
                    iva5 += int(detalle['iva_5'])
                detalle['iva_10']=int(value['iva_10'])
                p.drawString(18.6*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
                if detalle['iva_10'] != '':
                    iva10 += int(detalle['iva_10'])
                pos_y -= 0.5
                detalles.append(detalle)
            cantidad =  4 - len(detalles)
            pos_y -= (0.5 * cantidad)
            p.drawString(13.5*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(exentas).replace(",", "."))) 
            p.drawString(15.7*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(iva5).replace(",", ".")))   
            p.drawString(18*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(iva10).replace(",", ".")))
            pos_y -= 0.5
            p.drawString(18*cm, float(y_1ra_imp+3.2)*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            pos_y -= 1
            numalet= num2words(int(total_venta), lang='es')
            p.drawString(6.5*cm, float(pos_y - 1.5)*cm, unicode(numalet))
            p.drawString(18*cm, float(pos_y - 1.5)*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            total_iva_10 = int(iva10/11)
            total_iva_5 = int(iva5/21)
            total_iva = total_iva_10 + total_iva_5
            pos_y -= 0.5
            p.drawString(5.2*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_5).replace(",", ".")))
            p.drawString(8.5*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_10).replace(",", ".")))
            p.drawString(13*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva).replace(",", ".")))
            # FIN PRIMERA IMPRESION
            ######################################################################################################################################
            # INICIO SEGUNDA IMPRESION
            p.drawString(4.4*cm, 12.1*cm, unicode(request.POST.get('fecha', '')))
            if nueva_factura.tipo == 'co':
                p.drawString(12.55*cm, 12.1*cm, "X")
            else:
                p.drawString(14.1*cm, 12.1*cm, "X")
            
            p.drawString(16.6*cm, 12.1*cm, unicode(manzana.fraccion.nombre))
            #Solo se imprime el primer nombre y apellido-- Faltaaa
            nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
            p.drawString(5.3*cm, 11.5*cm, unicode(nombre_ape))
            p.drawString(16.4*cm, 11.5*cm, unicode(manzana.nro_manzana))
            p.drawString(18.7*cm, 11.5*cm, unicode(lote_id.nro_lote))
            if nueva_factura.cliente.ruc == None:
                nueva_factura.cliente.ruc = ""                
            p.drawString(2.3*cm, 10.8*cm, unicode(nueva_factura.cliente.ruc))
            p.drawString(16.7*cm, 10.8*cm, unicode(nueva_factura.cliente.telefono_laboral))
            
            p.drawString(3*cm, 10.2*cm, unicode(nueva_factura.cliente.direccion_cobro))
            p.drawString(13.1*cm, 10.2*cm, unicode(lote_id.superficie)+ "  mts2")
            p.drawString(17.6*cm, 10.2*cm, unicode(lote_id.cuenta_corriente_catastral))
            
            #Se obtienen la lista de los detalles
            lista_detalles=json.loads(nueva_factura.detalle)
            detalles=[]
            pos_y = float(8.6)
            exentas = 0
            iva10 =0
            iva5 = 0
            total_iva_10 = 0
            total_iva_5 = 0
            total_iva = 0           
            total_gral = 0
            total_venta = 0
            for key, value in lista_detalles.iteritems():
                detalle={}
                detalle['item']=key
                detalle['cantidad']=value['cantidad']
                p.drawString(1.7*cm, float(pos_y - 0.5)*cm, unicode(detalle['cantidad']))
                detalle['concepto']=value['concepto']
                p.drawString(5*cm, float(pos_y - 0.5)*cm, unicode(detalle['concepto']))
                detalle['precio_unitario']=int(value['precio_unitario'])
                p.drawString(11.2*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
                total_venta +=  int(detalle['cantidad']) * int(detalle['precio_unitario'])
                detalle['exentas']=int(value['exentas'])
                p.drawString(13.5*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
                if detalle['exentas'] != '':
                    exentas += int(detalle['exentas'])
                detalle['iva_5']=int(value['iva_5'])
                p.drawString(15.8*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
                if detalle['iva_5'] != '':
                    iva5 += int(detalle['iva_5'])
                detalle['iva_10']=int(value['iva_10'])
                p.drawString(18.6*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
                if detalle['iva_10'] != '':
                    iva10 += int(detalle['iva_10'])
                pos_y -= 0.5
                detalles.append(detalle)
            cantidad =  4 - len(detalles)
            pos_y -= (0.5 * cantidad)
            p.drawString(13.5*cm, 4.8*cm, unicode('{:,}'.format(exentas).replace(",", "."))) 
            p.drawString(15.7*cm, 4.8*cm, unicode('{:,}'.format(iva5).replace(",", ".")))   
            p.drawString(18*cm, 4.8*cm, unicode('{:,}'.format(iva10).replace(",", ".")))
            pos_y -= 0.5
            p.drawString(18*cm, 4.2*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            pos_y -= 1
            numalet= num2words(int(total_venta), lang='es')
            p.drawString(6.5*cm, float(pos_y - 1.5)*cm, unicode(numalet))
            p.drawString(18*cm, float(pos_y - 1.5)*cm, unicode('{:,}'.format(total_venta).replace(",", "."))) 
            total_iva_10 = int(iva10/11)
            total_iva_5 = int(iva5/21)
            total_iva = total_iva_10 + total_iva_5
            pos_y -= 0.5
            p.drawString(5.2*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_5).replace(",", ".")))
            p.drawString(8.5*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_10).replace(",", ".")))
            p.drawString(13*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva).replace(",", ".")))
            # FIN SEGUNDA IMPRESION
            
            p.showPage()
            p.save()          
            return response;
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    
# Funcion para consultar el listado de todas las facturas.
def consultar_facturas(request):
    if request.user.is_authenticated():
        if request.method == 'GET':
            #Mostrar la lista de todas las facturas.  
            object_list = Factura.objects.all().order_by('id','-fecha')
            monto=0
            for factura in object_list:
                lista_detalles=json.loads(factura.detalle)
                for key, value in lista_detalles.iteritems():
                    monto+=int(int(value['cantidad'])*int(value['precio_unitario'])) 
                factura.monto=unicode('{:,}'.format(monto)).replace(",", ".") 
        else: #POST se envia el formulario con los parametros de busqueda.  
            data = request.POST     
            # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
            fecha_ini = data.get('fecha_ini', '')
            fecha_fin = data.get('fecha_fin', '')
            fecha_ini_parsed = unicode(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
            fecha_fin_parsed = unicode(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
            object_list = Factura.objects.filter(fecha__range=(fecha_ini_parsed,fecha_fin_parsed)).order_by('id','fecha')                    
            monto=0
            for factura in object_list:
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
        trfu = TimbradoRangoFacturaUsuario.objects.get(rango_factura_id= factura.rango_factura.id)
        numero_timbrado = trfu.timbrado.numero 
        lista_detalles=json.loads(factura.detalle)
        detalles=[]
        for key, value in lista_detalles.iteritems():
            detalle={}
            #detalle['precio_unitario']=unicode('{:,}'.format(value['precio_unitario']))
            detalle['item']=key
            detalle['cantidad']=value['cantidad']
            detalle['concepto']=value['concepto']
            detalle['precio_unitario']=value['precio_unitario']
            detalle['iva_10']=value['iva_10']
            detalle['iva_5']=value['iva_5']
            detalle['exentas']=value['exentas']
            detalles.append(detalle)
        if factura.tipo=='co':
            tipo='Contado'
        else:
            tipo='Credito'
        factura.tipo=tipo
        message = ''
            
        if request.method == 'POST':
            data = request.POST
            if data.get('boton_guardar'):
                form = FacturaForm(data, instance=factura)
                if form.is_valid():
                    message = "Se actualizaron los datos."
                    form.save(commit=False)
                    factura.save()
            elif data.get('boton_borrar'):
                c = Factura.objects.get(pk=factura_id)
                c.delete()
                return HttpResponseRedirect('/facturacion/listado')
        else:
            form = FacturaForm(instance=factura)
    
        c = RequestContext(request, {
            'factura': factura,
            'detalles' : detalles,
            'form': form,
            'message': message,
            'numero_timbrado': numero_timbrado
        })
        return HttpResponse(t.render(c))    
    else:
        return HttpResponseRedirect(reverse('login'))