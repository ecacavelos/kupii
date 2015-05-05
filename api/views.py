from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse, resolve
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template import RequestContext, loader
from django.core import serializers
from principal.models import *
from django.core.urlresolvers import reverse, resolve
from principal.common_functions import *
from django.core.serializers.json import DjangoJSONEncoder
import json
import traceback
from django.db.models import Count, Min, Sum, Avg
from principal.monthdelta import MonthDelta
from calendar import monthrange
from datetime import datetime, timedelta

#Ejemplo nuevo esquema de serializacion:
# all_objects = list(Restaurant.objects.all()) + list(Place.objects.all())
# data = serializers.serialize('xml', all_objects)
#data = serializers.serialize('json', list(objectQuerySet), fields=('fileName','id'))

@require_http_methods(["GET"])
def consulta(request, cedula):  
    if request.method == 'GET':
            try:            
                username = request.GET['username']
                password = request.GET['password']
                print("cedula de identidad ->" + cedula)
                #1. Se obtiene cliente
                cliente = Cliente.objects.filter(cedula = cedula)
                cliente_serialized = serializers.serialize('python', cliente)
                #2. Se obtienen las ventas de dicho cliente
                ventas_list = Venta.objects.filter(cliente_id = cliente_serialized[0]['pk'])
                items = [] # Aqui se almacena la lista de ventas disponibles para el pago.
                respuesta = []
                transaccion = Transaccion.objects.create(estado='Consultado')
                transaccion.save()
                transaccion_id = {'id_transaccion': transaccion.pk}             
                respuesta.append(transaccion_id)                                       
                for venta in ventas_list:
                    #3. Por cada venta se va generando la informacion necesaria para cada venta que requiere pago.
                    item = {}
                    lote = Lote.objects.filter(id = venta.lote_id)
                    lote_serialized = serializers.serialize('python', lote)
                    item['codigo_lote'] = lote_serialized[0]['fields']['codigo_paralot']
                    detalle_cuotas = get_cuotas_detail_by_lote(str(lote_serialized[0]['pk']))
                    item['cuotas_pagadas'] = detalle_cuotas['cant_cuotas_pagadas']
                    item['total_cuotas'] = detalle_cuotas['cantidad_total_cuotas']
                    cuota_detalle = get_cuota_information_by_lote(str(lote_serialized[0]['pk']),1)
                    item['numero_cuota_a_pagar'] = cuota_detalle[0]['nro_cuota'].split('/')[0]
                    item['monto_cuota'] = venta.precio_de_cuota                    
                    item['fecha_vencimiento'] = detalle_cuotas['proximo_vencimiento']
                    items.append(item)
                respuesta.append(items)
                return HttpResponse(json.dumps(respuesta), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido') 