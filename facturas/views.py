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
from django.utils import simplejson
from django.db import connection
from facturas.forms import FacturaForm
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
            nueva_factura.save()
            
            t = loader.get_template('facturas/facturar.html')
            c = RequestContext(request, {})
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    
# Funcion para consultar el listado de todas las facturas.
def consultar_facturas(request):
    if request.user.is_authenticated():
        if request.method == 'GET':
            #Mostrar el formulario basico de factura.  
            object_list = Factura.objects.all().order_by('id','-fecha')
            monto=0
#             for factura in object_list:
#                 lista_detalles=json.loads(factura.detalle)
#                 for key, value in lista_detalles.iteritems():
#                     monto+=int(value['cantidad'])*int(value['precio_unitario'])
#                 factura.monto=monto
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else: #POST se envia el formulario.  
            data = request.POST     
            #object_list = Factura.objects.all().order_by('id')
            # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
            fecha_ini = data.get('fecha_ini', '')
            fecha_fin = data.get('fecha_fin', '')
            fecha_ini_parsed = str(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
            fecha_fin_parsed = str(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
            object_list = Factura.objects.filter(fecha__range=(fecha_ini_parsed,fecha_fin_parsed)).order_by('id','fecha')                    
#             monto=0
#             for factura in object_list:
#                 lista_detalles=json.loads(factura.detalle)
#                 for key, value in lista_detalles.iteritems():
#                     monto+=int(value['cantidad'])*int(value['precio_unitario'])
#                 factura.monto=monto
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
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

    factura = Factura.objects.get(pk=factura_id)
    lista_detalles=json.loads(factura.detalle)
    #lista_detalles=sorted(lista_detalles.keys())
    #print type(lista_detalles)
    #print sorted(lista_detalles.keys())
    detalles=[]
    for key, value in lista_detalles.iteritems():
        detalle={}
        detalle['item']=key
        detalle['cantidad']=value['cantidad']
        detalle['concepto']=value['concepto']
        detalle['precio_unitario']=value['precio_unitario']
        detalle['iva_10']=value['iva_10']
        detalle['iva_5']=value['iva_5']
#         detalle['exentas']=value['exentas']
        detalles.append(detalle)
    
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
