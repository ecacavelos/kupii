# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Propietario, Fraccion, Lote, Manzana, PagoDeCuotas, Venta, Reserva, CambioDeLotes, RecuperacionDeLotes, TransferenciaDeLotes,Factura, Cliente,Timbrado
from operator import itemgetter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta
from calendar import monthrange
from principal.common_functions import get_nro_cuota
from django.utils import simplejson
from django.db import connection
import xlwt
import math

# Funcion principal del modulo de lotes.
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
        return HttpResponseRedirect("/login") 
