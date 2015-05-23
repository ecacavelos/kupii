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
import pytz


#Ejemplo nuevo esquema de serializacion:
# all_objects = list(Restaurant.objects.all()) + list(Place.objects.all())
# data = serializers.serialize('xml', all_objects)
#data = serializers.serialize('json', list(objectQuerySet), fields=('fileName','id'))
@require_http_methods(["GET"])
def consulta(request, cedula):  
    codigo_base_error_consulta  = 'c'
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
                                error_msg = 'Cliente no encontrado'     
                                print error_msg
                                error['codigo'] = codigo_base_error_consulta + '31'
                                error['mensaje'] = error_msg
                                return HttpResponse(json.dumps(error),status=404, content_type="application/json")                        
                            else:
#                                 cliente_serialized = serializers.serialize('python', cliente)
                                #2. Se obtienen las ventas de dicho cliente
                                ventas_list = Venta.objects.filter(cliente = cliente)                                
                                if not ventas_list:
                                    error_msg = 'Cliente no tiene compras actuales'
                                    print error_msg
                                    error['codigo'] = codigo_base_error_consulta + '32'
                                    error['mensaje'] = error_msg                                    
                                    return HttpResponse(json.dumps(error),status=404, content_type="application/json")                                                            
                                else:                                    
                                    items = [] # Aqui se almacena la lista de ventas disponibles para el pago.
                                    respuesta = []
                                    transaccion = Transaccion()
                                    transaccion.estado = 'Consultado'
                                    transaccion.cliente = cliente
                                    transaccion.save()
                                    cabecera = {'id_transaccion': transaccion.pk, 'codigo' : '100'}             
                                    respuesta.append(cabecera)
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
                        error_msg = 'Cuenta deshabilitada'     
                        print error_msg
                        error['codigo'] = codigo_base_error_consulta + '22'
                        error['mensaje'] = error_msg
                        return HttpResponse(json.dumps(error),status=401, content_type="application/json")                        
                else:
                    # the authentication system was unable to verify the username and password
                    error_msg = 'Usuario o password incorrecto'
                    print error_msg
                    error['codigo'] = codigo_base_error_consulta + '21'
                    error['mensaje'] = error_msg                                        
                    return HttpResponse(json.dumps(error), status=401, content_type="application/json")                    
            except MultiValueDictKeyError:
                error_msg = 'Sintaxis del request incorrecta'
                print error_msg
                error['codigo'] = codigo_base_error_consulta + '11'
                error['mensaje'] = error_msg                                                        
                return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
            except Exception, error:
                error_msg = 'Error en el servidor'
                print error_msg
                error['codigo'] = codigo_base_error_consulta + '00'
                error['mensaje'] = error_msg                                                        
                return HttpResponseServerError(json.dumps(error), content_type="application/json")                


            
@require_http_methods(["POST"])
@csrf_exempt
def pago(request):  
    error = {}    
    codigo_base_error_pago  = 'p'
    if request.method == 'POST':                           
            try:                
                username = request.GET['username']
                password = request.GET['password']
                transaccion_id = request.GET['transaccion_id']
                print 'Pago para transaccion id: ' + transaccion_id 
                detalle_pago_json = request.body
                print 'JSON recibido: ' + detalle_pago_json
                if not detalle_pago_json:
                    print('Error en los parametros del request')
                    error['codigo'] = codigo_base_error_pago + '12'
                    error['mensaje'] = 'Request sin datos en el cuerpo'                    
                    return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
                else:                
                    #1. Autenticacion
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        # the password verified for the user
                        if user.is_active:                        
                            #2. Se obtiene la transaccion
                            transaccion = Transaccion.objects.get(Q(estado__contains='Consultado'),Q(id=transaccion_id))
#                             transaccion_tmstmp = transaccion.created.replace(tzinfo=None)
                            if not transaccion: 
                                print 'Transaccion no encontrada'
                                error['codigo'] = codigo_base_error_pago + '41'
                                error['mensaje'] = 'Transaccion no encontrado'
                                return HttpResponse(json.dumps(error),status=404, content_type="application/json")                        
                            else:
                                if transaccion.estado != 'Consultado':
                                    error_msg = 'Transaccion con estado invalido' 
                                    print error_msg
                                    error['codigo'] = codigo_base_error_pago + '47'
                                    error['mensaje'] = error_msg
                                    return HttpResponse(json.dumps(error),status=404, content_type="application/json")
                                else: # Estado valido                                                                        
                                    if (datetime.now(pytz.utc) - transaccion.created).seconds/60 > 30: #TIMEOUT
                                            error_msg = 'Timeout'
                                            print error_msg
                                            error['codigo'] = codigo_base_error_pago + '45'
                                            error['mensaje'] = error_msg
                                            if transaccion.estado != 'Pagado':
                                                transaccion.estado = 'Expirado'
                                                transaccion.save()                                                                                   
                                            return HttpResponse(json.dumps(error),status=404, content_type="application/json")                                       
                                    else:
                                        detalle_pago = json.loads(detalle_pago_json)                                        
                                        lote = Lote.objects.get(codigo_paralot = detalle_pago['codigo_lote'])
                                        venta = Venta.objects.get(Q(lote=lote),Q(cliente=transaccion.cliente))                                
                                        detalle_cuotas = get_cuotas_detail_by_lote(str(lote.id))
                                        hoy = date.today()
                                        cuotas_a_pagar_detalle = obtener_cuotas_a_pagar(venta,hoy,detalle_cuotas)                                
                                        if not cuotas_a_pagar_detalle:
                                            print 'Cuota a pagar no encontrada'
                                            error['codigo'] = codigo_base_error_pago + '42'
                                            error['mensaje'] = 'Cuota a pagar no encontrada'
                                            return HttpResponse(json.dumps(error),status=404, content_type="application/json")
                                        else:    
                                            if str(cuotas_a_pagar_detalle[0]['numero_cuota']) != detalle_pago['cuota_a_pagar']:
                                                error_msg = 'Numero de cuota a pagar incorrecta, se espera: ' + str(cuotas_a_pagar_detalle[0]['numero_cuota']) 
                                                print error_msg
                                                error['codigo'] = codigo_base_error_pago + '43'
                                                error['mensaje'] = error_msg
                                                return HttpResponse(json.dumps(error),status=404, content_type="application/json")
                                            elif float(detalle_pago['monto_total']) != cuotas_a_pagar_detalle[0]['monto_cuota']:
                                                error_msg = 'Monto de la cuota incorrecto, se espera: ' + str(cuotas_a_pagar_detalle[0]['monto_cuota'])
                                                print error_msg
                                                error['codigo'] = codigo_base_error_pago + '44'
                                                error['mensaje'] = error_msg
                                                return HttpResponse(json.dumps(error),status=404, content_type="application/json")   
                                            else: # Parametros totalmente correctos, emitir el pago
                                                nuevo_pago = PagoDeCuotas()
                                                nuevo_pago.venta = venta
                                                nuevo_pago.lote = lote
                                                nuevo_pago.transaccion = transaccion
                                                nuevo_pago.fecha_de_pago = hoy
                                                nuevo_pago.nro_cuotas_a_pagar = 1
                                                nuevo_pago.cliente = transaccion.cliente
                                                nuevo_pago.plan_de_pago = venta.plan_de_pago
                                                nuevo_pago.plan_de_pago_vendedores= venta.plan_de_pago_vendedor
                                                nuevo_pago.vendedor = venta.vendedor
                                                nuevo_pago.total_de_cuotas = venta.precio_de_cuota
                                                nuevo_pago.total_de_pago = cuotas_a_pagar_detalle[0]['monto_cuota']
                                                nuevo_pago.total_de_mora = cuotas_a_pagar_detalle[0]['monto_cuota'] - venta.precio_de_cuota
                                                nuevo_pago.save() 
                                                transaccion.estado = 'Pagado'
                                                transaccion.save()      
                                                respuesta = {}
                                                respuesta['mensaje'] = 'Operacion Exitosa'
                                                respuesta['codigo'] = '200'                                 
                                                return HttpResponse(json.dumps(respuesta), content_type="application/json")
                        else:
                            error['codigo'] = codigo_base_error_pago + '22'
                            error['mensaje'] = 'Cuenta deshabilitada'
                            print("The password is valid, but the account has been disabled!")
                            return HttpResponse(json.dumps(error),status=401, content_type="application/json")                        
                    else:
                        # the authentication system was unable to verify the username and password
                        print("The username and password were incorrect.")
                        error['codigo'] = codigo_base_error_pago + '21'
                        error['mensaje'] = 'usuario o password incorrecto'                    
                        return HttpResponse(json.dumps(error), status=401, content_type="application/json")                    
            except MultiValueDictKeyError:
                print('Error en los parametros del request')
                error['codigo'] = codigo_base_error_pago + '11'
                error['mensaje'] = 'Sintaxis del request incorrecta'                    
                return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
            except Exception, error2:
                print error2
                if error2.message == 'Transaccion matching query does not exist.':
                    error_msg = 'Transaccion no encontrada'
                    print error_msg
                    error['codigo'] = codigo_base_error_pago + '46'
                    error['mensaje'] = error_msg
                    return HttpResponse(json.dumps(error),status=404, content_type="application/json")
                elif error2.message == 'Venta matching query does not exist.':
                    error_msg = 'No se encontro la venta'
                    print error_msg
                    error['codigo'] = codigo_base_error_pago + '48'
                    error['mensaje'] = error_msg
                    return HttpResponse(json.dumps(error),status=404, content_type="application/json")
                error['codigo'] = codigo_base_error_pago + '00'
                error['mensaje'] = 'Error en el servidor'                    
                return HttpResponseServerError(json.dumps(error), content_type="application/json")                
 
 