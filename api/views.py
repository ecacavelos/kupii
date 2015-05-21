from calendar import monthrange
import time
from datetime import datetime, timedelta,date
import json
import traceback

from django.contrib import messages
from django.contrib.auth import authenticate
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse, resolve, reverse, resolve
from django.db.models import Count, Min, Sum, Avg, Q
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, \
    HttpResponseForbidden
from django.template import RequestContext, loader
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from principal.common_functions import *
from principal.models import *
from principal.monthdelta import MonthDelta


#Ejemplo nuevo esquema de serializacion:
# all_objects = list(Restaurant.objects.all()) + list(Place.objects.all())
# data = serializers.serialize('xml', all_objects)
#data = serializers.serialize('json', list(objectQuerySet), fields=('fileName','id'))
@require_http_methods(["GET"])
def consulta(request, cedula):  
    error = {}    
    if request.method == 'GET':
                               
            try:
                
                username = request.GET['username']
                password = request.GET['password']
                
                #1. Autenticacion
                user = authenticate(username=username, password=password)
                if user is not None:
                    # the password verified for the user
                    if user.is_active:
                        
                            print("User is valid, active and authenticated")
                            print("cedula de identidad ->" + cedula)
                            #2. Se obtiene cliente
                            cliente = Cliente.objects.get(cedula = cedula)
                            if not cliente: 
                                print 'Cliente no encontrado'
                                error['codigo'] = '31'
                                error['mensaje'] = 'Cliente no encontrado'
                                return HttpResponse(json.dumps(error),status=404, content_type="application/json")                        
                            else:
#                                 cliente_serialized = serializers.serialize('python', cliente)
                                #2. Se obtienen las ventas de dicho cliente
                                ventas_list = Venta.objects.filter(cliente = cliente)                                
                                if not ventas_list:
                                    print 'Cliente no tiene compras actuales'
                                    error['codigo'] = '32'
                                    error['mensaje'] = 'Cliente no tiene compras actuales'
                                    return HttpResponse(json.dumps(error),status=404, content_type="application/json")                                                            
                                else:                                    
                                    items = [] # Aqui se almacena la lista de ventas disponibles para el pago.
                                    respuesta = []
                                    transaccion = Transaccion()
                                    transaccion.estado = 'Consultado'
                                    transaccion.cliente = cliente
                                    transaccion.save()
                                    transaccion_id = {'id_transaccion': transaccion.pk}             
                                    respuesta.append(transaccion_id)
                                    for venta in ventas_list:
                                        #3. Por cada venta se va generando la informacion necesaria para cada venta que requiere pago.
                                        item = {}
                                        lote = Lote.objects.filter(id = venta.lote_id)
                                        lote_serialized = serializers.serialize('python', lote)
                                        
                                        detalle_cuotas = get_cuotas_detail_by_lote(str(lote_serialized[0]['pk']))
                                        cuota_detalle = get_cuota_information_by_lote(str(lote_serialized[0]['pk']),1)
                                        item['codigo_lote'] = lote_serialized[0]['fields']['codigo_paralot']
                                        item['cuotas_pagadas'] = detalle_cuotas['cant_cuotas_pagadas']
                                        item['total_cuotas'] = detalle_cuotas['cantidad_total_cuotas']                                        
                                        item['numero_cuota_a_pagar'] = cuota_detalle[0]['nro_cuota'].split('/')[0]                    
                                        item['fecha_vencimiento'] = detalle_cuotas['proximo_vencimiento']
                                        hoy = date.today()
                                        cuotas_a_pagar_detalle = obtener_cuotas_a_pagar(venta,hoy,detalle_cuotas)
#                                         cuotas_a_pagar_detalle = obtener_cuotas_a_pagar(venta,date(2015,4,12),detalle_cuotas)                                        
                                        item['detalle_cuotas'] = cuotas_a_pagar_detalle 
                                        items.append(item)
                                    respuesta.append(items)
                                    return HttpResponse(json.dumps(respuesta), content_type="application/json")
                    else:
                        error['codigo'] = '22'
                        error['mensaje'] = 'Cuenta deshabilitada'
                        print("The password is valid, but the account has been disabled!")
                        return HttpResponse(json.dumps(error),status=401, content_type="application/json")                        
                else:
                    # the authentication system was unable to verify the username and password
                    print("The username and password were incorrect.")
                    error['codigo'] = '21'
                    error['mensaje'] = 'usuario o password incorrecto'                    
                    return HttpResponse(json.dumps(error), status=401, content_type="application/json")
                    
            except MultiValueDictKeyError:
                print('Error en los parametros del request')
                error['codigo'] = '11'
                error['mensaje'] = 'Sintaxis del request incorrecta'                    
                return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
            except Exception, error:
                print error
                error['codigo'] = '00'
                error['mensaje'] = 'Error en el servidor'                    
                return HttpResponseServerError(json.dumps(error), content_type="application/json")                
            
@require_http_methods(["POST"])
@csrf_exempt
def pago(request):  
    error = {}    
    if request.method == 'POST':                           
            try:                
                username = request.GET['username']
                password = request.GET['password']
                transaccion_id = request.GET['transaccion_id']
                detalle_pago_json = request.body
                if not detalle_pago_json:
                    print('Error en los parametros del request')
                    error['codigo'] = '12'
                    error['mensaje'] = 'Request sin datos en el cuerpo'                    
                    return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
                else:                
                    #1. Autenticacion
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        # the password verified for the user
                        if user.is_active:                        
                            #2. Se obtiene la transaccion
                            transaccion = Transaccion.objects.get(Q(question__contains='Consultado'),Q(id=transaccion_id))
                            if not transaccion: 
                                print 'Transaccion no encontrada'
                                error['codigo'] = '41'
                                error['mensaje'] = 'Transaccion no encontrado'
                                return HttpResponse(json.dumps(error),status=404, content_type="application/json")                        
                            else:
                                detalle_pago = json.loads(detalle_pago_json)
                                items = [] # Aqui se almacena la lista de ventas disponibles para el pago.
                                respuesta = []
                                for pago in detalle_pago:                                    
                                    item = {}
                                    # 1. Obtener la venta a partir del lote y el cliente 
                                    lote = Lote.objects.get(codigo_paralot = pago['codigo_lote'])
                                    venta = Venta.objects.get(Q(cliente=transaccion.cliente),Q(lote=lote))
                                    nuevo_pago = PagoDeCuotas()
                                    nuevo_pago.venta = venta
                                    nuevo_pago.lote = lote
                                    nuevo_pago.fecha_de_pago = date.today().isoformat()
                                    nuevo_pago.nro_cuotas_a_pagar = pago.cuotas_a_pagar
                                    nuevo_pago.cliente = transaccion.cliente
                                    nuevo_pago.plan_de_pago = venta.plan_de_pago
                                    nuevo_pago.plan_de_pago_vendedores= venta.plan_de_pago_vendedor
                                    nuevo_pago.vendedor = venta.vendedor
                                    nuevo_pago.total_de_cuotas = pago.monto_total
                                    nuevo_pago.total_de_mora = pago.monto_mora
                                    nuevo_pago.total_de_pago = pago.monto_total                                    
                                    item['resultado'] = 'exitoso'
                                    item['lote'] = lote.codigo_paralot                                                                    
                                    items.append(item)                                
                                respuesta.append(items)
                                return HttpResponse(json.dumps(respuesta), content_type="application/json")
                        else:
                            error['codigo'] = '22'
                            error['mensaje'] = 'Cuenta deshabilitada'
                            print("The password is valid, but the account has been disabled!")
                            return HttpResponse(json.dumps(error),status=401, content_type="application/json")                        
                    else:
                        # the authentication system was unable to verify the username and password
                        print("The username and password were incorrect.")
                        error['codigo'] = '21'
                        error['mensaje'] = 'usuario o password incorrecto'                    
                        return HttpResponse(json.dumps(error), status=401, content_type="application/json")                    
            except MultiValueDictKeyError:
                print('Error en los parametros del request')
                error['codigo'] = '11'
                error['mensaje'] = 'Sintaxis del request incorrecta'                    
                return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
            except Exception, error2:
                print error2
                error['codigo'] = '00'
                error['mensaje'] = 'Error en el servidor'                    
                return HttpResponseServerError(json.dumps(error), content_type="application/json")                
 
 