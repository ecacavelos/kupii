# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Propietario, Fraccion, Lote, Manzana, PagoDeCuotas, Venta, Reserva, CambioDeLotes, RecuperacionDeLotes, TransferenciaDeLotes,Factura, Cliente,Timbrado
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
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import cm
from num2words import num2words
import xlwt
import math
import json

# Funcion principal del modulo de facturas.
def facturar(request):    
    if request.user.is_authenticated():
        if request.method == 'GET':
            #Mostrar el formulario basico de factura.            
            t = loader.get_template('facturas/facturar.html')
            c = RequestContext(request, {})
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
            timbrado_id = request.POST.get('id-timbrado','')
            
            #Obtener el NUMERO
            numero = request.POST.get('nro-factura','')
            
            #Obtener fecha
            fecha = datetime.strptime(request.POST.get('fecha', ''), "%Y-%m-%d")
            
            #Obtener Tipo (Contado - Crédito)
            tipo = request.POST.get('tipo','')
            
            #Obtener el detalle
            detalle = request.POST.get('detalle','')
            
            #Crear un objeto Factura y guardar            
            nueva_factura = Factura()
            nueva_factura.fecha = fecha
            nueva_factura.timbrado = Timbrado.objects.get(pk=timbrado_id)
            nueva_factura.numero = numero
            nueva_factura.cliente = Cliente.objects.get(pk=cliente_id)
            nueva_factura.tipo = tipo
            nueva_factura.detalle = detalle
            nueva_factura.lote = lote_id 
            nueva_factura.save()
            
            response = HttpResponse(mimetype='application/pdf')
            nombre_factura = "factura-" + nueva_factura.numero + ".pdf"
            response['Content-Disposition'] = 'attachment; filename=factura.pdf'
            p = canvas.Canvas(response)
            p.setPageSize((19*cm, 14*cm))
            p.setFont("Helvetica",  10)
            p.drawString(2*cm, 10.3*cm, unicode(nueva_factura.fecha.strftime("%Y-%m-%d")))
            if nueva_factura.tipo == 'co':
                p.drawString(11*cm, 10.3*cm, "X")
            else:
                p.drawString(13.2*cm, 10.3*cm, "X")
            
            p.drawString(15*cm, 10.3*cm, unicode(manzana.fraccion.nombre))
            #Solo se imprime el primer nombre y apellido-- Faltaaa
            nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
            p.drawString(4*cm, 9.3*cm, unicode(nombre_ape))
            p.drawString(12*cm, 9.3*cm, unicode(manzana.nro_manzana))
            p.drawString(15.5*cm, 9.3*cm, unicode(lote_id.nro_lote))
            if nueva_factura.cliente.ruc == None:
                nueva_factura.cliente.ruc = ""                
            p.drawString(2*cm, 8.3*cm, unicode(nueva_factura.cliente.ruc))
            #Se obtienen la lista de los detalles
            lista_detalles=json.loads(nueva_factura.detalle)
            detalles=[]
            pos_y = float(7)
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
                p.drawString(1.5*cm, float(pos_y - 0.5)*cm, unicode(detalle['cantidad']))
                detalle['concepto']=value['concepto']
                p.drawString(2*cm, float(pos_y - 0.5)*cm, unicode(detalle['concepto']))
                detalle['precio_unitario']=value['precio_unitario']
                p.drawString(8*cm, float(pos_y - 0.5)*cm, unicode(detalle['precio_unitario']))
                total_venta +=  int(detalle['cantidad']) * int(detalle['precio_unitario'])
                detalle['exentas']=value['exentas']
                p.drawString(10.5*cm, float(pos_y - 0.5)*cm, unicode(detalle['exentas']))
                if detalle['exentas'] != '':
                    exentas += int(detalle['exentas'])
                detalle['iva_5']=value['iva_5']
                p.drawString(12*cm, float(pos_y - 0.5)*cm, unicode(detalle['iva_5']))
                if detalle['iva_5'] != '':
                    iva5 += int(detalle['iva_5'])
                detalle['iva_10']=value['iva_10']
                p.drawString(14*cm, float(pos_y - 0.5)*cm, unicode(detalle['iva_10']))
                if detalle['iva_10'] != '':
                    iva10 += int(detalle['iva_10'])
                pos_y -= 0.5
                detalles.append(detalle)
            cantidad =  4 - len(detalles)
            pos_y -= (0.5 * cantidad)
            p.drawString(10.5*cm, pos_y*cm, unicode(exentas)) 
            p.drawString(12*cm, pos_y*cm, unicode(iva5))   
            p.drawString(14*cm, pos_y*cm, unicode(iva10))
            pos_y -= 0.5
            p.drawString(14*cm, float(pos_y - 0.5)*cm, unicode(total_venta))
            pos_y -= 1
            p.drawString(14*cm, float(pos_y - 0.5)*cm, unicode(total_venta))
            numalet= num2words(int(total_venta), lang='es')
            p.drawString(6*cm, float(pos_y - 0.5)*cm, unicode(numalet))
            total_iva_10 = int(iva10/11)
            total_iva_5 = int(iva5/21)
            total_iva = total_iva_10 + total_iva_5
            pos_y -= 0.5
            p.drawString(5*cm, float(pos_y - 0.5)*cm, unicode(total_iva_5))
            p.drawString(6.2*cm, float(pos_y - 0.5)*cm, unicode(total_iva_10))
            p.drawString(11.5*cm, float(pos_y - 0.5)*cm, unicode(total_iva))
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
        })
        return HttpResponse(t.render(c))    
    else:
        return HttpResponseRedirect(reverse('login'))