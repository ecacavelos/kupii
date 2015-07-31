from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse, resolve
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template import RequestContext, loader
from django.core import serializers
from principal.models import Fraccion, Manzana, Venta, PagoDeCuotas, Propietario, Lote, Cliente, Vendedor, PlanDePago, PlanDePagoVendedor,Timbrado, RecuperacionDeLotes
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
def get_propietario_id_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_propietario = request.GET['term']
                print("term ->" + name_propietario)
                object_list = Propietario.objects.filter(nombres__icontains = name_propietario)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 

@require_http_methods(["GET"])
def get_vendedor_name_id_by_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                cedula_vendedor = request.GET['term']
                print("term ->" + cedula_vendedor);
                object_list = Vendedor.objects.filter(cedula__icontains= cedula_vendedor)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
        
@require_http_methods(["GET"])
def get_propietario_name_id_by_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                cedula_propietario = request.GET['term']
                print("term ->" + cedula_propietario);
                object_list = Propietario.objects.filter(cedula__icontains= cedula_propietario)
                data=serializers.serialize('json',list(object_list))
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 


@require_http_methods(["GET"])
def get_cliente_name_id_by_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                cedula_cliente = request.GET['term']
                print("term ->" + cedula_cliente);
                object_list = Cliente.objects.filter(cedula__icontains= cedula_cliente)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 

def get_cliente_id_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_cliente = request.GET['term']
                print("term ->" + name_cliente);
                print Cliente.objects.filter(nombres__icontains= name_cliente).query
                object_list = Cliente.objects.filter(nombres__icontains= name_cliente)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 

def get_vendedor_id_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_vendedor = request.GET['term']
                print("term ->" + name_vendedor);
                object_list = Vendedor.objects.filter(nombres__icontains= name_vendedor)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
 
@require_http_methods(["GET"])
def get_lotes_a_cargar_by_manzana(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                id_manzana = request.GET['id_manzana']
                id_fraccion = request.GET['id_fraccion']
                print("id_manzana ->" + id_manzana);
                print("id_fraccion ->" + id_fraccion);
                object_list = Manzana.objects.filter(pk= id_manzana, fraccion=id_fraccion)
                id_manzana = object_list[0].id
                total_lotes = object_list[0].cantidad_lotes
                object_list2= Lote.objects.filter(manzana_id = id_manzana)
                cantidad_encontrada = len(object_list2)
                print("cantidad_encontrada ->" + unicode(cantidad_encontrada));
                diferencia = total_lotes - cantidad_encontrada
                results =[]
                if (diferencia == 0):
                    results = [{"id": 0, "label": "No quedan Lotes disponibles en esta manzana"}]
                else:
                    if (cantidad_encontrada == 0):
                        for i in range(1, total_lotes+1):
                            record = {"id": i, "label": i}
                            results.append(record)
                    else:
                        encontrados = []
                        for i in range(1, total_lotes+2):
                            encontrados.append(0)
                            
                        for j in range(1, cantidad_encontrada +1):
                            nro_lote_encontrado = object_list2[j-1].nro_lote
                            for i in range(1,total_lotes+1): 
                                if (i == object_list2[j-1].nro_lote):
                                    encontrados[nro_lote_encontrado]= nro_lote_encontrado                        
                            
                        for i in range(1, total_lotes+1):
                            if (i != encontrados[i]):
                                record = {"id": i, "label": i}
                                results.append(record)                 
                
                return HttpResponse(json.dumps(results), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
 

@require_http_methods(["GET"])
def get_propietario_name_by_id(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                id_propietario = request.GET['propietario_id']
                print("id ->" + id_propietario);
                object_list = Propietario.objects.filter(id= id_propietario)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 


@require_http_methods(["GET"])
def get_propietario_lastId(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                #callback = request.GET['callback']
                #plan_id = request.GET['id_plan_pago']
                #print("id_plan_pago ->" + plan_id);
                id = Propietario.objects.latest('id').id                
                results = [{"id": id}]
                return HttpResponse(json.dumps(results), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))    
    



@require_http_methods(["GET"])
def get_fracciones_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:   
                nombre_fraccion = request.GET['term']
                print("term ->" + nombre_fraccion);
                object_list = Fraccion.objects.filter(nombre__icontains=nombre_fraccion)
                labels=["nombre"]         
                json_object_list = custom_json(object_list,labels)       
                return HttpResponse(json.dumps(json_object_list, cls=DjangoJSONEncoder),content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))
  
@require_http_methods(["GET"])
def get_fracciones_by_id(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:    
                id_fraccion = request.GET['term']
                print("term ->" + id_fraccion);
                object_list = Fraccion.objects.filter(id__icontains=id_fraccion).order_by('id')
                labels=["nombre"]         
                json_object_list = custom_json(object_list,labels)       
                return HttpResponse(json.dumps(json_object_list, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                print traceback.format_exc()
        else:
            return HttpResponseRedirect(reverse('login')) 

@require_http_methods(["GET"])
def get_manzanas_by_fraccion(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                fraccion_id = request.GET['fraccion_id']
                print("fraccion_id ->" + fraccion_id);
                object_list = Manzana.objects.filter(fraccion_id=fraccion_id)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))

@require_http_methods(["GET"])
def get_ventas_by_lote(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                lote_id = request.GET['lote_id']
                print("lote_id ->" + lote_id)
                #venta = Venta.objects.filter(lote=lote_id).order_by('-id')[:1]
                venta = [get_ultima_venta(lote_id)]
                print venta
                object_list = [ob.as_json() for ob in venta]
                cuotas_details = get_cuotas_detail_by_lote(lote_id)
                response = {
                    'venta': object_list,
                    'cuotas_details': cuotas_details,
                }
                return HttpResponse(json.dumps(response), content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login')) 

@require_http_methods(["GET"])
def get_ventas_by_cliente(request):
    try:
        cliente_id = request.GET['cliente']
        print("cliente_id ->" + cliente_id);
        object_list = Venta.objects.filter(cliente=cliente_id)
        data=serializers.serialize('json',list(object_list)) 
        return HttpResponse(data,content_type="application/json")
    except Exception, error:
        print error

@require_http_methods(["GET"])
def get_pagos_by_venta(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                venta_id = request.GET['venta_id']
                print("venta_id ->" + venta_id);
                object_list = PagoDeCuotas.objects.filter(venta=venta_id)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login')) 

@require_http_methods(["GET"])
def get_plan_pago(request):
    if request.method == 'GET':
        if request.method == 'GET':
            if request.user.is_authenticated():
                try:              
                    nombre_plan = request.GET['term']
                    print("term ->" + nombre_plan);
                    object_list = PlanDePago.objects.filter(nombre_del_plan__icontains= nombre_plan)
                    labels=["nombre_del_plan"]
                    return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")     
                except Exception, error:
                    print error
                    #return HttpResponseServerError('No se pudo procesar el pedido')
            else:
                return HttpResponseRedirect(reverse('login'))

@require_http_methods(["GET"])
def get_plan_pago_vendedor(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:                                
                nombre_plan = request.GET['term']
                print("term ->" + nombre_plan);
                object_list = PlanDePagoVendedor.objects.filter(nombre__icontains= nombre_plan)
                labels=["nombre"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))

def get_timbrado_by_numero(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                numero_timbrado = unicode(request.GET['term'])
                print("term ->" + numero_timbrado);
                object_list = Timbrado.objects.filter(numero__icontains= numero_timbrado)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))

def get_cliente_id_by_name_or_ruc(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_cliente = request.GET['term']
                print("term ->" + name_cliente);
                object_list = Cliente.objects.filter(nombres__icontains= name_cliente)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
        
def get_vendedor_id_by_name_or_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_vendedor = request.GET['term']
                print("term ->" + name_vendedor);
                object_list = Vendedor.objects.filter(nombres__icontains= name_vendedor)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
        
def get_propietario_id_by_name_or_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_cliente = request.GET['term']
                print("term ->" + name_cliente);
                object_list = Cliente.objects.filter(nombres__icontains= name_cliente)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
                
@require_http_methods(["GET"])
def get_mes_pagado_by_id_lote(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:                
                lote_id = request.GET['lote_id']
                cuotas_pag = request.GET['cant_cuotas']
                cuotas_detalles = get_cuota_information_by_lote(lote_id,cuotas_pag)
                data = json.dumps({
                    'cuotas_a_pagar': cuotas_detalles})
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))
        
def get_pago_cuotas_by_lote_cliente(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:  
                codigo= request.GET.get('lote_id')
                cedula_cli= request.GET.get('cliente_id')
                nombre= request.GET.get('nombre')
                lote =  Lote.objects.get(codigo_paralot= codigo)
                cliente = Cliente.objects.get(cedula=cedula_cli)
                venta = Venta.objects.get(lote_id= lote.id, cliente_id=cliente.id)
                object_list=get_pago_cuotas(venta, None, None)
                labels=["nro_cuota_y_total","nro_cuota"]
                return HttpResponse(json.dumps(object_list, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))
        
def get_detalles_factura(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                codigo= request.GET.get('lote_id')
                cedula_cli= request.GET.get('cliente_id')
                nro_cuota_desde = request.GET.get('nro_cuota_desde').split("/")
                nro_cuota_hasta = request.GET.get('nro_cuota_hasta').split("/")
                num_desde = int(nro_cuota_desde[0])
                num_hasta = int(nro_cuota_hasta[0])
                lote =  Lote.objects.get(codigo_paralot= codigo)
                cliente = Cliente.objects.get(cedula=cedula_cli)
                venta = Venta.objects.get(lote_id= lote.id, cliente_id=cliente.id)
                object_list=get_pago_cuotas(venta, None, None)
                detalles=[]
                detalle={}
                cantidad = num_hasta - (num_desde -1)
                detalle['cantidad'] = cantidad
                detalle['precio_unitario']= venta.precio_de_cuota
                detalle['exentas'] = int(round((cantidad * venta.precio_de_cuota) * 0.7))
                detalle['iva5']= int(round((cantidad * venta.precio_de_cuota) * 0.3))
                detalles.append(detalle)
                return HttpResponse(json.dumps(detalles, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponse(json.dumps(object_list, cls=DjangoJSONEncoder), content_type="application/json")
